# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=70, unique=True)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
    ]