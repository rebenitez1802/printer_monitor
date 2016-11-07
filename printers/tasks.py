# coding=utf-8
from __future__ import absolute_import
import os, re
from .util.email_fetcher import FetchEmail
from celery import shared_task
from datetime import datetime
from .models import MailsToProcess, Printer, PrinterReport,Alert, AlertAttributes
import email.utils
import xml.etree.ElementTree as ET
from django.core.exceptions import ObjectDoesNotExist
import django
from django.conf import settings


def saveAlert(alertType, emailmsg):
	if alertType == '[alert-toner]' and emailmsg.get_payload(decode = True):
		a = Alert()
		a.alerttype = alertType
		tuple9 = email.utils.parsedate(emailmsg.get('date'))
		dt_obj = datetime(*tuple9[0:6])
		a.date = dt_obj
		a.save()
		for line in emailmsg.get_payload().split('\n'):
			if 'Nombre de Equipo: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'name', value= line.split('Nombre de Equipo: ')[1])
				att.save()
			elif 'Mac ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'mac', value= line.split('Mac ')[1])
				att.save()
			elif 'Dirección IP: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'ip_address', value= line.split('Dirección IP: ')[1])
				att.save()
			elif 'Número de Serie: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'serial_number', value= line.split('Número de Serie: ')[1])
				att.save()
			elif 'Contador Total: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'total_count', value= line.split('Contador Total: ')[1])
				att.save()

			elif 'Marca: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'brand', value= line.split('Marca: ')[1])
				att.save()
			elif 'Modelo: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'model', value= line.split('Modelo: ')[1])
				att.save()
			elif 'Nivel de Tóner en: ' in line:
				att = AlertAttributes(alert_id= a.id, key = 'toner_level', value= line.split('Nivel de Tóner en: ')[1])
				att.save()
				
		#Handle alert toner emails

@shared_task
def monitorAlertMail(server,username, password, markasRead= True):
	django.db.connection.close()
	print 'marking email as Seen: %s' % markasRead
	at_pat = r'(\[.+\]) .*'
	emailtFetcher = FetchEmail(server, username,password)
	emails = emailtFetcher.fetch_unread_messages(markasRead)
	print 'processing %d emails' % len(emails)
	for email in emails:
		if 'subject' in email:
			subject = email['subject']
			if re.search(re.compile(at_pat),subject):
				atype = re.search(re.compile(at_pat),subject).group(1)
				saveAlert(atype, email)
	return True



@shared_task
def monitorReportMail(server, username, password, markasRead = True):
	django.db.connection.close()
	print 'marking email as Seen: %s' % markasRead
	emailtFetcher = FetchEmail(server,username,password)
	emails = emailtFetcher.fetch_unread_messages(markasRead)
	print 'processing %d emails' % len(emails)
	for idx, msg in enumerate(emails):
		print 'procesing email q'
		tuple9 = email.utils.parsedate(msg.get('date'))
		dt_obj = datetime(*tuple9[0:6])
		print dt_obj
		files = emailtFetcher.save_attachment(msg,settings.XML_PATH,idx)
		for f in files:
			print f
			obj = MailsToProcess(xml_path = f, date= dt_obj, done=False)
			obj.save()
			print obj.id
	emailtFetcher.close_connection()
	return True
#this method must be erased
def createPrinters(pm):
  	'''
  	center = models.ForeignKey(Center, on_delete=models.CASCADE)
	brand = models.CharField(max_length=200)
	model = models.CharField(max_length=200)
	serial_number = models.CharField(max_length=200)
	host_name = models.CharField(max_length=200)
	ip_address = models.GenericIPAddressFiel
  	'''
	if pm:
		obj = Printer(center_id = 1, brand = pm.model.split(' ')[0], model = pm.model, serial_number = pm.serial_number, host_name = pm.host_name, ip_address = pm.ip_address)
		obj.save()
		return obj.id
	return None



@shared_task
def procesXmlFiles(createprinter = False):
	'''
	ip_address = models.GenericIPAddressField(validators = [validate_ipv46_address])
	mac_address = models.CharField(max_length=200)
	model = models.CharField(max_length=200)
	serial_number = models.CharField(max_length=200)
	host_name = models.CharField(max_length=200)
	toner_level = models.CharField(max_length=200)
	pages_printed = models.IntegerField(blank = True)
	status = models.CharField(max_length=200)
	date = models.DateTimeField()
	'''
	django.db.connection.close()
	xmls = MailsToProcess.objects.filter(done = False)
	for xml in xmls:
		
		tree = ET.parse(xml.xml_path)
		root = tree.getroot()
		for m in root: #printers
			obj = PrinterReport()
			for attr in m:
				if attr[0].text == 'DeviceIpAddress':
					if attr[1].text:
						print attr[1].text
						obj.ip_address = attr[1].text
				elif attr[0].text == 'DeviceMacAddress':
					if attr[1].text:
						print attr[1].text
						obj.mac_address = attr[1].text
				elif attr[0].text == 'DeviceHostName':
					if attr[1].text:
						print attr[1].text
						obj.host_name = attr[1].text
				elif attr[0].text == 'DeviceModelName':
					if attr[1].text:
						print attr[1].text
						obj.model = attr[1].text
				elif attr[0].text == 'DeviceSerialNumber':
					if attr[1].text:
						print attr[1].text
						obj.serial_number = attr[1].text

				elif attr[0].text == 'deviceAggregateTonerLevels':
					if attr[1].text:
						print attr[1].text
						obj.toner_level = attr[1].text
				elif attr[0].text == 'deviceAggregateStatus':
					if attr[1].text:
						print attr[1].text
						obj.status = attr[1].text
				elif attr[0].text == 'DevicePagesPrinted':
					if attr[1].text:
						print attr[1].text
						obj.pages_printed = attr[1].text
			obj.date = datetime.now()
			try:
				p = Printer.objects.get(serial_number = obj.serial_number)
			except ObjectDoesNotExist:
				p = None
			except Exception:
				p = None
			
			if p:
				obj.printerOwner_id = p.id
				obj.save()
				xml.done = True
				xml.save()
				p.last_report_id = obj.id 
				p.save()
			'''elif createprinter:

				idPrinter = createPrinters(obj)
				if idPrinter:
					obj.printer_id = idPrinter
					obj.save()
					xml.done = True
					xml.save()'''


	return True