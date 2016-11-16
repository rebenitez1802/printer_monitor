from openpyxl import Workbook
from openpyxl.styles import PatternFill
from django.conf import settings

def generatePrinterReportXls(data,headers,cols, backgroundStyles=None):
	filename = 'file.xlsx'
  	path = settings.PROJ_PATH + "/printers/static/download/" + filename
  	#print 'generating %s' % path
	wb = Workbook()
	ws = wb.active
	ws.title = (' - '.join(headers))[:30]
	ws.append(cols)

	for row in data:
		ws.append(row)
	
	if backgroundStyles:
		for s in backgroundStyles:
			for c in ws.rows[s[0]]:
				c.fill =PatternFill("solid", fgColor=s[1])
				#print c
	#print 'saving to disk file %s' % path
	try:
		wb.save(filename= path)
	except Exception as e:
		print(type(inst))    # the exception instance
		print(inst.args)     # arguments stored in .args
		print(inst)
	#print 'saved %s' % path
	return filename