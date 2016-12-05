from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch, landscape
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
def generatePrinterReport(data, showAlerts=False):
  filename = 'pdf.pdf'
  path = settings.PROJ_PATH + "/printers/static/download/" + filename
  #print 'Generating File %s' % path
  doc = SimpleDocTemplate(path, rightMargin=10,
                                leftMargin=10,
                                topMargin=25,
                                bottomMargin=72,
                                pagesize=landscape(letter))
                                
  # container for the 'Flowable' objects
  elements = []
   
  styleSheet = getSampleStyleSheet()
  
  I = Image(settings.PROJ_PATH + '/printers/static/images/ixon-logo.png')
  I2 = Image(settings.PROJ_PATH + '/printers/static/images/red-suqare25.png')
  I3 = Image(settings.PROJ_PATH + '/printers/static/images/yellow-square25.png')
  #I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
  #I.drawWidth = 1.25*inch
  header = [['Informe Mensual Recuento de Paginas','','','',I]]
  if showAlerts:
    header.append([I3,'Reporte con mas de 7 dias','','',''])
    
    header.append([I2,'No hay Reporte Valido Disponible','','',''])
  
    
  th1 = Table(header,style=[
    ('ALIGN',(1,0),(1,0),'RIGHT'), 
    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold'),
    ('ALIGN',(0,1),(0,-1),'RIGHT'), 
    ('FONTSIZE', (0,0),(0,0), 26),
    ('SPAN',(-1,0),(-1,-1)),
    ('SPAN',(0,0),(1,0)),
    ('VALIGN',(1,0),(1,-1),'MIDDLE'),
    ('TOPPADDING', (0,0),(0,-1), 10),
    ('BOTTOMPADDING', (0,0),(0,-1), 10)
    
    ]
  #,colWidths=[doc.width/6]*6)
  )
  #th2 = Table(headers,hAlign='LEFT', style = [('SPAN',(0,0),(2,0)),('BOX',(0,0),(-1,-1),2,colors.black)])
  
  
  

  
  elements.append(th1)
  #elements.append(th2)
  

  for tt,styles in data:
    t=Table(tt,style=styles, colWidths=[doc.width/len(tt[0])]*len(tt[0]))
    elements.append(Spacer(0.5*inch,0.5*inch))
    elements.append(t)
  # write the document to disk
  #print 'Building File %s' % path
  try:
    doc.build(elements)
  except Exception as e:
    print(type(e))    # the exception instance
    print(e.args)     # arguments stored in .args
    print(e)

  #print 'Returning %s' % filename
  return filename


def samplePdf(): 
  doc = SimpleDocTemplate("complex_cell_values.pdf", pagesize=letter)
  # container for the 'Flowable' objects
  elements = []
   
  styleSheet = getSampleStyleSheet()
   
  I = Image(settings.PROJ_PATH +'/printers/static/images/ixon-logo.png')
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
