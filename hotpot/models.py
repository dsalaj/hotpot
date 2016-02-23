from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
import datetime

class MenuItemRetailerPrice(models.Model):
    menuitem = models.ForeignKey('MenuItem')
    retailer = models.ForeignKey('Retailer')
    price = models.DecimalField(decimal_places=2, max_digits=6)


class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2047)
    category = models.ForeignKey('Category')
    unit_price = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name

    def retailer_price(self, retailer):
        try:
            r = Retailer.objects.get(password=retailer)
            try:
                r_price = self.menuitemretailerprice_set.get(retailer=r)
                return r_price.price
            except:
                return "undefined"
        except:
            return self.unit_price


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Menu(models.Model):
    items = models.ManyToManyField('MenuItem')
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()

    def __str__(self):
        return 'FROM ' + str(self.time_from.date()) + ' TO ' + str(self.time_to.date())

    @staticmethod
    def get_current_menu_items():
        now = datetime.datetime.now()
        try:
            menu = Menu.objects.get(time_from__lte=now, time_to__gte=now)
        except ObjectDoesNotExist:
            return None
        return menu.items.all()

    def clean(self):
        time_from = self.time_from
        time_to = self.time_to
        menus = Menu.objects.all()
        for m in menus:
            if m.time_from < time_from < m.time_to or \
               m.time_from < time_to < m.time_to or \
               time_from < m.time_from and m.time_to < time_to or \
               time_to < m.time_from and m.time_to < time_from:
                raise ValidationError("Please enter a value that does not overlap with already "
                                      "existing menu ("+str(m)+") time range")


class OrderItem(models.Model):
    order = models.ForeignKey('Order')
    item = models.ForeignKey('MenuItem')
    retailer = models.ForeignKey('Retailer', null=True)
    amount = models.IntegerField()


class Coupon(models.Model):
    PERCENTAGE = 1
    CURRENCY = 2
    TYPE = (
        (PERCENTAGE, 'percentage'),
        (CURRENCY, 'value')
    )
    coupon_type = models.IntegerField(choices=TYPE)
    value = models.FloatField()
    order = models.ForeignKey('Order')


class Order(models.Model):
    order_number = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateField()
    title = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    note = models.TextField(max_length=2047)

    def __str__(self):
        return str(self.timestamp) + ' ' + str(self.email)


class Retailer(models.Model):
    password = models.CharField(max_length=40)

    def __str__(self):
        return self.password


class UserMiddleware(object):
    @staticmethod
    def process_request(request):
        if not hasattr(request, 'session'):
            raise ImproperlyConfigured("django.contrib.sessions.middleware.SessionMiddleware"
                                       " must be before UserMiddleware in MIDDLEWARE_CLASSES")
        if not 'user' in request.session.keys():
            request.session['user'] = ""
