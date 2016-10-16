from __future__ import absolute_import
import os
from .util.email_fetcher import FetchEmail
from celery import shared_task
from datetime import datetime
from .models import MailsToProcess
import email.utils
import xml.etree.ElementTree as ET

@shared_task
def monitorReportMail(server, username, password, markasRead = True):
	print 'marking email as Seen: %s' % markasRead
	emailtFetcher = FetchEmail(server,username,password)
	emails = emailtFetcher.fetch_unread_messages(markasRead)
	print 'processing %d emails' % len(emails)
	for idx, msg in enumerate(emails):
		print 'procesing email q'
		tuple9 = email.utils.parsedate(msg.get('date'))
		dt_obj = datetime(*tuple9[0:6])
		print dt_obj
		files = emailtFetcher.save_attachment(msg,'/opt/apps/printer-monitor_env/printer_monitor/xml',idx)
		for f in files:
			print f
			obj = MailsToProcess(xml_path = f, date= dt_obj, done=False)
			obj.save()
			print obj.id
	emailtFetcher.close_connection()
	return True

@shared_task
def procesXmlFiles(path, processedPath):
	for file in os.listdir(path):
		tree = ET.parse(os.path.join(path,file))
		root = tree.getroot()
		for m in root: #printers
			for attr in m:
				if attr[0].text == 'DeviceIpAddress':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'DeviceMacAddress':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'DeviceHostName':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'DeviceModelName':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'DeviceSerialNumber':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'deviceAggregateTonerLevels':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'deviceAggregateStatus':
					if attr[1].text:
						print attr[1].text
				elif attr[0].text == 'DevicePagesPrinted':
					if attr[1].text:
						print attr[1].text
				
	return True