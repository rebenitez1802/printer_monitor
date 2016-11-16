import json,re, datetime
from django.shortcuts import render
from django.utils import timezone
from django.core import serializers
from django.db.models import Sum, Count, Case, When, IntegerField
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import PrinterReport, Center, Customer, Printer 
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .util.pdfmaker import generatePrinterReport
from .util.xlsmaker import generatePrinterReportXls
from wsgiref.util import FileWrapper
from reportlab.lib import colors


# Create your views here.
def _404(request):
	return render(request, '404.html')
def logout_view(request):
    logout(request)
    return redirect('printers.views.login_view')

def login_view(request):
	if not request.user.is_authenticated():
		
		if request.method == 'POST':
			_next = '/customer'
			print request.path
			if request.GET.get('next'):
				_next = request.GET.get('next')
			print _next
			
			user = authenticate(username=request.POST['user'], password=request.POST['password'])
			if user:
				login(request, user)
				
				return JsonResponse({'msg':'OK', 'status': 'Loged', 'next': _next })
			else:
				return JsonResponse({'msg':'Error: El usuario y el password no coinciden'}, status = 401)

		 
		return render(request,'login.html')
	else:
		return redirect('printers.views.report')


@login_required()
def generatePrinterReportPdf(request):
	'''
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
	'''
	q = Printer.objects.all()
	year = request.GET.get('year')
	month = request.GET.get('month')
	customer = request.GET.get('customer')
	forma = request.GET.get('format')
	headers = []
	
	qr = PrinterReport.objects.all()
	tope = timezone.make_aware(datetime.datetime.now() -datetime.timedelta(days = 7), timezone.get_default_timezone())
	
	if year and month:
		fromdate = '%s-%s-01' % (year,completeZeros(month,2))
		todate = '%s-%s-01' % (year, completeZeros(str(int(month) + 1),2))
		
		
		if timezone.make_aware( datetime.datetime.strptime(todate,'%Y-%m-%d') - datetime.timedelta(days = 7),timezone.get_default_timezone()) < tope:
			tope = timezone.make_aware( datetime.datetime.strptime(todate,'%Y-%m-%d') - datetime.timedelta(days = 7),timezone.get_default_timezone())
		

		qr = qr.filter(date__range=[fromdate,todate]).order_by('-date')
		headers.append(u'Mes %s-%s' % (month,year))
		headers.append('')

	
	else:
		
		headers.append('')
		headers.append('')
	print tope
	if customer:
		q = q.filter(center__customer__id = int(customer))
		headers.append('Cliente %s' % Customer.objects.get(pk = int(customer)).name)
	
	
	else:
		headers.append('')
	response = None
	file = None
	data = []
	cols = ['IP', 'MAC', 'MODELO', 'SERIAL', 'HOST', 'TONER', 'PAGINAS', 'ESTATUS', 'FECHA']
	
	res = {}
	res['data'] =[ob.as_json() for ob in q]
	pat = r'[0-9]+'
	addStyles = []
	xlsAddStyles = []
	j = 0 
	for p in res['data']:
		p['last_report'] = {}
		for pr in qr:
			if pr.is_valid:
				#print pr.pages_printed
				if p['serial_number'] == pr.serial_number and re.search(pat, str(pr.pages_printed)):
					p['last_report'] = pr.as_json()
					
					if tope > pr.date:
						p['warning'] = True
						addStyles.append(('BACKGROUND',(0,j+1),(-1,j+1),colors.yellow))
						xlsAddStyles.append((j+1,'FFFF00'))
					#	print 'warning %s' % j
					else:
						p['warning'] = False

					break
		if not p['last_report']:
			p['no-report'] = True
			addStyles.append(('BACKGROUND',(0,j+1),(-1,j+1),colors.red))
			xlsAddStyles.append((j+1,'FF0000'))
			#print 'Alert %s' % j
		j = j + 1
	if forma == 'pdf':
		
		data.append(cols)
		for p in res['data']:
			row = [p['ip_address'], p['last_report']['mac_address'] if p['last_report'] else '' , p['model'], p['serial_number'], p['host_name'], p['last_report']['toner_level'] if p['last_report'] else '', p['last_report']['pages_printed'] if p['last_report'] else '', p['last_report']['status'] if p['last_report'] else '', p['last_report']['date'] if p['last_report'] else '']
			data.append(row)

		print len(data)
		file ='printers/static/download/'+ generatePrinterReport(data,headers,addStyles)
		
	if forma == 'xls':
		for p in res['data']:
			row = [p['ip_address'], p['last_report']['mac_address'] if p['last_report'] else '' , p['model'], p['serial_number'], p['host_name'], p['last_report']['toner_level'] if p['last_report'] else '', p['last_report']['pages_printed'] if p['last_report'] else '', p['last_report']['status'] if p['last_report'] else '', p['last_report']['date'] if p['last_report'] else '']
			data.append(row)
		file = 'printers/static/download/'+ generatePrinterReportXls(data,headers,cols,xlsAddStyles)

	f = open(file, "r")
	response = HttpResponse(FileWrapper(f), content_type='application/%s' % forma)
	response['Content-Disposition'] = 'attachment; filename=%s' % file
	f.close()
	return response
 
@login_required()
def report_data(request):
	q = Customer.objects.all() 
	if not (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
		#print 'Filtrandoo'
		q = q.filter(user = request.user)

	customers = []
	for c in q:
		customers.append({'id':c.id,'name':c.name})
	#print centers
	months = settings.MY_MONTHS
	years = []
	for y in range(datetime.datetime.now().year,datetime.datetime.now().year - settings.MAX_YEARS, -1):
		years.append((y,'%s' % y))
	return render(request, 'reportData.html', {'centers':customers, 'months':months, 'years':years})


def completeZeros(strr,length):
	while len(strr) < length:
		strr = '0' + strr
	return strr

@login_required()
def reporPrinterJson(request):
	res = {}
	year = request.GET.get('year')
	month = request.GET.get('month')
	customer = request.GET.get('customer')

	q = Printer.objects.all()
	if customer:
		q = q.filter(center__customer__id = int(customer))
	
	qr = PrinterReport.objects.all()
	todate  = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()).strftime('%Y-%m-%d')
	if year and month:
		fromdate = '%s-%s-01' % (year,completeZeros(month,2))
		todate = '%s-%s-01' % (year, completeZeros(str(int(month) + 1),2))
		print 'range %s -- %s' % (fromdate, todate)
		qr = qr.filter(date__range=[fromdate,todate]).order_by('-date')
		print len(qr)
		
	
	res['data'] =[ob.as_json() for ob in q]
	pat = r'[0-9]+'
	
	for p in res['data']:
		p['last_report'] = {}
		for pr in qr:
			if pr.is_valid:
				#print pr.pages_printed
				if p['serial_number'] == pr.serial_number and re.search(pat, str(pr.pages_printed)):
					p['last_report'] = pr.as_json()
					if timezone.make_aware( datetime.datetime.strptime(todate,'%Y-%m-%d') - datetime.timedelta(days = 7),timezone.get_default_timezone()) > pr.date:
						p['warning'] = True
					else:
						p['warning'] = False

					break
		if not p['last_report']:
			p['no-report'] = True



	return JsonResponse(res)

@login_required()
def reportJson(request):
	res = {}
	q = Customer.objects.all()
	
	if not (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
		
		q = Customer.objects.filter(user = request.user)
	q = q.annotate(total_pages= Sum('center__printer__last_report__pages_printed')).annotate(total_printers= Count('center__printer', distinct=True)).annotate(total_centers = Count('center',distinct = True))
	q = q.annotate(total_disconect = Sum(Case(When(center__printer__last_report__status__in = ['Error','Desconectado'], then = 1),When(center__printer__last_report__status__isnull = True, then = 1), default=0, output_field=IntegerField())))
	q = q.annotate(total_low_toner = Sum(Case(When(center__printer__last_report__toner_level__regex = r'(K\(([0-9]|10|\?)\))', then = 1),When(center__printer__last_report__toner_level__isnull = True, then = 1), default=0, output_field=IntegerField())))
	print q
	res['data'] =[ob.as_json() for ob in q]
	return JsonResponse(res)

@login_required()
def reportByCostumer(request, costumer_id):
	res = {}
	q = Center.objects.all()
	
	if not (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
		
		q = Center.objects.filter(printer__center__customer__user = request.user)

	q = q.filter(printer__center__customer__id = costumer_id).annotate(total_pages= Sum('printer__last_report__pages_printed')).annotate(total_printers= Count('printer', distinct=True))
	q = q.annotate(total_disconect = Sum(Case(When(printer__last_report__status__in = ['Error','Desconectado'], then = 1),When(printer__last_report__status__isnull = True, then = 1), default=0, output_field=IntegerField())))
	q = q.annotate(total_low_toner = Sum(Case(When(printer__last_report__toner_level__regex = r'(K\(([0-9]|10|\?)\))', then = 1),When(printer__last_report__toner_level__isnull = True, then = 1), default=0, output_field=IntegerField())))
	res['data'] =[ob.as_json() for ob in q]
	return JsonResponse(res)

@login_required()
def reportByCenter(request, center_id):
	res = {}
	q = Printer.objects.all()
	
	if not (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
		#print 'Filtrando CUSTOMER'
		q = Printer.objects.filter(center__customer__user = request.user)
	if center_id:
		q = q.filter(center__id = center_id )
	res['data'] =[ob.as_json() for ob in q]
	return JsonResponse(res)

@login_required()
def report(request, customer_id = None):
	breadcrumbs = []
	breadcrumbs.append({'url': '/customer/', 'title':'Clientes'})
	if not customer_id:
		return render(request,'report.html', {'breadcrumbs': breadcrumbs})
	else:
		c = Customer.objects.get(pk = customer_id)
		breadcrumbs.append({'url':'/customer/%s' % customer_id, 'title': c.name})
		return render(request, 'reportCust.html', {'customer_id': customer_id, 'breadcrumbs':breadcrumbs})

@login_required()
def center(request, center_id):
	
	breadcrumbs = []
	breadcrumbs.append({'url': '/customer/', 'title':'Clientes'})
	if center_id:
		c = Center.objects.get(pk = center_id)
		breadcrumbs.append({'url':'/customer/%s' % c.customer.id, 'title': c.customer.name})
		breadcrumbs.append({'url':'/center/%s' % center_id, 'title': c.name})
	else:
		breadcrumbs.append({'url':'/center/', 'title': 'Todas las Impresoras'})
	return render(request,'reportCent.html',{'center_id':center_id, 'breadcrumbs': breadcrumbs})


