from __future__ import unicode_literals
from django.core.validators import validate_email, validate_ipv46_address, RegexValidator
from django.db import models

# Create your models here.

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


class Customer(models.Model):
	name = models.CharField(max_length=200)
	rut = models.CharField(max_length=200)
	address = models.TextField(max_length=500)
	phone = models.CharField(max_length=200, validators=[phone_regex])
	email = models.EmailField(max_length=200, validators = [validate_email])

class Center(models.Model):
	name = models.CharField(max_length=200)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	address = models.TextField(max_length=500)
	phone = models.CharField(max_length=200, validators =[phone_regex])
	city = models.CharField(max_length=200)
	district = models.CharField(max_length=200)
	state = models.CharField(max_length=200)
	email = models.EmailField(max_length=200, validators = [validate_email])
	manager_name  = models.CharField(max_length=200)
	manager_phone = models.CharField(max_length=200)



class Printer(models.Model):
	center = models.ForeignKey(Center, on_delete=models.CASCADE)
	brand = models.CharField(max_length=200)
	model = models.CharField(max_length=200)
	serial_number = models.CharField(max_length=200)
	host_name = models.CharField(max_length=200)
	ip_address = models.GenericIPAddressField(validators = [validate_ipv46_address])

class MailsToProcess(models.Model):
	xml_path = models.CharField(max_length = 200)
	date = models.DateTimeField()
	done = models.BooleanField()

class PrinterReport(models.Model):
	printer = models.ForeignKey(Printer, on_delete = models.CASCADE)
	ip_address = models.GenericIPAddressField(validators = [validate_ipv46_address])
	mac_address = models.CharField(max_length=200)
	model = models.CharField(max_length=200)
	serial_number = models.CharField(max_length=200)
	host_name = models.CharField(max_length=200)
	toner_level = models.CharField(max_length=200)
	pages_printed = models.IntegerField(blank = True)
	status = models.CharField(max_length=200)
	date = models.DateTimeField()

