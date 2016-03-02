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
from decimal import Decimal
import os


def add_to_cart(request, product_id, quantity):
    if int(quantity) > 0:
        product = MenuItem.objects.get(id=product_id)
        cart = Cart(request)
        batch_item = Menu.get_current_menu().itembatch_set.get(item=product)
        if batch_item.amount >= int(quantity) + int(cart.get_qty(product)):
            cart.add(product, product.retailer_price(request.session['user']), quantity)
            request.session['quantity_error'] = None
            request.session['quantity_error_item'] = None
            return JsonResponse({"return": "ok"})
        else:
            request.session['quantity_error'] = batch_item.amount
            request.session['quantity_error_item'] = product.name
            return JsonResponse({"return": "fail"})


def remove_from_cart(request, product_id):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(product)
    print("removed thing to cart")


def change_in_cart(request, product_id, quantity):
    if int(quantity) > 0:
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
    else:
        remove_from_cart(request, product_id)

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
            order = order_form.save()
            for item in context['cart']:
                OrderItem.objects.create(order=order,
                                         item=item.product,
                                         amount=item.quantity,
                                         total_price=item.total_price)
                item_batch = batch.get(item=item.product)
                print "Item " + str(item_batch.item.name) + " amount = " + str(item_batch.amount) + " - " + str(item.quantity)
                item_batch.amount = item_batch.amount - item.quantity
                print "Item " + str(item_batch.item.name) + " amount = " + str(item_batch.amount)
                item_batch.full_clean() #FIXME
                item_batch.save()
            order.total_price = sum([i.total_price for i in OrderItem.objects.filter(order=order)])
            if request.session['shipping_cost'] is not None:
                shipping = float(request.session['shipping_cost'])
                order.total_price += Decimal(shipping)
            else:
                shipping = 0
            order.save()
            #finish(generate_invoice_pdf({'order': order}))
            return pdf_preview(generate_invoice_pdf(order, shipping))
            request.session.flush()
            return render_with_middleware(request, 'hotpot/clean.html', {'msg': 'Thank you for the Order'})
    else:
        order_form = OrderForm()
    context['order_form'] = order_form
    context['menu'] = Menu.get_current_menu_items()
    return render_with_middleware(request, 'hotpot/checkout.html', context)


def finish(pdf):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pdfkit_out.pdf"'
    response.write(pdf)
    print "pdf invoice rendered"
    email = EmailMessage('Hello', 'Here is the message with pdf.', 'hotpot.graz@gmail.com',
                         ['salaj.au@gmail.com', 'frost_master@hotmail.com'])
    email.attach('hotpot_invoice.pdf', response.getvalue(), 'application/pdf')
    print "pdf attached to email"
    email.send(fail_silently=False)
    print "email sent"


def generate_invoice_pdf(order, shipping):
    context = {}
    context['date'] = datetime.date.today().strftime('%d.%m.%Y')
    context['delivery_date'] = order.delivery_date.strftime('%d.%m.%Y')
    context['invoice_number'] = order.serial_number
    context['order_items'] = order.orderitem_set.all()
    context['total_order_items'] = sum(o.amount for o in context['order_items'])
    context['order'] = order
    context['cwd'] = os.getcwd()
    if shipping == 0:
        context['mwst10'] = Decimal(order.total_price * 0.1).quantize(Decimal('0.01'))
        context['mwst20'] = Decimal(0).quantize(Decimal('0.01'))
    else:
        context['mwst10'] = Decimal((float(order.total_price) - shipping) * 0.1).quantize(Decimal('0.01'))
        context['mwst20'] = Decimal(shipping * 0.2).quantize(Decimal('0.01'))
        context['shipping'] = Decimal(shipping).quantize(Decimal('0.01'))
    return easy_pdf.rendering.render_to_pdf("pdf/pdfkit_test.html", context, encoding=u'utf-8')


def pdf_preview(pdf):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pdfkit_out.pdf"'
    response.write(pdf)
    return HttpResponse(response.getvalue(), content_type='application/pdf')

