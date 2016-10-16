# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 21:27
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0002_auto_20161012_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='address',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='center',
            name='email',
            field=models.EmailField(max_length=200, validators=[django.core.validators.EmailValidator()]),
        ),
        migrations.AlterField(
            model_name='center',
            name='phone',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')]),
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=200, validators=[django.core.validators.EmailValidator()]),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')]),
        ),
        migrations.AlterField(
            model_name='printer',
            name='ip_address',
            field=models.GenericIPAddressField(validators=[django.core.validators.validate_ipv46_address]),
        ),
    ]
