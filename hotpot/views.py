# views.py
from cart.cart import Cart
from django.shortcuts import render
from hotpot.models import *
from hotpot.forms import *
from django.http import HttpResponse
import easy_pdf
from easy_pdf.views import PDFTemplateView # needed for easy_pdf.rendering !
from django.core.mail import send_mail, EmailMessage


def pdf_preview(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pdfkit_out.pdf"'
    context = dict(cart=Cart(request))
    pdfres = easy_pdf.rendering.render_to_pdf("pdf/pdfkit_test.html", context, encoding=u'utf-8')
    response.write(pdfres)
    return HttpResponse(response.getvalue(), content_type='application/pdf')


def add_to_cart(request, product_id, quantity):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.add(product, product.retailer_price(request.session['user']), quantity)
    print("added thing to cart")


def remove_from_cart(request, product_id):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(product)
    print("removed thing to cart")


def change_in_cart(request, product_id, quantity):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.update(product, quantity, product.retailer_price(request.session['user']))
    print("changed thing in cart")


def home(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    if request.method == 'POST':
            if 'logout' in request.POST and request.POST['logout'] == "1":
                request.session['logged'] = False
                request.session['user'] = ""
                context['login_form'] = RetailerLogin()
                return render(request, 'hotpot/home.html', context)

            login_form = RetailerLogin(request.POST)
            if login_form.is_valid():
                print "Login form valid"
                request.session['logged'] = True
                request.session['user'] = Retailer.objects.get(password=login_form.data['password']).__str__()
    else:
        login_form = RetailerLogin()
    context['login_form'] = login_form
    return render(request, 'hotpot/home.html', context)


def buy(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    return render(request, 'hotpot/buy.html', context)


def checkout(request):
    context = dict(cart=Cart(request))
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            f = order_form.save(commit=False)
            f.save()
            finish({'order': f, 'cart': context['cart']})
            for item in context['cart']:
                OrderItem.objects.create(order=f, item=item.product, amount=item.quantity)
            request.session.flush()
            return render(request, 'hotpot/clean.html', {'msg': 'Thank you for the Order'})
    else:
        order_form = OrderForm()
    context['order_form'] = order_form
    context['menu'] = Menu.get_current_menu_items()
    return render(request, 'hotpot/checkout.html', context)


def finish(context):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pdfkit_out.pdf"'
    pdfres = easy_pdf.rendering.render_to_pdf("pdf/pdfkit_test.html", context, encoding=u'utf-8')
    print "pdf invoice rendered"
    response.write(pdfres)
    email = EmailMessage('Hello', 'Here is the message with pdf.', 'hotpot.graz@gmail.com',
                         ['salaj.au@gmail.com', 'frost_master@hotmail.com'])
    email.attach('invoicex.pdf', response.getvalue(), 'application/pdf')
    print "pdf attached to email"
    email.send(fail_silently=False)
    print "email sent"
