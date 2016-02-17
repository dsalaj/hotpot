# views.py
from cart.cart import Cart
from django.shortcuts import render
from hotpot.models import *
from django.http import HttpResponse
import easy_pdf
from easy_pdf.views import PDFTemplateView
from django.core.mail import send_mail


def other_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pdfkit_out.pdf"'
    context = {}
    context['menu'] = MenuItem.objects.all()
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


def get_cart(request):
    context = dict(cart=Cart(request))
    context['menu'] = MenuItem.objects.all()
    return render(request, 'hotpot/cart.html', context)


def pdf_html(request):
    send_mail('Subject here', 'Here is the message.', 'hotpot.graz@gmail.com', ['salaj.au@gmail.com'], fail_silently=False)
    return render(request, 'hotpot/clean.html')