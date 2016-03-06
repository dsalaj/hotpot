# views.py
from __future__ import unicode_literals
from django.shortcuts import render
from hotpot import settings
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
from django.core import mail
from django.template.loader import render_to_string
from smtplib import SMTPException
import logging
logger = logging.getLogger('hotpot.' + __name__)
# -*- coding: utf-8 -*-


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


def change_in_cart(request, product_id, quantity):
    if int(quantity) > 0:
        product = MenuItem.objects.get(id=product_id)
        cart = Cart(request)
        batch_item = Menu.get_current_menu().itembatch_set.get(item=product)
        if batch_item.amount >= int(quantity):
            cart.update(product, quantity, product.retailer_price(request.session['user']))
            request.session['quantity_error'] = None
            request.session['quantity_error_item'] = None
            return JsonResponse({"return": "ok"})
        else:
            request.session['quantity_error'] = batch_item.amount
            request.session['quantity_error_item'] = product
            return JsonResponse({"return": "fail"})
    else:
        remove_from_cart(request, product_id)


@never_cache
def report(request):
    context = {}
    if not request.user.is_superuser:
        return render(request, 'hotpot/clean.html', {'msg': 'Admin log in required'})

    if request.method == 'POST':
        form = ReportForm(request.POST)
        context['form'] = form
        if form.is_valid():
            delivery_days = form.get_delivery_days()
            selected_orders = Order.objects.filter(delivery_date__in=delivery_days)
            context['sum_total'] = sum([o.total_price for o in selected_orders])
            unique_menuitems = set()
            menuitems_summary = {}
            for o in selected_orders:
                unique_menuitems = unique_menuitems.union([i.item for i in o.items])
                for i in o.items:
                    if menuitems_summary.has_key(i.item):
                        menuitems_summary[i.item] += i.amount
                    else:
                        menuitems_summary[i.item] = i.amount
            #context['sum_unique'] = list(unique_menuitems)
            context['sum_mitems'] = menuitems_summary
            if request.POST['button'] == 'Show':
                context['orders'] = selected_orders
                return render(request, 'hotpot/report.html', context)
            elif request.POST['button'] == 'Export':
                return render(request, 'hotpot/clean.html', {'msg': 'TODO: implement csv export'})
            else:
                return render(request, 'hotpot/clean.html', {'msg': 'Unknown submit value'})
    else:
        form = ReportForm()
        context['form'] = form
    return render(request, 'hotpot/report.html', context)


@never_cache
def home(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    context['categories'] = Category.objects.all()
    return render(request, 'hotpot/home.html', context)


@never_cache
def buy(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    context['categories'] = Category.objects.all()
    return render(request, 'hotpot/buy.html', context)


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
                item_batch.amount = item_batch.amount - item.quantity
                item_batch.full_clean() #FIXME
                item_batch.save()
            order.total_price = sum([i.total_price for i in OrderItem.objects.filter(order=order)])
            if request.session['shipping_cost'] is not None:
                shipping = float(request.session['shipping_cost'])
                order.total_price += Decimal(shipping)
            else:
                shipping = 0
            order.save()
            # return pdf_preview(generate_invoice_pdf(order, shipping))
            finish(generate_invoice_pdf(order, shipping), order, shipping)
            request.session.flush()

            context = dict(cart=Cart(request))
            context['menu'] = Menu.get_current_menu_items()
            context['categories'] = Category.objects.all()
            context['order_complete'] = True
            return render(request, 'hotpot/home.html', context)
    else:
        order_form = OrderForm()
    context['order_form'] = order_form
    context['menu'] = Menu.get_current_menu_items()
    return render(request, 'hotpot/checkout.html', context)


def finish(pdf, order, shipping):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pdfkit_out.pdf"'
    response.write(pdf)
    print "pdf invoice rendered"
    # email = EmailMessage('Ihre HOTPOT Bestellung', 'Ihre HOTPOT Bestellung', settings.DEFAULT_FROM_EMAIL,
    #                      ['salaj.au@gmail.com', 'frost_master@hotmail.com'])
    # email.attach('hotpot_rechnung.pdf', response.getvalue(), 'application/pdf')
    # print "pdf attached to email"
    # email.send(fail_silently=False)
    # print "email sent"

    try:
        connection = mail.get_connection()
    except SMTPException as e:
        logger.error("Failed to open connection to mail server",
                     exc_info=True, extra={'request': None, 'error':e})
        return

    sender_address = settings.DEFAULT_FROM_EMAIL
    mail_list = []

    # hotpot new invoice email
    hotpot_context = {'order': order, 'order_items': order.orderitem_set.all()}
    if shipping != 0:
        hotpot_context['shipping'] = Decimal(shipping).quantize(Decimal('0.01'))
    hotpot_text_message = render_to_string('email/hotpot_new_order.txt', hotpot_context)
    hotpot_mail = mail.EmailMessage('[HOTPOT] Neue Bestellung ist eingegangen',
                                    hotpot_text_message,
                                    sender_address,
                                    [settings.DEFAULT_FROM_EMAIL])
    hotpot_mail.attach('hotpot_rechnung.pdf', response.getvalue(), 'application/pdf')
    mail_list.append(hotpot_mail)

    # subscriber new newsletter subscription email
    buyer_context = hotpot_context
    buyer_text_message = render_to_string('email/buyer_new_order.txt', buyer_context)
    buyer_mail = mail.EmailMessage('Ihre HOTPOT Bestellung',
                                   buyer_text_message,
                                   sender_address,
                                   [order.email])
    buyer_mail.attach('hotpot_rechnung.pdf', response.getvalue(), 'application/pdf')
    mail_list.append(buyer_mail)

    for message in mail_list:
        try:
            message.connection = connection
            message.send()
            print "invoice email sent"
        except SMTPException as e:
            logger.error("Sending mail to %s failed" % (str(message.to)),
                         exc_info=True, extra={'request': None, 'mailmessage': message, 'error': e})
    connection.close()


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
        context['mwst10'] = Decimal(order.total_price * Decimal(0.1)).quantize(Decimal('0.01'))
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

