# views.py
from django.shortcuts import render
from hotpot.models import *
from hotpot.forms import *
from django.http import HttpResponse, JsonResponse
import easy_pdf
from easy_pdf.views import PDFTemplateView # needed for easy_pdf.rendering !
from django.core.mail import send_mail, EmailMessage
from django.views.decorators.cache import never_cache
from cart.cart import Cart

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
    batch_item = Menu.get_current_menu().itembatch_set.get(item=product)
    print str(batch_item.amount) + " " + str(quantity)
    if batch_item.amount >= int(quantity) + int(cart.get_qty(product)):
        cart.add(product, product.retailer_price(request.session['user']), quantity)
        print("added thing to cart")
        request.session['quantity_error'] = None
        request.session['quantity_error_item'] = None
        return JsonResponse({"return": "ok"})
    else:
        request.session['quantity_error'] = batch_item.amount
        request.session['quantity_error_item'] = product.name
        print("add to cart q FAILED " + str(request.session['quantity_error']))
        return JsonResponse({"return": "fail"})


def remove_from_cart(request, product_id):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(product)
    print("removed thing to cart")


def change_in_cart(request, product_id, quantity):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    batch_item = Menu.get_current_menu().itembatch_set.get(item=product)
    if batch_item.amount >= int(quantity):
        cart.update(product, quantity, product.retailer_price(request.session['user']))
        print("changed thing in cart")
        request.session['quantity_error'] = None
        request.session['quantity_error_item'] = None
    else:
        request.session['quantity_error'] = batch_item.amount
        request.session['quantity_error_item'] = product
        print("change in cart q FAILED")

def render_with_middleware(request, html, context):
    #newsletter_view_helper(request, context)
    #retailer_login_helper(request, context)
    return render(request, html, context)



@never_cache
def home(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    return render_with_middleware(request, 'hotpot/home.html', context)


@never_cache
def buy(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    return render_with_middleware(request, 'hotpot/buy.html', context)


@never_cache
def checkout(request):
    context = dict(cart=Cart(request))
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            batch = Menu.get_current_menu().itembatch_set
            f = order_form.save(commit=False)
            f.save()
            finish({'order': f, 'cart': context['cart']})
            for item in context['cart']:
                OrderItem.objects.create(order=f, item=item.product, amount=item.quantity)
                item_batch = batch.get(item=item.product)
                item_batch.amount -= item.quantity
                item_batch.full_clean() #FIXME
                item_batch.save()
            request.session.flush()
            return render_with_middleware(request, 'hotpot/clean.html', {'msg': 'Thank you for the Order'})
    else:
        order_form = OrderForm()
    context['order_form'] = order_form
    context['menu'] = Menu.get_current_menu_items()
    return render_with_middleware(request, 'hotpot/checkout.html', context)


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
