import argparse
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle, Image
from pythonlib.rotatedtext import verticalText
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ParagraphAndImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm, inch, mm
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle


# https://stackoverflow.com/questions/13061545/rotated-document-with-reportlab-vertical-text
from reportlab.graphics.shapes import Drawing, Group, String

"""Create PDF invoice"""

"""
Example: 
python create_pdf.py 123 

"""

width, height = A4
today = date.today()

pdfmetrics.registerFont(TTFont('arimo', 'files/fonts/Arimo-Regular.ttf'))
pdfmetrics.registerFont(TTFont('arimo-bold', 'files/fonts/Arimo-Bold.ttf'))
pdfmetrics.registerFont(TTFont('martel', 'files/fonts/MartelSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('martel-bold', 'files/fonts/MartelSans-Bold.ttf'))

#parser = argparse.ArgumentParser()
#parser.add_argument("pdf_no")
#parser.add_argument("path_out")
#parser.add_argument("")
#parser.add_argument("input_file", type=str, help="File with calculated invoice data")
#parser.add_argument("export_directory", type=str, help="Directory to save result to")
#args = parser.parse_args()

# Common configuration
#fileName = 'files/Faktura-nnn.pdf'
document_title = 'Faktura'
title = 'Faktura'
#subTitle = '2022'
sfk_lines = [
    'Sjövalla FK',
    'Organisationsnummer: 852000-3305',
    'Finnsjögården 12',
    '435 41 Mölnlycke',
    'Sverige'
]
sfk_image = 'files/sfk_logo_small.png'
sfk_text_image = 'files/sfk-ol-text.png'
qr_image = 'files/qr_subventioner_invoice.png'
sfk_contact = [
    'Vid förfrågningar angående denna faktura, kontakta:',
    '&nbsp;',
    'Per-Arne Wahlgren',
    'Telefon: 0708-322148',
    'E-post: per-arne.wahlgren@telia.com'
]

#style = getSampleStyleSheet()
#normal = style["Normal"]
#normal.alignment = TA_CENTER
#normal.fontName = "Helvetica"
#normal.fontSize = 15

def create_pdf_old(data:object):
    print("Creating PDF")
    invoice_date = today.isoformat()
    due_date = (today + timedelta(days=30)).isoformat()

    invoice_info = [["Köp", data["name"]],
        ["Organisation", "Sjövalla FK"],
        ["Bankgiro", "5617-2570"],
        ["Summa att betala", data["total_amount"]],
        ["Förfallodatum", due_date],
        ["Fakturanummer", "123"]]
    return ""

#PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        #print(f"a: {args}")
        #print(f"kw: {kwargs}")
        #print(f"self: {self}")
        if 'data' in kwargs:
            self.data = kwargs['data']
        else:
            self.data = {}
        #args = []
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("arimo", 7)
        #540, 820
        self.drawRightString(540, 820,
            f"Sida {self._pageNumber} av {page_count}")

def myFirstPage(canvas, pdf):
    canvas.saveState()
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('arimo',9)
    #canvas.drawString(cm, 0.75 * cm, f"Sida {doc.page} {canvas.getPageNumber()}")
    canvas.restoreState()

def col(i):
    """Calculate color to pair of altering rows"""
    if i % 2 == 0:
        row_idx = int(i/2)
    else:
        row_idx = int((i+1)/2)

    return colors.white if row_idx % 2 == 1 else HexColor(0xF2F2F2)

class SFKInvoice:
    def __init__(self, *args, **kwargs):
        if 'left_footer' in kwargs:
            self.left_footer = kwargs['left_footer']
        else:
            self.left_footer = None
        if 'footer' in kwargs:
            self.footer = kwargs['footer']
        else:
            self.footer = "Sjövalla Orientering - orientering.sjovalla.se"
        if 'data' in kwargs:
            self.data = kwargs['data']
            self.filename = f"files/pdfs/Faktura-{self.data['invoice_no']}.pdf"
        else:
            self.data = {}
            self.filename = f"files/pfds/Faktura-exempel.pdf"
        
        self.doc = SimpleDocTemplate(self.filename, pagesize=A4,
                                     topMargin = 1 * cm, bottomMargin = 2 * cm,
                                     leftMargin = 1 * cm, rightMargin = 1 * cm)
        self.Story = []

        self.generateReport(self.data)

    def onMyFirstPage(self, canvas, doc):
        # If the left_footer attribute is not None, then add it to the page
        canvas.saveState()
        data = self.data
        if self.left_footer is not None:
            canvas.setFont('arimo', 8)
            canvas.drawString(1 * cm, 1 * cm, self.left_footer)
        if self.footer is not None:
            canvas.setFont('arimo', 8)
            canvas.drawCentredString(width/2, 1*cm, self.footer)
            
        #print(f"total amount: {canvas.data}")
        canvas.saveState()
        # Logos
        #canvas.drawInlineImage(sfk_image, 10, 785, width=48, height=48)
        #canvas.drawInlineImage(sfk_text_image, 65, 800, width=102, height=30)
        canvas.drawInlineImage(sfk_image, 40, 770, width=48, height=48)
        canvas.drawInlineImage(sfk_text_image, 95, 785, width=102, height=30)

        canvas.setFont('arimo-bold', 26)
        canvas.setTitle(title)
        canvas.drawCentredString(300, 770, title)
        
        #canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, document_title)

        canvas.setFont("arimo-bold", 12)
        canvas.drawString(40, 730, "Betalningsmottagare")
        canvas.setFont("arimo", 12)
        text = canvas.beginText(40, 715)
        for line in sfk_lines:
            text.textLine(line)
        canvas.drawText(text)

        # Kund
        name = self.data["name"]
        canvas.setFont("arimo-bold", 12)
        canvas.drawString(390, 730, "Kund")
        canvas.setFont("arimo", 12)
        canvas.drawString(390, 715, name)

        invoice_date = today.isoformat()
        due_date = (today + timedelta(days=31)).isoformat()
        # print(f"Today: {invoice_date}. Due date: {due_date}") # Works
        canvas.drawString(40, 637, f"Fakturadatum: {invoice_date}")

        # Invoice info
        invoice_info = [["Köp", name],
            ["Organisation", "Sjövalla FK"],
            ["Bankgiro", "5617-2570"],
            ["Summa att betala", f"{str(data['total_amount'])} kr"],
            ["Förfallodatum", due_date + " (30 dagar)"],
            ["Fakturanummer", str(data["invoice_no"])]]
        canvas.setFont("arimo-bold", 12)
        text = canvas.beginText(40, 615)
        text.textLines([lines[0] for lines in invoice_info], trim=1)
        canvas.drawText(text)

        canvas.setFont("arimo-bold", 12)
        text = canvas.beginText(290, 615)
        #for line in invoice_info:
        #    text.textLine(line[1].rjust(30,"_"))
        text.textLines([lines[1] for lines in invoice_info], trim=1)
        canvas.drawText(text)

        canvas.setFont("arimo-bold", 14)
        #canvas.drawString(40, 515, "Specifikation")
        canvas.drawCentredString(300, 510, "Specifikation")

        canvas.restoreState()
        canvas.restoreState()

    def onMyLaterPages(self, canvas, doc):
        # If the left_footer attribute is not None, then add it to the page
        canvas.saveState()
        if self.left_footer is not None:
            canvas.setFont('arimo', 8)
            canvas.drawString(1 * cm, 1 * cm, self.left_footer)
        if self.footer is not None:
            canvas.setFont('arimo', 8)
            canvas.drawCentredString(width/2, 1*cm, self.footer)
        canvas.restoreState()

    def generateReport(self, data):
        print("Generation report:", data["invoice_no"], data["name"])
        self.reportContent(data)
        self.doc.build(self.Story, canvasmaker=NumberedCanvas, 
                       onFirstPage=self.onMyFirstPage,
                       onLaterPages=self.onMyLaterPages)
        print(f"Saved as '{self.filename}'")

    def reportContent(self, data):
        print("Report content: ", data["invoice_no"], data["name"])
        """Creates PDF content"""
        #styles = getSampleStyleSheet()
        #for i in range(15):
        #    self.Story.append(Paragraph(txt))

        #pdf = SimpleDocTemplate("files/Faktura-exempel.pdf", data=d)
        story = self.Story
        story = [Spacer(1,10.5*cm)]
        style = styles["Normal"]

        #invoice = data
        #print(f"invoice data: {invoice}")
        invoice_date = today.isoformat()
        due_date = (today + timedelta(days=30)).isoformat()

        #print(data["rows"])
        items = [['Id', 'Benämning', 'Antal', 'Status', 'Pris', 'E.avg*', 'Subvention', 'Justering**', 'Belopp']]
        # TODO: Get from Excel instead?
        totalt_pris = 0 # Pris + Efteranmälningsavgift
        for row in data["rows"]:
            #print(row)
            items.append([row["id"], row["text"]])
            items.append(['', '', '1', row["status"], str(row["amount"])+ " kr", str(row["late_fee"])+ " kr", "("+ str(row["%"]) + "%) " + str(row["discount"]) + " kr",str(row["adjustment"]) + " kr", str(row["to_pay"]) + " kr"])
            #totalt_belopp += row["to_pay"]
            totalt_pris += row["amount"] + row["late_fee"]

        # TODO Justeringar!!!

        #exit(1)

        data4 = [['Id', 'Benämning', 'Antal', 'Status', 'Pris', 'Subvention', 'Belopp'],
             ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
             ['', '', '1', 'Ej start', '14 kr', '(40%) 140 kr', '0 kr']]

        # Add Invoice specification as a table
        t=Table(items,colWidths=[None,6*cm, None],
            style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('BACKGROUND',(0,0),(-1,0),HexColor(0x3f9049)),
                    ('FONTNAME',(0,0),(-1,-1),'arimo'),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                    ('ALIGN',(2,1),(3,-1),'CENTER'), # Antal, Ej start
                    ('ALIGN',(4,1),(-1,-1),'RIGHT') # 
                    ], repeatRows=1, spaceBefore=0.5*cm, spaceAfter=0.5*cm)

        for i in range(1,len(items)):
            if i % 2 == 0:
                idx = i + (i-1)
                ts = TableStyle([
                    #('SIZE',(0,i),9),
                    ('SPAN',(0,i),(1,i)),
                    ('BACKGROUND',(0,i),(-1,i), col(i))])
            else:
                ts = TableStyle([
                    ('SPAN',(1,i),(-1,i)),
                    ('BACKGROUND',(0,i),(-1,i), col(i))])
            t.setStyle(ts)

        story.append(t)

        # Add summary to pay
        #self.canvas.setFont("arimo-bold", 12)
        # https://docs.reportlab.com/reportlab/userguide/ch6_paragraphs/

        style1 = ParagraphStyle(
            name='Normal',
            fontName='arimo',
            fontSize=12,
            alignment= TA_RIGHT,
            rightIndent = 1*cm
        )
        style2 = ParagraphStyle(
            name='Normal',
            fontName='arimo-bold',
            fontSize=12,
            alignment= TA_RIGHT,
            rightIndent = 1*cm
        )
        #style.fontName = "arimo-bold"
        #style.alignment = TA_RIGHT
        p = Paragraph(f"*) 'E.avg' = Efteranmälningsavgift", style)
        story.append(p)
        p = Paragraph(f"**) Eventuell manuell justering", style)
        story.append(p)
        p = Paragraph(f"Summa pris: {totalt_pris} kr", style1)
        story.append(p)
        p = Paragraph(f"Avdrag subventioner: {-data['total_discount']} kr", style1)
        story.append(p)
        p = Paragraph(f"Justeringar: {data['total_adjustment']} kr", style1)
        story.append(p)
        print(f"Att betala '{data['total_amount']}' == pris '{totalt_pris}' - subv {data['total_discount']} + just. {data['total_adjustment']}")
        assert data['total_amount'] == totalt_pris - data['total_discount'] + data['total_adjustment']
        #p = Paragraph(f"Summa belopp: {data['total_discount']} kr", style1)
        #story.append(p)
        story.append(Spacer(1, 0.5*cm))
        #style.rightIndent = 1*cm
        #style.fontSize = 12
        p = Paragraph(f"Summa att betala: {data['total_amount']} kr", style2)
        story.append(p)
        story.append(Spacer(1, 0.5*cm))

        style = ParagraphStyle(
            name='Normal',
            fontName='arimo',
            fontSize=10,
        )
        p = Paragraph(f"Var god betala var faktura för sig. Märk aktuell faktura med text: {data['invoice_no']} {data['name']}", style)
        story.append(p)
        p = Paragraph(f"Tack för hjälpen!", style)
        story.append(p)

        story.append(Spacer(1, 1*cm))

        #style2 = styles["Normal2"]
        #style.fontName = "arimo"
        #style2.alignment = TA_LEFT
        #style.rightIndent = 0
        #style.fontSize = 10
        for line in sfk_contact:
            p = Paragraph(line, style)
            story.append(p)

        # Rules
        story.append(Spacer(1,0.5*cm))
        p = Paragraph("Information om subventioner: https://orientering.sjovalla.se/s/subventioner", style)
        story.append(p)
        story.append(Spacer(1,0.5*cm))

        # Set the story
        self.Story = story

if False:
    data = {
        "invoice_no": 777,
        "name": "Testare Testsson",
        "rows": [
            {"id":"1", "text":"Anmälan 1", "amount":345, "lateFee": 40, "%":100, "discount": 345},
            {"id":"2", "text":"Anmälan 2", "amount":345, "lateFee": 40, "%":100, "discount": 345},
            {"id":"3", "text":"Anmälan 3", "amount":345, "lateFee": 40, "%":100, "discount": 345},
            {"id":"ref1", "text":"Justering #1", "amount":100},
            {"id":"ref3", "text":"Justering #3", "amount":-200}
        ],
        "total_discount": 234,
        "total_amount": 1234
    }


#inv = SFKInvoice(left_footer="Testing", data=data)
#inv = SFKInvoice(footer="Sjövalla Orientering - orientering.sjovalla.se", data=data)

# Working
#inv = SFKInvoice(data=data)
#inv.generateReport(data=data)

if False:
    exit(0)

    #for i in range(1,13):
    #    print(col(i))
    #exit(0)

    def create_pdf(data:object):
        d = {"test":True}
        pdf = SimpleDocTemplate("files/Faktura-exempel.pdf", data=d)
        story = [Spacer(1,9*cm)]
        style = styles["Normal"]

        invoice = data["invoice"]
        invoice_date = today.isoformat()
        due_date = (today + timedelta(days=30)).isoformat()

        if False:
            invoice_info = [["Köp", invoice["name"]],
                ["Organisation", "Sjövalla FK"],
                ["Bankgiro", "5617-2570"],
                ["Summa att betala", invoice["total_amount"]],
                ["Förfallodatum", due_date],
                ["Fakturanummer", "123"]]
            t = Table(invoice_info)
            story.append(t)

        #for a,b in invoice_info:
        #    p = Paragraph(a, style)
        #    story.append(p)

        data3 =  [['Id', 'Benämning', 'Antal', 'Ej start', 'Pris', 'Subvention', 'Belopp'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(100 %) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(100 %) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(100 %) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'B Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr'],
                ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
                ['', '', '1', 'X', '14 kr', '(40%) 140 kr', '0 kr']]

        #for i in range(1,len(data3)):
        #    data3[i][0] = i

        t=Table(data3,colWidths=[None,8*cm, None],
            style=[
                    #('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    #('BACKGROUND',(0,0),(-1,0),colors.palegreen),
                    ('BACKGROUND',(0,0),(-1,0),HexColor(0x3f9049)),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                    #('TEXTCOLOR',(3,1),(3,-1),colors.red),
                    ('ALIGN',(2,1),(3,-1),'CENTER'), # Antal, Ej start
                    ('ALIGN',(4,1),(-1,-1),'RIGHT') # 
                    #('BOX',(0,0),(-1,-1),1,colors.black),
                    #('SPAN',(1,1),(-1,1)),
                    #('BACKGROUND',(-2,-2),(-1,-1), colors.pink),
                    ], repeatRows=1, spaceBefore=0.5*cm, spaceAfter=0.5*cm)

        #print(f"data length: {len(data3)}")

        #bg = 'A'
        for i in range(1,len(data3)):
            #idx = i + (i-1)
            #print(f"idx: {str(idx).rjust(2)}, i: {str(i).rjust(2)}, mod: {str(i % 2).rjust(1)} => {idx-1}-{idx}")
            #print(f"i: {str(i).rjust(2)}, mod: {str(i % 2).rjust(1)} {str(i).rjust(2)} {str(col(i)).rjust(1)} {data3[i]}")
            # SPAN, (sc,sr), (ec,er)
            if i % 2 == 0:
                idx = i + (i-1)
                #print(f"idx: {str(idx).rjust(2)}, mod: {idx%3}")
                ts = TableStyle([
                    #('SIZE',(0,i),9),
                    ('SPAN',(0,i),(1,i)),
                    ('BACKGROUND',(0,i),(-1,i), col(i))])
            else:
                ts = TableStyle([
                    ('SPAN',(1,i),(-1,i)),
                    ('BACKGROUND',(0,i),(-1,i), col(i))])
            #print(f"   idx: {i} => {bg}\n")
            t.setStyle(ts)


    #    for i in range(1,len(data3)):
    #        idx = i + (i-1)
    #        print(f"idx: {str(idx).rjust(2)}, i: {str(i).rjust(2)}, mod: {str(i % 2).rjust(1)} => {idx-1}-{idx}")
    #        if i % 2 == 0:
    #            bc = colors.white
    #            bc = HexColor(0xF5F5F5)
    #            bc = colors.pink
    #            #bc = Color(100,100,100,0.9)
    #            ts = TableStyle([
    #                #('BACKGROUND', (idx-1,0),(-1,idx-1), bc),
    #                ('SPAN',(1,1),(-1,1)),
    #
    #                #('BACKGROUND', (idx,0),(-1,idx), bc),
    #                ('SPAN',(1,1),(-1,1))
    #                ])
    #            t.setStyle(ts)
    #        else:
    #            #bc = colors.pink
    #            bc = HexColor(0xF5F5F5)
    #            #bc = colors.pink
    #            ts = TableStyle([
    #                ('BACKGROUND', (0,i),(-1,i), bc),
    #                ('SPAN',(1,1),(-1,1)),
    #
    #                ('BACKGROUND', (0,i+1),(-1,i+1), bc),
    #                ('SPAN',(1,1),(-1,1))
    #                ])
    #            #t.setStyle(ts)

            # (from_row, from_col), (to_row, to_col)
            # (0,0)   top left
            # (-1,-1) bottom right
            #idx=idx-1
        story.append(t)

        if False:
            num_rows = 5
            num_columns = 40
            matrix = [[ 3 for j in range(num_rows)] for i in range(num_columns)]
            t = Table(matrix)
            t.setStyle(TableStyle([('BACKGROUND',(1,1),(-2,-2),Color(153,3,56,0.1)),
                                    ('TEXTCOLOR',(0,0),(1,-1),colors.red)]))
            story.append(t)

        # Add summary to pay
        p = Paragraph(f"Summa att betala: {data['invoice']['total_amount']}", style)
        story.append(p)
        story.append(Spacer(1, 3.2*cm))

        # Close up

        if False:
            for i in range(30):
                bogustext = (f"This is Paragraph number {i}. ") *20
                p = Paragraph(bogustext, style)
                story.append(p)
                story.append(Spacer(1, 3.2*cm))

        #pdf.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages, canvasmaker=NumberedCanvas(), data=data)
        #pdf.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages, canvasmaker=NumberedCanvas)

    #data = {
    #    "invoice_no": 123,
    #    "invoice": {
    #        "name": "Testare Testsson",
    #        "rows": [
    #            {"id":"1", "text":"Anmälan 1", "amount":345, "lateFee": 40, "%":100, "discount": 345},
    #            {"id":"2", "text":"Anmälan 2", "amount":345, "lateFee": 40, "%":100, "discount": 345},
    #            {"id":"3", "text":"Anmälan 3", "amount":345, "lateFee": 40, "%":100, "discount": 345},
    #            {"id":"ref1", "text":"Justering #1", "amount":100},
    #            {"id":"ref3", "text":"Justering #3", "amount":-200}
    #        ],
    #        "total_discount": 234,
    #        "total_amount": 1234
    #    }
    #}

    #create_pdf(data)






