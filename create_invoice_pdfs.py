import argparse
from datetime import date
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

"""Create PDF files for all members"""


today = date.today()

parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str, help="File with calculated invoice data")
parser.add_argument("export_directory", type=str, help="Directory to save result to")
args = parser.parse_args()

df = pd.read_excel(args.input_file, na_filter=False)
df_pdf = df[['id','item-id','amount','lateFee','status','item-invoiceDetails.e-mail','Person','Tävling','Klass','Ålder','OK?','Subvention %','Subvention','Att betala']]

# Action
#print(df_pdf)

fileName = 'Faktura-nnn.pdf'
documentTitle = 'Faktura'
title = 'Faktura'
subTitle = '2022'
sfkLines = [
    'Sjövalla FK',
    'Finnsjögården 12',
    '435 41 Mölnlycke',
    'Sverige'
]
image = 'files/sfk-ol-and-logo.png'

# creating a pdf object
pdf = canvas.Canvas(fileName, pagesize=A4)

width, height = A4

# registering a external font in python
pdfmetrics.registerFont(TTFont('arimo', 'files/fonts/Arimo-Regular.ttf'))
pdfmetrics.registerFont(TTFont('arimo-bold', 'files/fonts/Arimo-Bold.ttf'))
pdfmetrics.registerFont(TTFont('martel', 'files/fonts/MartelSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('martel-bold', 'files/fonts/MartelSans-Bold.ttf'))

pdf.setFont('arimo-bold', 26)

# drawing a image at the 
# specified (x.y) position
# 626 × 186
# 626 × 186
pdf.drawInlineImage(image, 10, 785, width=156, height=46)

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

invoice_date = "2022-12-14"
pdf.drawString(40, 645, f"Fakturadatum              {invoice_date}")

# Invoice info
invoice_info = [["Köp", "Per-Arne Wahlgren"],
    ["Organisation", "Sjövalla FK"],
    ["Bankgiro", "5617-2570"],
    ["Summa att betala", "1 300 SEK"],
    ["Förfallodatum", "2023-01-10"],
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

def coord(x, y, height, unit=1):
    x, y = x * unit, height - y * unit
    return x, y

STYLE = TableStyle([
    ('TEXTCOLOR',(0,0),(1,-1),colors.red)
])
data = [['00', '01', '02', '03', '04'],
        ['10', '11', '12', '13', '14'],
        ['20', '21', '22', '23', '24'],
        ['30', '31', '32', '33', '34']]

def get_info(competition:str, klass:str):
    if len(competition) > 40:
        return competition[0:37] + "... " + klass
    return competition + " " + klass

#df_out = df_pdf[(df_pdf['id']==2) & (df_pdf['col3']=='Y') ]
df_out = df_pdf[df_pdf['item-id']==64954] # EA
#df_out = df_pdf[df_pdf['item-id']==65020] # SH
print(df_out)

#df_pdf = df[['id','item-id','amount','lateFee','status','item-invoiceDetails.e-mail','Person','Tävling','Klass','Ålder','OK?','Subvention %','Subvention','Att betala']]
#df_out['Info'] = df_out.[:,('Tävling')].str.slice(0,30) + ' ' + df_out['Klass']
df_out['Info'] = np.vectorize(get_info)(df_out['Tävling'],df_out['Klass'])
df_out['Subvention b'] = df_out['Subvention %'].apply(lambda x: str(x) + "%")
data = df_out[['id','Info','amount','lateFee','status','Subvention %','Subvention','Att betala']].values.tolist()

#data = [['Test', '01', '02', '03', '04'],
#        ['Testaaaar', '11', '12', '13', '14']]
#t=Table(data, spaceAfter=False, style=STYLE)
t=Table(data, style=STYLE)
t=Table(data)

w, h = t.wrap(width, height)

t.wrapOn(pdf, width, height)
t.drawOn(pdf, *coord(40, 0, cm))

# saving the pdf
pdf.save()