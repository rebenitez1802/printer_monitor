from openpyxl import Workbook
from openpyxl.styles import PatternFill
def generatePrinterReportXls(data,headers,cols, backgroundStyles=None):
	filename = 'file.xlsx'
  	path = "printers/static/download/" + filename
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
	
	wb.save(filename= path)
	return filename