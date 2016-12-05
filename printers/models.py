from __future__ import unicode_literals
from django.core.validators import validate_email, validate_ipv46_address, RegexValidator
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="El formato para el campo es el siguiente: '+999999999'.")

ALERT_TYPE = [('[alert-toner]', 'Alerta de Toner Bajo'), ('[alert-no_report]','Alerta de No reporte recibido')]
PRINTER_TYPE = [('mono','Mono'),('color', 'Color') ]

class Customer(models.Model):
	name = models.CharField(max_length=200)
	rut = models.CharField(max_length=200, null=True, blank=True)
	address = models.TextField(max_length=500, null=True, blank=True)
	phone = models.CharField(max_length=200, validators=[phone_regex], null=True, blank=True)
	email = models.EmailField(max_length=200, validators = [validate_email], null=True, blank=True)
	user = models.ManyToManyField(User, blank = True, null =True)

	def as_json(self):
		dic = dict(
		name = self.name,
		rut = self.rut,
		address = self.address,
		phone = self.phone,
		email = self.email,
		customer_id = self.id,

		)
		if hasattr(self, 'total_disconect'):
			dic['total_disconect'] = self.total_disconect
		if hasattr(self, 'total_low_toner'):
			dic['total_low_toner'] = self.total_low_toner
		
		if hasattr(self, 'total_centers'):
			dic['total_centers'] = self.total_centers
		if hasattr(self, 'total_printers'):
			dic['total_printers'] = self.total_printers
		if hasattr(self, 'total_pages'):
			dic['total_pages'] = self.total_pages	
		return dic	


class Center(models.Model):
	name = models.CharField(max_length=200)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	address = models.TextField(max_length=500, null=True, blank=True)
	phone = models.CharField(max_length=200, validators =[phone_regex], null=True, blank=True)
	city = models.CharField(max_length=200, null=True, blank=True)
	district = models.CharField(max_length=200, null=True, blank=True)
	state = models.CharField(max_length=200, null=True, blank=True)
	email = models.EmailField(max_length=200, validators = [validate_email], null=True, blank=True)
	manager_name  = models.CharField(max_length=200, null=True, blank=True)
	manager_phone = models.CharField(max_length=200, null=True, blank=True)
	order = models.IntegerField(null=True,blank=True)
	def as_json(self):


		dic = dict(
    	center_id = self.id,
    	name = self.name,
    	customer_name = self.customer.name,
    	customer = self.customer.id,
    	address = self.address,
    	phone = self.phone,
    	city = self.city,
    	district = self.district,
    	state = self.state,
    	email = self.email,
    	manager_name = self.manager_name,
    	manager_phone = self.manager_phone
    	)
		if hasattr(self, 'total_low_toner'):
			dic['total_low_toner'] = self.total_low_toner
		if hasattr(self, 'total_disconect'):
			dic['total_disconect'] = self.total_disconect
		if hasattr(self, 'total_printers'):
			dic['total_printers'] = self.total_printers
		if hasattr(self, 'total_pages'):
			dic['total_pages'] = self.total_pages
		return dic
    	



class Printer(models.Model):
	center = models.ForeignKey(Center, on_delete=models.CASCADE)
	last_report = models.ForeignKey('PrinterReport', blank = True, null = True)
	brand = models.CharField(max_length=200, blank=True,null=True)
	mac_address = models.CharField(max_length = 200, blank=True, null=True)
	model = models.CharField(max_length=200, blank=True, null=True)
	serial_number = models.CharField(max_length=200, blank =True,null=True)
	host_name = models.CharField(max_length=200, blank=True, null=True)
	ip_address = models.GenericIPAddressField(validators = [validate_ipv46_address], blank=True, null=True)
	printer_type =  models.CharField(max_length=200, choices=PRINTER_TYPE, default = PRINTER_TYPE[0][0])
	location = models.CharField(max_length=200, blank=True, null=True)

	def getPrinterTypePretty(self):
		ret = 'Desconocido'
		for a,y in PRINTER_TYPE:
			if a == self.alerttype:
				ret = y
				break
		return ret

	def as_json(self):
		dic = dict(
			id=self.id,
			center_name = self.center.name,
			center_id = self.center.id,
			last_report = self.last_report.as_json() if self.last_report else {},
			brand = self.brand,
			model = self.model,
			serial_number = self.serial_number,
			host_name = self.host_name,
			ip_address = self.ip_address,
			printer_type = self.printer_type,
			location = self.location
			
			)
		return dic


class MailsToProcess(models.Model):
	xml_path = models.CharField(max_length = 200)
	date = models.DateTimeField()
	done = models.BooleanField()

class PrinterReport(models.Model):
	printerOwner = models.ForeignKey(Printer, on_delete = models.CASCADE)
	ip_address = models.GenericIPAddressField(validators = [validate_ipv46_address])
	mac_address = models.CharField(max_length=200)
	model = models.CharField(max_length=200)
	serial_number = models.CharField(max_length=200)
	host_name = models.CharField(max_length=200)
	toner_level = models.CharField(max_length=200,blank = True, null=True)
	pages_printed = models.IntegerField(blank = True, null=True)
	status = models.CharField(max_length=200,blank = True, null=True)
	date = models.DateTimeField()
	is_valid = models.BooleanField(default = False)
	def as_json(self):
		return dict(
    	printer_id = self.printerOwner.id,
    	ip_address = self.ip_address,
    	mac_address = self.mac_address,
    	model = self.model,
    	serial_number = self.serial_number,
    	host_name = self.host_name,
    	toner_level = self.toner_level,
    	pages_printed = self.pages_printed,
    	status = self.status,
    	date = self.date.strftime('%d-%m-%Y at %H:%M:%S'))

class Alert(models.Model):
	alerttype = models.CharField(max_length = 200, choices = ALERT_TYPE)
	date = models.DateTimeField(auto_now = True)
	processed = models.BooleanField(default=False)
	printerOwner = models.ForeignKey(Printer, on_delete = models.CASCADE, blank =True, null = True)
	def getAlertTypePretty(self):
		ret = 'Desconocido'
		for a,y in ALERT_TYPE:
			if a == self.alerttype:
				ret = y
				break
		return ret

class AlertAttributes(models.Model):
	alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
	key = models.CharField(max_length=50)
	value = models.CharField(max_length=500)

class AlertEmailGroup(models.Model):
	alerttype = models.CharField(max_length=200, choices=ALERT_TYPE)
	send_email = models.BooleanField()

class AlertEmailGroupRecivers(models.Model):
	alert_group = models.ForeignKey(AlertEmailGroup, on_delete=models.CASCADE)
	email = models.EmailField(max_length=200, validators = [validate_email])
	name = models.CharField(max_length=200)






