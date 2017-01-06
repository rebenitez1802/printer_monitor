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
			_next = '/printers/customer/'
			
			if request.GET.get('next'):
				_next = request.GET.get('next')
			
			
			user = authenticate(username=request.POST['user'], password=request.POST['password'])
			if user:
				login(request, user)
				
				return JsonResponse({'msg':'OK', 'status': 'Loged', 'next': _next })
			else:
				return JsonResponse({'msg':'Error: El usuario y el password no coinciden'}, status = 401)

		 
		return render(request,'login.html')
	else:
		return redirect('printers.views.report')
def countPages(p,_list):
	added = False
	for cent in _list:
		if p['center_name'] == cent[0]:
			cent[1] = cent[1] + int(p['last_report']['pages_printed']) 
			added=True
			break
	if not added:
		_list.append([p['center_name'],p['last_report']['pages_printed']])

def getMonth(m):
	for n,name in settings.MY_MONTHS:
		
		if m == n:
			return name.upper()

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
	alerts = request.GET.get('alerts')
	headers = []
	
	qr = PrinterReport.objects.all().order_by('-date')
	tope = timezone.make_aware(datetime.datetime.now() -datetime.timedelta(days = 7), timezone.get_default_timezone())
	
	if year and month:
		fromdate = '%s-%s-01' % (year,completeZeros(month,2))
		if int(month) + 1 < 13:
			todate = '%s-%s-01' % (year, completeZeros(str(int(month) + 1),2))
		else:
			todate = '%s-%s-01' % (str(int(year)+1), completeZeros(str(int(month) + 1 - 12),2))
		
		if timezone.make_aware( datetime.datetime.strptime(todate,'%Y-%m-%d') - datetime.timedelta(days = 7),timezone.get_default_timezone()) < tope:
			tope = timezone.make_aware( datetime.datetime.strptime(todate,'%Y-%m-%d') - datetime.timedelta(days = 7),timezone.get_default_timezone())
		

		qr = qr.filter(date__range=[fromdate,todate]).order_by('-date')
		

	
	if customer:
		q = q.filter(center__customer__id = int(customer))
		cname = Customer.objects.get(pk = int(customer)).name
	
	
	else:
		cname = ''
	response = None
	file = None
	data = []
	cols = ['Modelo', 'Numero de Serie', 'Direccion IP', 'Nombre del Host', 'Sucursal', 'Paginas']
	data_tuples = []
	res = {}
	res['data'] =[ob.as_json() for ob in q.order_by('center__order')]
	pat = r'[0-9]+'
	addStyles = [
                      ('BOX',(0,0),(-1,-1),2,colors.black),
                      ('GRID',(0,0),(-1,-1),0.5,colors.black),
                      ('FONTSIZE', (0,0),(-1,-1,), 8),
                      ('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('FONT', (0, 1), (-1, -1), 'Helvetica'),
		  				('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                      ('BACKGROUND',(0,0),(-1,0),colors.gray),
                      #('BACKGROUND',(0,0),(0,-1),colors.red)
  	]
	xlsAddStyles = []
	j = 0 
	for p in res['data']:
		p['last_report'] = {}
		for pr in qr:
			if pr.is_valid:
				#print pr.pages_printed
				if pr.printerOwner:
					if p['id'] == pr.printerOwner.id and re.search(pat, str(pr.pages_printed)):
						p['last_report'] = pr.as_json()
						
						if tope > pr.date:
							p['warning'] = True
							if alerts:
								addStyles.append(('BACKGROUND',(0,j+1),(-1,j+1),colors.yellow))
								xlsAddStyles.append((j+2,'FFFF00'))
						#	print 'warning %s' % j
						else:
							p['warning'] = False

						break
		if not p['last_report']:
			p['no-report'] = True
			if alerts:
				addStyles.append(('BACKGROUND',(0,j+1),(-1,j+1),colors.red))
				xlsAddStyles.append((j+2,'FF0000'))
			#print 'Alert %s' % j
		j = j + 1

	rrmono = []
	rrcolor = []
	totalpmono = 0
	totalpcolor = 0

	for p in res['data']:
		if p['printer_type'] == 'mono':
			if p['last_report']:
				if p['last_report']['pages_printed']:
					totalpmono = totalpmono + int(p['last_report']['pages_printed'])
					countPages(p,rrmono)
		else:
			if p['last_report']:
				if p['last_report']['pages_printed']:
					totalpcolor = totalpmono + int(p['last_report']['pages_printed'])
					countPages(p,rrcolor)
	rrdatamono = []
	_hmono = len(rrmono)/2 if len(rrmono)%2 == 0 else len(rrmono)/2 + 1

	for i in range(0,_hmono):
		if i == _hmono-1 and len(rrmono)%2 != 0:
			rrdatamono.append(rrmono[i+_hmono-1]+['','','',''])
		else:
			rrdatamono.append(rrmono[i]+['                   ']+rrmono[i+_hmono]+[''])
	rrdatamono.append(['', '','','','',''])
	rrdatamono.append(['Total Periodo', totalpmono,'','','','EQUIPOS MONOCROMO'])

	
	rrdatacolor = []
	_hcolor = len(rrcolor)/2 if len(rrcolor)%2 == 0 else len(rrcolor)/2 + 1

	for i in range(0,_hcolor):
		if i == _hcolor-1 and len(rrcolor)%2 != 0:
			rrdatacolor.append(rrcolor[i+_hcolor-1]+['','','',''])
		else:
			rrdatacolor.append(rrcolor[i]+['                   ']+rrcolor[i+_hcolor]+[''])
	rrdatacolor.append(['', '','','','',''])
	rrdatacolor.append(['Total Periodo', totalpcolor,'','','','EQUIPOS COLOR'])

	if forma == 'pdf':
		
		data.append(cols)
		for p in res['data']:
			row = [p['model'],p['serial_number'], p['ip_address'],p['host_name'], p['center_name'],  p['last_report']['pages_printed'] if p['last_report'] else '']
			data.append(row)

		resHStyles = [
		  ('FONT', (0, 0), (0, -1), 'Helvetica'),
		  ('FONT', (-1, 0), (-1, -1), 'Helvetica-Bold'),
          ('BOX',(0,0),(-1,-1),2,colors.black),
          
          
          ('FONTSIZE', (0,0),(0,-1,), 8),
		  ('FONTSIZE', (-1,0),(-1,-1,), 12),
          ('ALIGN',(-1,0),(-1,-1),'CENTER'),
          ('ALIGN',(0,0),(0,1),'LEFT'),
          
                      #('BACKGROUND',(-1,0),(-1,-1),colors.red),
        ]
		res1Styles = [
		  ('FONT', (0, 0), (-1, -1), 'Helvetica'),
		  ('FONT', (-1, -1), (-1, -1), 'Helvetica-Bold'),
          ('BOX',(0,0),(-1,-1),2,colors.black),
          ('BOX',(0,-2),(-1,-1),2,colors.black),
          ('BACKGROUND',(0,-2),(-1,-1),colors.gray),
          ('FONTSIZE', (0,0),(-1,-1,), 8),

          ('ALIGN',(1,0),(1,-2),'CENTER'),
          ('ALIGN',(4,0),(4,-2),'CENTER'),
          ('ALIGN',(0,0),(0,-2),'LEFT'),
          ('ALIGN',(3,0),(3,-2),'LEFT'),
                      #('BACKGROUND',(-1,0),(-1,-1),colors.red),
        ]
		res2Styles = [
		  ('FONT', (0, 0), (-1, -1), 'Helvetica'),
		  ('FONT', (-1, -1), (-1, -1), 'Helvetica-Bold'),
		  ('BOX',(0,0),(-1,-1),2,colors.black),
		  ('BOX',(0,-2),(-1,-1),2,colors.black),
		  ('BACKGROUND',(0,-2),(-1,-1),colors.yellow),
		  ('FONTSIZE', (0,0),(-1,-1,), 8),

		  ('ALIGN',(1,0),(1,-2),'CENTER'),
		  ('ALIGN',(4,0),(4,-2),'CENTER'),
		  ('ALIGN',(0,0),(0,-2),'LEFT'),
		  ('ALIGN',(3,0),(3,-2),'LEFT'),
		              #('BACKGROUND',(-1,0),(-1,-1),colors.red),
		]
		rrdataheader = []
		if year and month:
			rrdataheader.append(['Fecha de Creacion: %s' % (datetime.datetime.now().strftime('%d-%m-%Y')),'','', getMonth(int(month)) ])
			rrdataheader.append(['Cliente: %s' % cname,'','', year])
			rrdataheader.append(['Dispositivos: %s' % (len(data) - 1),'',''])
		else:
			rrdataheader.append(['Fecha de Creacion:  %s' % (datetime.datetime.now().strftime('%d-%m-%Y')),'','',''])
			rrdataheader.append(['Cliente: %s' % cname,'','', ''])
			rrdataheader.append(['Dispositivos: %s' % (len(data) - 1), '','',''])

		data_tuples.append((rrdataheader,resHStyles))
		data_tuples.append((rrdatamono,res1Styles))
		if len(rrdatacolor) > 2:
			data_tuples.append((rrdatacolor,res2Styles))
		data_tuples.append((data,addStyles))
		
		file = settings.PROJ_PATH + '/printers/static/download/'+ generatePrinterReport(data_tuples,showAlerts=True if alerts else False)
		
	if forma == 'xls':
		data.append(cols)
		for p in res['data']:
			row = [p['model'],p['serial_number'], p['ip_address'],p['host_name'], p['center_name'],  p['last_report']['pages_printed'] if p['last_report'] else '']
			data.append(row)

		datat=[]
		xlsAddStyles.append((1, '999999'))


		rrdataheader = []
		if year and month:
			rrdataheader.append(['Fecha de Creacion: %s' % (datetime.datetime.now().strftime('%d-%m-%Y')),'','','','', getMonth(int(month)) ])
			rrdataheader.append(['Cliente: %s' % cname,'','','','', year])
			rrdataheader.append(['Dispositivos: %s' % (len(data) - 1),'',''])
		else:
			rrdataheader.append(['Fecha de Creacion:  %s' % (datetime.datetime.now().strftime('%d-%m-%Y')),'','',''])
			rrdataheader.append(['Cliente: %s' % cname,'','', ''])
			rrdataheader.append(['Dispositivos: %s' % (len(data) - 1), '','',''])

		datat.append((rrdataheader,[]))

		datat.append((rrdatamono,[(_hmono+1,'999999'),(_hmono+2,'999999')]))
		if len(rrdatacolor) > 2:
			datat.append((rrdatacolor,[(_hcolor+1,'FFFF00'),(_hcolor+2,'FFFF00')]))

		datat.append((data,xlsAddStyles))
		titlexls = cname 
		if month and year:
			titlexls = titlexls + ' - '+getMonth(int(month))+' - '+str(year)
		file =  settings.PROJ_PATH + '/printers/static/download/'+ generatePrinterReportXls(datat,titlexls)

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
	
	qr = PrinterReport.objects.all().order_by('-date')
	todate  = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()).strftime('%Y-%m-%d')
	if year and month:
		fromdate = '%s-%s-01' % (year,completeZeros(month,2))
		
		if int(month) + 1 < 13:
			todate = '%s-%s-01' % (year, completeZeros(str(int(month) + 1),2))
		else:
			todate = '%s-%s-01' % (str(int(year)+1), completeZeros(str(int(month) -11),2))

		
		
		qr = qr.filter(date__range=[fromdate,todate]).order_by('-date')
		
		
	
	res['data'] =[ob.as_json() for ob in q]
	pat = r'[0-9]+'
	
	for p in res['data']:
		p['last_report'] = {}
		for pr in qr:
			if pr.is_valid:
				#print pr.pages_printed
				if p['id'] == pr.printerOwner.id and re.search(pat, str(pr.pages_printed)):
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
	
	now = datetime.datetime.now()
	q = q.filter(center__printer__last_report__date__year= now.year,
                 center__printer__last_report__date__month= now.month)
	q = q.annotate(total_pages= Sum('center__printer__last_report__pages_printed')).annotate(total_printers= Count('center__printer', distinct=True)).annotate(total_centers = Count('center',distinct = True))
	q = q.annotate(total_disconect = Sum(Case(When(center__printer__last_report__status__in = ['Error','Desconectado'], then = 1),When(center__printer__last_report__status__isnull = True, then = 0), default=0, output_field=IntegerField())))
	q = q.annotate(total_low_toner = Sum(Case(When(center__printer__last_report__toner_level__regex = r'(K\(([0-9]|10|\?)\))', then = 1),When(center__printer__last_report__toner_level__isnull = True, then = 0), default=0, output_field=IntegerField())))
	
	res['data'] =[ob.as_json() for ob in q]
	return JsonResponse(res)

@login_required()
def reportByCostumer(request, costumer_id):
	res = {}
	q = Center.objects.all()
	
	if not (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
		
		q = Center.objects.filter(printer__center__customer__user = request.user)

	q = q.filter(customer__id = costumer_id).annotate(total_pages= Sum('printer__last_report__pages_printed')).annotate(total_printers= Count('printer', distinct=True))
	q = q.annotate(total_disconect = Sum(Case(When(printer__last_report__status__in = ['Error','Desconectado'], then = 1),When(printer__last_report__status__isnull = True, then = 0), default=0, output_field=IntegerField())))
	q = q.annotate(total_low_toner = Sum(Case(When(printer__last_report__toner_level__regex = r'(K\(([0-9]|10|\?)\))', then = 1),When(printer__last_report__toner_level__isnull = True, then = 0), default=0, output_field=IntegerField())))
	
	res['data'] =[ob.as_json() for ob in q]

	'''for cen in res['data']:
		pl = Printer.objects.filter(center__id = cen['center_id'])
		cen['total_printers'] = len(pl)
		pagesp = 0
		lowt = 0
		discon = 0
		for p in pl:
			if p.last_report:
				if p.last_report.pages_printed:
					pagesp = pagesp + p.last_report.pages_printed
				if not p.last_report.status or p.last_report.status in ['Error','Desconectado']:
					discon = discon + 1
				if p.last_report.toner_level:
					regx = r'(K\(([0-9]|10|\?)\))'
					if re.match(regx,p.last_report.toner_level) or p.last_report.toner_level.strip() == '':
						lowt = lowt + 1
				else:
					print 'notiene toner'
					lowt = lowt + 1
			else:
				discon = discon + 1
				lowt = lowt + 1
		cen['total_pages'] = pagesp
		cen['total_disconect'] = discon
		cen['total_low_toner'] = lowt 

	'''
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
	breadcrumbs.append({'url': '/printers/customer/', 'title':'Clientes'})
	if not customer_id:
		return render(request,'report.html', {'breadcrumbs': breadcrumbs})
	else:
		c = Customer.objects.get(pk = customer_id)
		breadcrumbs.append({'url':'/customer/%s' % customer_id, 'title': c.name})
		return render(request, 'reportCust.html', {'customer_id': customer_id, 'breadcrumbs':breadcrumbs})

@login_required()
def center(request, center_id):
	
	breadcrumbs = []
	breadcrumbs.append({'url': '/printers/customer/', 'title':'Clientes'})
	if center_id:
		c = Center.objects.get(pk = center_id)
		breadcrumbs.append({'url':'/printers/customer/%s' % c.customer.id, 'title': c.customer.name})
		breadcrumbs.append({'url':'/printers/center/%s' % center_id, 'title': c.name})
	else:
		breadcrumbs.append({'url':'/center/', 'title': 'Todas las Impresoras'})
	return render(request,'reportCent.html',{'center_id':center_id, 'breadcrumbs': breadcrumbs})


