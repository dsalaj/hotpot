from __future__ import unicode_literals
from django.db import models
from hotpot import settings
import hashlib
import time


def createNewsletterHash(email):
    h = hashlib.sha256()
    h.update(str(round(time.time() / 604800)))  # valid for 7 days
    h.update(email)
    h.update(settings.SECRET_KEY)
    return h.hexdigest()


class NewsletterSubscriber(models.Model):
    email = models.EmailField(max_length=70, unique=True)
    active = models.BooleanField(default=False)
