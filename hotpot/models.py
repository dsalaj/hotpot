from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from solo.models import SingletonModel
import datetime


class MenuItemRetailerPrice(models.Model):
    menuitem = models.ForeignKey('MenuItem')
    retailer = models.ForeignKey('Retailer')
    price = models.DecimalField(decimal_places=2, max_digits=6)


@python_2_unicode_compatible
class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2047)
    category = models.ForeignKey('Category')
    unit_price = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return str(self.pk) + ' ' + self.name

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


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ItemBatch(models.Model):
    item = models.ForeignKey('MenuItem')
    amount = models.PositiveIntegerField()
    menu = models.ForeignKey('Menu')

    class Meta:
        unique_together = ('item', 'menu',)


@python_2_unicode_compatible
class Menu(models.Model):
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()

    def __str__(self):
        return 'FROM ' + str(self.time_from.date()) + ' TO ' + str(self.time_to.date())

    @staticmethod
    def get_current_menu():
        now = datetime.datetime.now()
        try:
            menu = Menu.objects.get(time_from__lte=now, time_to__gte=now)
            return menu
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_current_menu_items():
        return [i.item for i in Menu.get_current_menu().itembatch_set.all()]

    def clean(self):
        time_from = self.time_from
        time_to = self.time_to
        menus = Menu.objects.filter(~Q(pk=self.pk))
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
    total_price = models.DecimalField(decimal_places=2, max_digits=8)


@python_2_unicode_compatible
class Order(models.Model):
    order_year = models.DateField(default=datetime.date.today)
    order_number = models.IntegerField(unique_for_year=order_year)

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
    note = models.TextField(max_length=2047, blank=True)
    total_price = models.DecimalField(decimal_places=2, max_digits=8, null=True)

    @property
    def serial_number(self):
        return str(self.order_year.year)+'/'+str(self.order_number)

    def __str__(self):
        return self.serial_number + ' - ' + str(self.email)

    class Meta:
        unique_together = ('order_year', 'order_number',)

    def save(self, *args, **kwargs):
        if not self.order_number:
            o = Order.objects.filter(order_year__year=datetime.date.today().year).order_by('order_number').last()
            if o is not None:
                self.order_number = o.order_number + 1
            else:
                self.order_number = 1
        super(Order, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Retailer(models.Model):
    password = models.CharField(max_length=40)

    def __str__(self):
        return self.password


class Shipping(SingletonModel):
    price = models.DecimalField(decimal_places=2, max_digits=6, default=10)
    treshold = models.DecimalField(decimal_places=2, max_digits=6, default=50)
    class Meta:
        verbose_name = "Shipping"


class DeliveryDays(models.Model):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    DAY = (
        (MON, 'Montag'),
        (TUE, 'Dienstag'),
        (WED, 'Mittwoch'),
        (THU, 'Donnerstag'),
        (FRI, 'Freitag'),
        (SAT, 'Samstag'),
        (SUN, 'Sonntag')
    )
    shipping = models.ForeignKey('Shipping')
    day = models.IntegerField(choices=DAY)
    time = models.TimeField()
