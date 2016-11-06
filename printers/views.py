import json,re, datetime
from django.shortcuts import render
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

# Create your views here.
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
				return JsonResponse({'msg':'Error: Wrong Credentials'}, status = 401)

		 
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
	q = PrinterReport.objects.all()
	fromdate = request.GET.get('from')
	todate = request.GET.get('to')
	center = request.GET.get('center_id')
	forma = request.GET.get('format')
	headers = []
	if todate and fromdate:
		pat = r'([0-9]{4})\-([0-9]{2})\-([0-9]{2})'
		if re.search(pat,todate) and re.search(pat,fromdate):
			headers.append('From: %s' % fromdate)
			headers.append('To: %s' % todate)
			q = q.filter(date__range=[fromdate,todate]).order_by('-date')
	else:
		headers.append('')
		headers.append('')
	if center and center != '':
		q = q.filter(printerOwner__center__id = int(center))
		headers.append('Center: %s' % Center.objects.get(pk = int(center)).name)
	else:
		headers.append('')
	response = None
	file = None
	data = []
	cols = ['IP', 'MAC', 'MODEL', 'SERIAL', 'HOST', 'TONER LEVEL', 'PAGES', 'STATUS', 'DATE']
	if forma == 'pdf':
		
		data.append(cols)
		for p in q:
			row = [p.ip_address, p.mac_address, p.model, p.serial_number, p.host_name, p.toner_level, p.pages_printed, p.status, p.date.strftime('%d-%m-%Y at %H:%M:%S')]
			data.append(row)

		file ='printers/static/download/'+ generatePrinterReport(data,headers)
		
	if forma == 'xls':
		for p in q:
			row = [p.ip_address, p.mac_address, p.model, p.serial_number, p.host_name, p.toner_level, p.pages_printed, p.status, p.date.strftime('%d-%m-%Y at %H:%M:%S')]
			data.append(row)
		file = 'printers/static/download/'+ generatePrinterReportXls(data,headers,cols)

	f = open(file, "r")
	response = HttpResponse(FileWrapper(f), content_type='application/%s' % forma)
	response['Content-Disposition'] = 'attachment; filename=%s' % file
	f.close()
	return response
 
@login_required()
def report_data(request):
	q = Center.objects.all() 
	if not (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
		print 'Filtrandoo'
		q = q.filter(customer__user = request.user)

	centers = []
	for c in q:
		centers.append({'id':c.id,'name':c.name})
	print centers
	return render(request, 'reportData.html', {'centers':centers})
@login_required()
def reporPrinterJson(request):
	res = {}
	q = PrinterReport.objects.all()
	fromdate = request.GET.get('from')
	todate = request.GET.get('to')
	center = request.GET.get('center_id')
	if todate and fromdate:
		pat = r'([0-9]{4})\-([0-9]{2})\-([0-9]{2})'
		if re.search(pat,todate) and re.search(pat,fromdate):
			
			q = q.filter(date__range=[fromdate,todate]).order_by('-date')
	if center:
		q = q.filter(printerOwner__center__id = int(center))
	res['data'] =[ob.as_json() for ob in q]
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
		print 'Filtrando CUSTOMER'
		q = Printer.objects.filter(center__customer__user = request.user)
	if center_id:
		q = q.filter(center__id = center_id )
	res['data'] =[ob.as_json() for ob in q]
	return JsonResponse(res)

@login_required()
def report(request, customer_id = None):
	if not customer_id:
		return render(request,'report.html')
	else:
		return render(request, 'reportCust.html', {'customer_id': customer_id})

@login_required()
def center(request, center_id):
	return render(request,'reportCent.html',{'center_id':center_id})


