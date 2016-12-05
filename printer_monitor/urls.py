"""printer_monitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='customer/')),
    url(r'^admin/', admin.site.urls),
  
    
    url(r'^customer/([0-9]+)?$', 'printers.views.report'),
    url(r'^center/([0-9]+)?$', 'printers.views.center'),
    url(r'^report/$', 'printers.views.report_data'),
    url(r'^login$', 'printers.views.login_view'),
    url(r'^logout$', 'printers.views.logout_view'),
    url(r'^report/generatePdf$', 'printers.views.generatePrinterReportPdf'),
    
    url(r'^api/report/center/([0-9]+)?$', 'printers.views.reportByCenter'),
    url(r'^api/report/customer/([0-9]+)$', 'printers.views.reportByCostumer'),
    url(r'^api/report/$', 'printers.views.reportJson'),
    url(r'^api/report/printerReport$', 'printers.views.reporPrinterJson')
    

]
handler404 = 'printers.views._404'
