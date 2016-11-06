from openpyxl import Workbook

def generatePrinterReportXls(data,headers,cols):
	filename = 'file.xlsx'
  	path = "printers/static/download/" + filename
	wb = Workbook()
	ws = wb.active
	ws.title = ' - '.join(headers)
	ws.append(cols)
	for row in data:
		ws.append(row)
	wb.save(filename= path)
	return filename