from newsletter.models import NewsletterSubscriber, createNewsletterHash
from newsletter.forms import NewsletterForm
from django.core import mail
from smtplib import SMTPException
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from hotpot import settings
import logging
logger = logging.getLogger('demabu.' + __name__)


def newsletter_view_helper(request, view_context):
    context = {}
    context['subscribed'] = False

    action = request.GET.get("action")
    subscriber_hash = request.GET.get("subscriber")
    subscriber_email = request.GET.get("email")
    if (action and subscriber_hash and subscriber_email) is not None:
        try:
            subscriber = NewsletterSubscriber.objects.get(email=subscriber_email)
            if subscriber_hash == createNewsletterHash(subscriber_email):
                if action == 'confirm':
                    subscriber.active = True
                    subscriber.save()
                    context['activated'] = True
                elif action == 'unsubscribe':
                    subscriber.active = False
                    subscriber.save()
                    context['unsubscribed'] = True
                else:
                    context['invalid'] = True
            else:
                context['invalid'] = True
        except NewsletterSubscriber.DoesNotExist:
            context['invalid'] = True

    if request.POST:
        newsletter_form = NewsletterForm(request.POST, request.FILES)
        if newsletter_form.is_valid():
            email = newsletter_form.cleaned_data['email']
            NewsletterSubscriber.objects.create(email=email)
            context['subscribed'] = True
            send_newsletter_subscription_mail(email, createNewsletterHash(email), request.META['HTTP_HOST'])
    else:
        newsletter_form = NewsletterForm()
    context['newsletter_form'] = newsletter_form
    view_context.update(context)


def send_newsletter_subscription_mail(email, hash, host):
    try:
        connection = mail.get_connection()
    except SMTPException as e:
        logger.error("Failed to open connection to mail server",
                     exc_info=True, extra={'request': None, 'error':e})
        return

    sender_address = settings.DEFAULT_FROM_EMAIL
    mail_list = []
    #site_uri = settings.LINK_PREFIX + Site.objects.get_current().domain
    site_uri = host

    # hotpot new newsletter subscription email
    hotpot_context = { 'subscriber_email': email, 'site_uri': site_uri }
    hotpot_text_message = render_to_string('email/hotpot_new_subscription.txt', hotpot_context)
    hotpot_mail = mail.EmailMessage('New Newsletter Subscription',
                                    hotpot_text_message,
                                    sender_address,
                                    [settings.DEFAULT_FROM_EMAIL])
    mail_list.append(hotpot_mail)

    # subscriber new newsletter subscription email
    subscriber_context = { 'subscriber_email': email, 'subscriber_hash': hash, 'site_uri': site_uri }
    subscriber_text_message = render_to_string('email/subscriber_new_subscription.txt', subscriber_context)
    subscriber_mail = mail.EmailMessage('HOTPOT Newsletter Subscription',
                                        subscriber_text_message,
                                        sender_address,
                                        [email])
    mail_list.append(subscriber_mail)

    for message in mail_list:
        try:
            message.connection = connection
            message.send()
        except SMTPException as e:
            logger.error("Sending mail to %s failed" % (str(message.to)),
                         exc_info=True, extra={'request': None, 'mailmessage': message, 'error': e})
    connection.close()
