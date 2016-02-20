# views.py
from cart.cart import Cart
from django.shortcuts import render
from hotpot.models import *
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
    cart.add(product, product.unit_price, quantity)
    print("added thing to cart")


def remove_from_cart(request, product_id):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(product)
    print("removed thing to cart")


def change_in_cart(request, product_id, quantity):
    product = MenuItem.objects.get(id=product_id)
    cart = Cart(request)
    cart.update(product, quantity, product.unit_price)
    print("changed thing in cart")


def home(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    return render(request, 'hotpot/home.html', context)


def buy(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    return render(request, 'hotpot/cart.html', context)


def checkout(request):
    context = dict(cart=Cart(request))
    context['menu'] = Menu.get_current_menu_items()
    return render(request, 'hotpot/checkout.html', context)


def finish(request):
    context = dict(cart=Cart(request))
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
    request.session.flush()
    return render(request, 'hotpot/clean.html', {'msg': 'pdf created, email sent!'})
