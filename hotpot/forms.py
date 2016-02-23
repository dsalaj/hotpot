from django.forms import ModelForm, RadioSelect
from hotpot.models import Order, Retailer
import datetime
from dateutil import relativedelta
from django import forms

def pretty_date(day):
    return '('+str(day.day)+'.'+str(day.month)+')'


def next_delivery_dates():
    today = datetime.date.today()
    tuesday = today + relativedelta.relativedelta(weekday=1)
    wednesday = today + relativedelta.relativedelta(weekday=2)
    return ((tuesday,'Dienstag '+pretty_date(tuesday)), (wednesday,'Mittwoch '+pretty_date(wednesday)))


class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ['order_number', 'timestamp']
        widgets = {'delivery_date': RadioSelect(choices=next_delivery_dates())}


class RetailerLogin(ModelForm):
    class Meta:
        model = Retailer
        fields = ['password']

    def clean_password(self):
        data = self.cleaned_data['password']
        if data not in Retailer.objects.all().__str__():
            raise forms.ValidationError("Wrong password!")
        return data
