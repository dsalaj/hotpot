"""hotpot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from hotpot import views, settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.get_cart, name='get_cart'),
    url(r'^add/(?P<product_id>[0-9]+)/(?P<quantity>[0-9]+)/$', views.add_to_cart, name='add_to_cart'),
    url(r'^pdf/', views.other_view, name='other_view'),
    url(r'^email/', views.pdf_html, name='email'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
