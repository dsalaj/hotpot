from django.forms import ModelForm, TextInput
from newsletter.models import NewsletterSubscriber


class NewsletterForm(ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': TextInput(attrs={'placeholder': 'Enter Email Address'}),
        }