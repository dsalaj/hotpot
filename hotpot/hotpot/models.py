from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2047)
    category = models.ForeignKey('Category')
    unit_price = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name


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

    def clean(self):
        data = self.cleaned_data
        time_from = data['time_from']
        time_to = data['time_to']

        if not (trial_stop > trial_start):
            raise forms.ValidationError('trial stop must be > trial start')

        return data

class OrderItem(models.Model):
    order = models.ForeignKey('Order')
    item = models.ForeignKey('MenuItem')
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
    timestamp = models.DateTimeField(auto_created=True)
    delivery_date = models.DateField()
    title = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    note = models.CharField(max_length=2047)

    def __str__(self):
        return str(self.timestamp) + ' ' + str(self.email)