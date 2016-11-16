from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch, landscape
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet
 
def generatePrinterReport(data,headers, aditionalStyles = None):
  filename = 'pdf.pdf'
  path = "printers/static/download/" + filename

  doc = SimpleDocTemplate(path, pagesize=landscape(letter))
  # container for the 'Flowable' objects
  elements = []
   
  styleSheet = getSampleStyleSheet()
  
  I = Image('printers/static/images/ixon-logo.png')
  #I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
  #I.drawWidth = 1.25*inch
  header = [[I],headers]
  th = Table(header,hAlign='LEFT', style = [('SPAN',(0,0),(2,0)),('BOX',(0,0),(-1,-1),2,colors.black)])
  style = [
                      ('BOX',(0,0),(-1,-1),2,colors.black),
                      ('GRID',(0,0),(-1,-1),0.5,colors.black),
                      ('FONTSIZE', (0,0),(-1,-1,), 8),
                      ('ALIGN',(0,0),(-1,-1),'CENTER'),
                      #('BACKGROUND',(-1,0),(-1,-1),colors.red),
                      #('BACKGROUND',(0,0),(0,-1),colors.red)
  ]
  if aditionalStyles:
    style = style + aditionalStyles

  t=Table(data,style=style)
  elements.append(th)
  elements.append(Table([['  ','Reporte con mas de 7 dias'],[[]],['  ','No hay Reporte Valido Disponible']],hAlign='RIGHT', style=[('BACKGROUND',(0,0),(0,0),colors.yellow),('BACKGROUND',(0,2),(0,2),colors.red)]))
  elements.append(Spacer(0.5*inch,0.5*inch))
  elements.append(t)
  # write the document to disk
  doc.build(elements)
  return filename


def samplePdf(): 
  doc = SimpleDocTemplate("complex_cell_values.pdf", pagesize=letter)
  # container for the 'Flowable' objects
  elements = []
   
  styleSheet = getSampleStyleSheet()
   
  I = Image('/opt/apps/printer-monitor_env/printer_monitor/printers/static/images/ixon-logo.png')
  I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
  I.drawWidth = 1.25*inch
  P0 = Paragraph('''
                 <b>A pa<font color=red>r</font>a<i>graph</i></b>
                 <super><font color=yellow>1</font></super>''',
                 styleSheet["BodyText"])
  P = Paragraph('''
      <para align=center spaceb=3>The <b>ReportLab Left
      <font color=red>Logo</font></b>
      Image</para>''',
      styleSheet["BodyText"])
  data= [['A', 'B', 'C', P0, 'D'],
         ['00', '01', '02', [I,P], '04'],
         ['10', '11', '12', [P,I], '14'],
         ['20', '21', '22', '23', '24'],
         ['30', '31', '32', '33', '34']]
   
  t=Table(data,style=[
                      
                      ('BOX',(0,0),(-1,-1),2,colors.black),
                      ('GRID',(0,0),(-1,-1),0.5,colors.black),
                     
                      ('ALIGN',(0,0),(-1,-1),'CENTER'),
                      
  ])
  t._argW[3]=1.5*inch
   
  elements.append(t)
  # write the document to disk
  doc.build(elements)
