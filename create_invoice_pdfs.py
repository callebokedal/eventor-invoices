import argparse
from datetime import date, datetime, timedelta
import pandas as pd # pyright: ignore[reportMissingModuleSource]
import numpy as np # pyright: ignore
from reportlab.pdfgen import canvas  # pyright: ignore
from reportlab.pdfbase.ttfonts import TTFont  # pyright: ignore
from reportlab.pdfbase import pdfmetrics  # pyright: ignore
from reportlab.lib import colors  # pyright: ignore
from reportlab.lib.pagesizes import A4  # pyright: ignore
from reportlab.lib.units import cm  # pyright: ignore
from reportlab.platypus import Table, TableStyle  # pyright: ignore
from pythonlib.rotatedtext import verticalText

# https://stackoverflow.com/questions/13061545/rotated-document-with-reportlab-vertical-text
from reportlab.graphics.shapes import Drawing, Group, String  # pyright: ignore
from reportlab.lib.enums import TA_CENTER  # pyright: ignore
from reportlab.lib.styles import getSampleStyleSheet  # pyright: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph  # pyright: ignore

"""

OBSOLETE - NOT TO BE USED

"""

style = getSampleStyleSheet()
normal = style["Normal"]
normal.alignment = TA_CENTER
normal.fontName = "Helvetica"
normal.fontSize = 15

def test():
    pdf = SimpleDocTemplate("testplatypus.pdf",
                            pagesize=(80, 250),
                            rightMargin=10,
                            leftMargin=10,
                            topMargin=20,
                            bottomMargin=20)
    story = []
    text_lines = ["I really need this to be",
                "wrapped and vertical!"]

    para = Paragraph('Basic text.', normal)
    story.append(para)
    drawing = Drawing(50, 110)
    group = Group()
    group.rotate(-90)
    for i, line in enumerate(text_lines):
        group.add(String(-100, 15*(2-i), line, fontName='Helvetica'))
    drawing.add(group)
    story.append(drawing)
    para2 = Paragraph('More text.', normal)
    story.append(para2)
    #pdf.drawCentredString(30, 30, "Vanlig text")
    pdf.build(story)

#test()

"""Create PDF files for all members

OBSOLETE - NOT USED
"""

today = date.today()

parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str, help="File with calculated invoice data")
parser.add_argument("export_directory", type=str, help="Directory to save result to")
args = parser.parse_args()

def coord(x, y, height, unit=1):
    x, y = x * unit, height - y * unit
    return x, y

# Action

df = pd.read_excel(args.input_file, na_filter=False)
#print(df.columns)
# ['id', 'Text', 'BatchId', 'E-id', 'E-mail', 'E-invoiceNo', 'Person',
#       'Event', 'Klass', 'amount', 'fee', 'lateFee', 'status', 'Ålder', 'OK?',
#       '%', 'Subvention', 'Att betala'],
# Note! Column names was updates by 'parse_data_files.py'
df_pdf = df[['id','E-id','amount','lateFee','status','E-mail','Person','Event','Klass','Ålder','OK?','%','Subvention','Att betala']]

#print(df_pdf)

fileName = 'files/Faktura-nnn.pdf'
documentTitle = 'Faktura'
title = 'Faktura'
subTitle = '2022'
sfkLines = [
    'Sjövalla FK',
    'Organisationsnummer: 852000-3305',
    'Finnsjögården 12',
    '435 41 Mölnlycke',
    'Sverige'
]
sfk_image = 'static_files/sfk_logo_small.png'
sfk_ol_image = 'static_files/sfk-ol-text.png'

# creating a pdf object
pdf = canvas.Canvas(fileName, pagesize=A4)

width, height = A4

# registering a external font in python
pdfmetrics.registerFont(TTFont('arimo', 'static_files/fonts/Arimo-Regular.ttf'))
pdfmetrics.registerFont(TTFont('arimo-bold', 'static_files/fonts/Arimo-Bold.ttf'))
pdfmetrics.registerFont(TTFont('martel', 'static_files/fonts/MartelSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('martel-bold', 'static_files/fonts/MartelSans-Bold.ttf'))


# drawing a image at the 
# specified (x.y) position
# 626 × 186
# 626 × 186
pdf.drawInlineImage(sfk_image, 10, 785, width=48, height=48)
pdf.drawInlineImage(sfk_ol_image, 65, 800, width=102, height=30)

pdf.setFont('arimo', 8)
pdf.drawString(540, 820, f"Sida {1} av {2}")

pdf.setFont('arimo-bold', 26)
# setting the title of the document
pdf.setTitle(documentTitle)

# creating the title by setting it's font 
# and putting it on the canvas
pdf.drawCentredString(300, 770, title)

# creating the subtitle by setting it's font, 
# colour and putting it on the canvas
#pdf.setFillColorRGB(0, 0, 255)
#pdf.setFont("martel", 10)
#pdf.setFont("Courier-Bold", 24)
#pdf.drawCentredString(290, 720, subTitle)

# drawing a line
#pdf.line(30, 710, 550, 710)

# creating a multiline text using
# textline and for loop
# Sjövalla FK
pdf.setFont("arimo-bold", 12)
pdf.drawString(40, 730, "Betalningsmottagare")
pdf.setFont("arimo", 12)
text = pdf.beginText(40, 715)
#text.setFont("Courier", 18)
#text.setFillColor(colors.red)
for line in sfkLines:
    text.textLine(line)
pdf.drawText(text)

# Kund
pdf.setFont("arimo-bold", 12)
pdf.drawString(390, 730, "Kund")
pdf.setFont("arimo", 12)
pdf.drawString(390, 715, "Ett Ganska Långt Namn")

invoice_date = today.isoformat()
due_date = (today + timedelta(days=31)).isoformat()
# print(f"Today: {invoice_date}. Due date: {due_date}") # Works
pdf.drawString(40, 645, f"Fakturadatum: {invoice_date}")

# Invoice info
invoice_info = [["Köp", "Per-Arne Wahlgren"],
    ["Organisation", "Sjövalla FK"],
    ["Bankgiro", "5617-2570"],
    ["Summa att betala", "1 300 SEK"],
    ["Förfallodatum", due_date],
    ["Fakturanummer", "123"]]
pdf.setFont("arimo-bold", 12)
text = pdf.beginText(40, 615)
text.textLines([lines[0] for lines in invoice_info], trim=1)
pdf.drawText(text)

pdf.setFont("arimo-bold", 12)
text = pdf.beginText(290, 615)
#for line in invoice_info:
#    text.textLine(line[1].rjust(30,"_"))
text.textLines([lines[1] for lines in invoice_info], trim=1)
pdf.drawText(text)

pdf.setFont("arimo-bold", 14)
pdf.drawString(40, 515, "Specifikation")

# Draw table heading
def drawTableHeading(x:int,y:int, fontSize:int=9):
    pdf.setFont("arimo-bold", 9)
    pdf.drawString(46,y,"Id")
    pdf.drawString(81,y,"Anmälan / Benämning")
    pdf.drawString(330,y+fontSize+5,"Ej start")
    pdf.drawRightString(332,y,"Kostnad (kr)")
    pdf.drawString(345,y,"Subvention (%)")
    pdf.drawString(370,y+fontSize+5,"Subvention (kr)")
    pdf.drawString(420,y,"Att betala")

drawTableHeading(360,420,9)

data = [['00', '01', '02', '03', '04'],
        ['10', '11', '12', '13', '14'],
        ['20', '21', '22', '23', '24'],
        ['30', '31', '32', '33', '34']]

def get_info(competition:str, klass:str):
    if len(competition) > 40:
        return competition[0:37] + "... " + klass
    return competition + " " + klass

#df_out = df_pdf[(df_pdf['id']==2) & (df_pdf['col3']=='Y') ]
df_out = df_pdf[df_pdf['E-id']==64954].copy() # EA
#df_out = df_pdf[df_pdf['item-id']==65020] # SH
#print(df_out)

#df_pdf = df[['id','item-id','amount','lateFee','status','item-invoiceDetails.e-mail','Person','Tävling','Klass','Ålder','OK?','Subvention %','Subvention','Att betala']]
#df_out['Info'] = df_out.[:,('Tävling')].str.slice(0,30) + ' ' + df_out['Klass']

#df_final['Subvention'] = np.vectorize(calculate_discount_amount)(df_final['amount'],df_final['OK?'],df_final['Subvention %'])
#df_out['Info']         = np.vectorize(get_info)(df_out['Tävling'],df_out['Klass'])
#df_out['Subvention b'] = df_out['Subvention %'].apply(lambda x: str(x) + "%")
df_out['Info']         = np.vectorize(get_info)(df_out['Event'],df_out['Klass'])
df_out['%'] = df_out['%'].apply(lambda x: str(x) + "%")
df_out['status'] = df_out['status'].apply(lambda x: str(x).replace("Ej start","x"))
#df_out.loc[:,'%'] = lambda x: str(x) + "%"
#data = df_out[['id','Info','amount','lateFee','status','Subvention %','Subvention','Att betala']].values.tolist()
data = df_out[['id','Info','amount','lateFee','status','%','Subvention','Att betala']].values.tolist()

# df_final['Att betala'] = np.vectorize(calculate_amount_to_pay)(df_final['amount'],df_final['lateFee'],df_final['Tävling'],df_final['Ålder'],df_final['OK?'],df_final['Subvention %'],df_final['Person'])


#data = [['Test', '01', '02', '03', '04'],
#        ['Testaaaar', '11', '12', '13', '14']]
#t=Table(data, spaceAfter=False, style=STYLE)

rows = len(data)
print(f"Number of records: {rows}")

ts = TableStyle([
    ('VALIGN',(0,0),(-1,-1),'BOTTOM'), # Does not work?
    ('TEXTCOLOR',(0,0),(0,-1),colors.grey),
    ('FONTSIZE',(0,0),(0,-1),7),
    ('ALIGN',(2,0),(-1,-1),'RIGHT')
])
t=Table(data, style=ts, colWidths=[None]*6)
#t=Table(data)

w, h = t.wrap(width, height)

#t.wrapOn(pdf, width+300, height)
t.drawOn(pdf, *coord(40, 0, cm))

# 
pdf.showPage()

pdf.setFont('arimo', 8)
pdf.drawString(540, 820, f"Sida {2} av {2}")

# saving the pdf
pdf.save()