from django.contrib import admin
from .models import Customer, Center,Printer, MailsToProcess, PrinterReport,Alert,AlertAttributes,AlertEmailGroup,AlertEmailGroupRecivers
from django import forms
# Register your models here.


class CustomModelChoiceField (forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)



class CustomerAdmin(admin.ModelAdmin):
	list_display = (['name'])



class CenterAdminForm(forms.ModelForm):
	customer = CustomModelChoiceField(queryset=Customer.objects.all())
	
	class Meta:
		model = Center
		fields = '__all__'


class CenterAdmin(admin.ModelAdmin):
	form = CenterAdminForm
	model = Center
	list_display = (['name','get_customer'])
	def get_customer(self,obj):
		return obj.customer.name
	get_customer.admin_order_field = 'customer'
	get_customer.short_description = 'Customer Name'



class PrinterAdminForm(forms.ModelForm):
	center = CustomModelChoiceField(queryset=Center.objects.all())
	
	class Meta:
		model = Printer
		fields = '__all__'

class PrinterAdmin(admin.ModelAdmin):
	form = PrinterAdminForm
	model = Printer
	list_display = (['mac_address','serial_number', 'brand', 'model', 'get_center',  'get_customer'])
	exclude = ('last_report',)
	list_filter = ('center__customer__name','center__name')

	def get_center(self,obj):
		return obj.center.name
	get_center.admin_order_field = 'center'
	get_center.short_description = 'Center Name'

	def get_customer(self,obj):
		return obj.center.customer.name
	get_customer.short_description = 'Customer Name'

class MailsToProcessAdmin(admin.ModelAdmin):
	model = MailsToProcess
	list_display = (['date','xml_path','done'])

class PrinterReportAdmin(admin.ModelAdmin):
	model = PrinterReport
	list_display =('date', 'serial_number', 'pages_printed','toner_level','status')

class AlertAttributesTubular(admin.TabularInline):
	model = AlertAttributes
	extra = 0

class AlertAdmin(admin.ModelAdmin):
	model = Alert
	list_display = ('date','alerttype','processed')
	inlines=[AlertAttributesTubular]
	exclude = ('printerOwner',)

class AlertEmailGroupReciversTubular(admin.TabularInline):
	model = AlertEmailGroupRecivers
	extra = 0

class AlertEmailGroupAdmin(admin.ModelAdmin):
	model= AlertEmailGroup
	list_display = ('alerttype','send_email')
	inlines = [AlertEmailGroupReciversTubular]

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Center, CenterAdmin)
admin.site.register(Printer, PrinterAdmin)
admin.site.register(MailsToProcess, MailsToProcessAdmin)
admin.site.register(PrinterReport, PrinterReportAdmin)
admin.site.register(Alert,AlertAdmin)
admin.site.register(AlertEmailGroup, AlertEmailGroupAdmin)