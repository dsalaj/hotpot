from django.forms import ModelForm, RadioSelect
from hotpot.models import *
import datetime
from dateutil import relativedelta
from django import forms


def pretty_date(day):
    return '('+str(day.day)+'.'+str(day.month)+')'


def next_delivery_dates():
    delivery_days = Shipping.objects.get().deliverydays_set.all()
    days_tuple = ()
    today = datetime.date.today()
    now = datetime.datetime.now()
    for dd in delivery_days:
        if today.weekday() == dd.day:
            date = datetime.datetime.combine(today+relativedelta.relativedelta(days=7), dd.time)
        else:
            date = datetime.datetime.combine(today+relativedelta.relativedelta(weekday=dd.day), dd.time)
        try:
            menu = Menu.objects.get(time_from__lte=now, time_to__gte=now)
            end_menu_time = menu.time_to.replace(tzinfo=None)
        except ObjectDoesNotExist:
            end_menu_time = now
        print str(dd.get_day_display()) + ' ' + str(date > now) + ' ' + str(end_menu_time > date) + ' ' + \
              str((date - end_menu_time) < ((end_menu_time + relativedelta.relativedelta(hours=25)) - end_menu_time))
        if date > now and (end_menu_time > date or
           (date - end_menu_time) < ((end_menu_time + relativedelta.relativedelta(hours=25)) - end_menu_time)):

            days_tuple = days_tuple + ((date, str(dd.get_day_display()+' '+pretty_date(date))),)
    return days_tuple
    # BACKUP CODE
    # tuesday = today + relativedelta.relativedelta(weekday=1)
    # wednesday = today + relativedelta.relativedelta(weekday=2)
    # return ((tuesday,'Dienstag '+pretty_date(tuesday)), (wednesday,'Mittwoch '+pretty_date(wednesday)))


class OrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['delivery_date'].widget = RadioSelect(choices=next_delivery_dates())

    class Meta:
        model = Order
        exclude = ['order_number', 'timestamp']
        #widgets = {'delivery_date': RadioSelect(choices=next_delivery_dates())}


class RetailerLogin(ModelForm):
    class Meta:
        model = Retailer
        fields = ['password']

    def clean_password(self):
        data = self.cleaned_data['password']
        if data not in Retailer.objects.all().__str__():
            raise forms.ValidationError("Wrong password!")
        return data
