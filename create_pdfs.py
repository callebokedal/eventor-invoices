import argparse
from datetime import date, datetime, timedelta
from pythonlib.SFKInvoice import SFKInvoice
import pandas as pd

"""Create PDF files for all members"""

#today = date.today()

parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str, help="File with calculated invoice data")
#parser.add_argument("export_directory", type=str, help="Directory to save result to")
args = parser.parse_args()

def shorten_text(text:str):
    """Make short text is not too long"""
    if len(text) > 95:
        return text[0:92] + "... "
    return text

# Action
xls = pd.ExcelFile(args.input_file)
df1 = pd.read_excel(xls, 'Aktivitetsöversikt')
df2 = pd.read_excel(xls, 'Fakturaöversikt')
#df1 Index(['id', 'Text', 'BatchId', 'E-id', 'E-mail', 'E-invoiceNo', 'Person',
#       'Event', 'Klass', 'amount', 'fee', 'lateFee', 'status', 'Ålder', 'OK?',
#       '%', 'Subvention', 'Att betala', 'Justering', 'Notering'],
#      dtype='object')
#df2 Index(['Fakturanummer', 'Person', 'Subvention (kr)', 'Justering (kr)',
#       'Totalt att betala (kr)', 'Fakturanamn', 'E-post', 'Faktura skickad',
#       'Faktura betald', 'Notering'],
#      dtype='object')

df = pd.merge(df1,df2,on="Person", suffixes=("_a","_f"))
g = df.groupby("Person")

data = []
#data.append[['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', '']]

# Loop all rows
for index, rows in g:
    #print(type(rows))
    #print(rows.columns)
    #print(type(rows["Person"]))
    #for idx, value in rows.items():
    #    print(value)
    #print(rows["Person"])
    #print("person namn:", rows["Person"].iloc[0])
    #print("person E-invoiceNo:", rows["E-invoiceNo"].iloc[0])
    #print("total_amount",  rows["Totalt att betala (kr)"].iloc[0])

#    data3 = [['Id', 'Benämning', 'Antal', 'Status', 'Pris', 'Subvention', 'Belopp'],
#            ['1234', 'A Anmälan för XXXXXXXXX YYYYYYYYYYY i DM, D20', '', '', '', '', ''],
#            ['', '', '1', 'Ej start', '14 kr', '(40%) 140 kr', '0 kr']]
    person = {
        "invoice_no": rows["Fakturanummer"].iloc[0],
        "name": rows["Person"].iloc[0],
        "e-mail": rows["E-mail"].iloc[0],
        "rows": [],
        "total_discount": rows["Subvention (kr)"].iloc[0],
        "total_adjustment": rows["Justering (kr)"].iloc[0],
        "total_amount": rows["Totalt att betala (kr)"].iloc[0],
        "note": rows["Notering_f"].iloc[0]
    }
    #print(person)
#df1 Index(['id', 'Text', 'BatchId', 'E-id', 'E-mail', 'E-invoiceNo', 'Person',
#       'Event', 'Klass', 'amount', 'fee', 'lateFee', 'status', 'Ålder', 'OK?',
#       '%', 'Subvention', 'Att betala', 'Justering', 'Notering'],
    for idx, row in rows.iterrows():
        #print(row["id"])
        r = {"id":row["id"], 
            "text": shorten_text(row["Text"]), 
            "amount": row["amount"], 
            "late_fee": row["lateFee"], 
            "status": row["status"], 
            "%": row["%"], 
            "discount": row["Subvention"], 
            "to_pay": row["Att betala"],
            "adjustment": row["Justering"],
            "note": row["Notering_a"]}
        person["rows"].append(r)
    data.append(person)
    #print(person)
    #for row in rows:
    #    print(row)

#print(data)
idx = 0
for invoice in data:
    idx += 1
    if idx < 10000:
        inv = SFKInvoice(data=invoice)
        print(invoice["invoice_no"], invoice["name"], invoice["total_amount"])
        