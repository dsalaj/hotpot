from hotpot.forms import RetailerLogin
from hotpot.models import Retailer, Shipping
from cart.cart import Cart
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured


def retailer_login_helper(request):
    context = {}
    if request.method == 'POST':
            if 'logout' in request.POST and request.POST['logout'] == "1":
                request.session.flush()
                request.session['logged'] = False
                request.session['user'] = ""
                context['login_form'] = RetailerLogin()
                login_form = RetailerLogin()
            else:
                login_form = RetailerLogin(request.POST)
                if login_form.is_valid():
                    request.session.flush()
                    request.session['logged'] = True
                    request.session['user'] = Retailer.objects.get(password=login_form.data['password']).__str__()
    else:
        login_form = RetailerLogin()
    context['login_form'] = login_form
    return context


def shipping_helper(request):
    if not hasattr(request, 'session'):
        raise ImproperlyConfigured("django.contrib.sessions.middleware.SessionMiddleware"
                                   " must be before UserMiddleware in MIDDLEWARE_CLASSES")
    if 'user' not in request.session.keys():
        request.session['user'] = ""
    try:
        if float(Cart(request).summary()) < Shipping.objects.get().treshold:
            request.session['shipping_cost'] = str(Shipping.objects.get().price)
        else:
            request.session['shipping_cost'] = None
    except ObjectDoesNotExist:
        pass
    return {}
