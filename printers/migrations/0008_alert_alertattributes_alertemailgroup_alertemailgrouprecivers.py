# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-22 20:07
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0007_auto_20161022_1724'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alerttype', models.CharField(choices=[('[alert-toner]', 'Alerta de Toner Bajo')], max_length=200)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AlertAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=500)),
                ('alert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='printers.Alert')),
            ],
        ),
        migrations.CreateModel(
            name='AlertEmailGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alerttype', models.CharField(choices=[('[alert-toner]', 'Alerta de Toner Bajo')], max_length=200)),
                ('send_email', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='AlertEmailGroupRecivers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=200, validators=[django.core.validators.EmailValidator()])),
                ('name', models.CharField(max_length=200)),
                ('alert_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='printers.AlertEmailGroup')),
            ],
        ),
    ]
