import re
import json
import argparse
import pandas as pd
import numpy as np
from datetime import date

"""Convert report files from Eventor/OL-molnet into usable data-files (invoice details)"""

today = date.today()

parser = argparse.ArgumentParser()
parser.add_argument("data_file", type=str, help="File to read input from (JSON-lines with invoice data)")
parser.add_argument("member_file", type=str, help="File with Member details exported from Eventor")
parser.add_argument("out_file", type=str, help="File to save result to")
args = parser.parse_args()

def read_file(path, encoding='utf-8'):
    with open(path, 'rb') as f:
        data = f.read()
        if encoding is None:
            return data
        return data.decode(encoding)

def formatJSON(o):
    if isinstance(o, datetime):
        return str(o)
    else:
        return o.__dict__

def pretty_json(json_data):
    return json.dumps(json_data, default=formatJSON, indent=4)

def parse_data(filename:str):
    idx = 0
    data = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            idx +=1
            if True or idx < 10:
                line_data = json.loads(line)
                # print(pretty_json(line_data['items']))
                data.append(line_data)
    return data
    
def extract_person_name(text:str):
    """Get name out of invoice text. Two alternatives:
    
    - "Anmälan för <name|[team]> i <competition info>", or variants of this
    - "Hyrbricka SportIdent för <name>" (name always at the end)
    
    """
    # Catch pattern 1
    # Anmälan för <Name> i SM, sprint - D20 Kval B
    match = re.search(r"^Anmälan för ([a-zåäöé -]*?) i ", text, re.IGNORECASE)
    if match != None:
        return match.group(1)

    # Catch pattern 2
    # Anmälan för <Name>, <Team name> i SM, sprint - D20 Kval B
    match = re.search(r"^Anmälan för ([a-zåäöé -]*?), ", text, re.IGNORECASE)
    if match != None:
        return match.group(1)

    # Catch pattern 3 (only valid option left)
    # 1. Fältlunch - Pasta och köttfärsås (85 SEK) för <Name>
    # "Anything" för <Name>
    match = re.search(r" för ([a-zåäöé -]*)$", text, re.IGNORECASE)
    if match != None:
        return match.group(1)

    print(text)
    raise "No match found"


assert extract_person_name("Anmälan för Ett Namn, Sjövalla FK 1 i Daladubbeln, stafett  - D16") == "Ett Namn"
assert extract_person_name("Anmälan för Ett Annat Namn, Göteborg-Majorna OK / IFK Göteborg Orientering / Kungälvs OK / OK Landehof / Sjövalla FK 5 i 25manna - 25manna") == "Ett Annat Namn"

def extract_competition(competition_details:str):
    """Remove class info from competition details"""

    # Special case
    if re.search(r"fältlunch|fältmåltid", competition_details, re.IGNORECASE) != None:
        return competition_details

    res = re.split(" - ", competition_details)
    return " - ".join(res[:-1]) if len(res) > 1 else competition_details

assert extract_competition("Aleträffen - H40") == "Aleträffen"
assert extract_competition("Snötrampen - Insk. 2 km") == "Snötrampen"
assert extract_competition("Vårserien, #2 - Insk. 2 km") == "Vårserien, #2"
assert extract_competition("Midsommarsprinten - Göteborg Syd - Röd") == "Midsommarsprinten - Göteborg Syd"
assert extract_competition("Hyrbricka SportIdent för Ett Namn") == "Hyrbricka SportIdent för Ett Namn"
assert extract_competition("1. Fältlunch - Pasta och köttfärsås (85 SEK) för Ett Namn") == "1. Fältlunch - Pasta och köttfärsås (85 SEK) för Ett Namn"


def extract_class(competition_details:str):
    """Extract class info from competition details"""

    # Special case
    if re.search(r"fältlunch|fältmåltid", competition_details, re.IGNORECASE) != None:
        return ""

    res = re.split(' - ', competition_details)
    return str(res[-1]) if len(res) > 1 else ""

assert extract_class("Vårserien, #2 - Insk. 2 km") == "Insk. 2 km"
assert extract_class("Aleträffen - H40") == "H40"
assert extract_class("Midsommarsprinten - Göteborg Syd - Röd") == "Röd"
assert extract_class("Hyrbricka SportIdent för Ett Namn") == ""
assert extract_class("1. Fältlunch - Pasta och köttfärsås (85 SEK) för Ett Namn") == ""

def extract_competition_details(text:str):
    """Extract competition name"""
    valid_entry = re.search(r"^Anmälan för ", text, re.IGNORECASE) != None
    if not valid_entry:
        return text.replace("Card Rental", "Hyrbricka SportIdent")
    
    name = extract_person_name(text)
    pattern = f"^Anmälan för {name} i "
    remaining = re.sub(pattern, "", text)
    if remaining.startswith("Anmälan"):
        # Case 
        # Anmälan för <Name>, <Team name> i SM, sprint - D20 Kval B
        res = re.split(', ', text)
        return ", ".join(res[1:])
    return remaining

assert extract_competition_details("Anmälan för Ett Namn, Sjövalla FK 1 i Daladubbeln, stafett  - D16") == "Sjövalla FK 1 i Daladubbeln, stafett  - D16"
assert extract_competition_details("Anmälan för Ett Annat Namn, Göteborg-Majorna OK / IFK Göteborg Orientering / Kungälvs OK / OK Landehof / Sjövalla FK 5 i 25manna - 25manna") == "Göteborg-Majorna OK / IFK Göteborg Orientering / Kungälvs OK / OK Landehof / Sjövalla FK 5 i 25manna - 25manna"
assert extract_competition_details("Anmälan för Ett Annat Namn, Sjövalla FK 1 i 25manna - 25manna") == "Sjövalla FK 1 i 25manna - 25manna"
assert extract_competition_details("Anmälan för Ett Namn i Snötrampen - Insk. 2 km") == "Snötrampen - Insk. 2 km"
assert extract_competition_details("Anmälan för Ett Namn i Vårserien, #2 - Insk. 2 km") == "Vårserien, #2 - Insk. 2 km"
assert extract_competition_details("Anmälan för Ett Namn i Aleträffen - H40") == "Aleträffen - H40"
assert extract_competition_details("Hyrbricka SportIdent för Ett Namn") == "Hyrbricka SportIdent för Ett Namn"
assert extract_competition_details("Card Rental för Ett Namn") == "Hyrbricka SportIdent för Ett Namn"


def valid_entry(text:str, status:str, competition:str):
    """Test if entry is valid or not. Not the same as valid for discount (but the first check)
    
    Not valid if:
    - Status: "Ej start"
    - 
    """
    no_start = re.search(r"ej start", status, re.IGNORECASE) != None
    if no_start:
        return False
    
    valid_entry = re.search(r"^Anmälan för ", text, re.IGNORECASE) != None
    if not valid_entry:
        return False
    
    invalid_type = re.search(r"punch|card rental|hyrbricka| o-ringen|måltider|subvention", text, re.IGNORECASE) != None
    if invalid_type:
        print(f"Not valid: {re.search(r'punch|card rental|hyrbricka| o-ringen|måltider|subvention', text, re.IGNORECASE)}")
        return False

    return True

def log(s:str):
    print(s)

def calculate_discount(valid:bool, status:str, text:str, competition:str, klass:str, age) -> int:
    """Calculate discount in precentage"""
    # Status should already been verified via 'valid' - only included for logging purpose
    if not valid: 
        log(f"[calculate_discount] Entry not valid for discount '{text}', status: '{status}'")
        return 0

    # Members of age < 21 get 100% discount for "Vårserie" and "DM"
    if age < 21:
        if re.search(r"vårserie|dm, ", competition, re.IGNORECASE) != None:
            return 100
    
    publiktävling = re.search(r"publiktävling", competition, re.IGNORECASE) != None
    if re.search(r"sm, |sm sprint|veteran|i 25manna|skogsflicks", competition, re.IGNORECASE) != None and not publiktävling:
        return 100

    return 40

assert calculate_discount(False, "", "Does not matter here", "", "H10", 10) == 0
assert calculate_discount(False, "Ej start", "Does not matter here", "", "H10", 10) == 0
assert calculate_discount(True, "", "Does not matter here", "Landehofs hösttävling", "H10", 10) == 40
assert calculate_discount(True, "", "Does not matter here", "Landehofs hösttävling", "H50", 50) == 40
assert calculate_discount(True, "", "Does not matter here", "25mannamedeln + Swedish League, #9 (WRE)", "H50", 50) == 40
assert calculate_discount(True, "", "Does not matter here", "Sjövalla FK 1 i 25manna", "H50", 50) == 100

def calculate_discount_amount(amount, valid, discount:int):
    """Calculate only discounted amount"""
    if not valid:
        return 0

    amount = int(float(amount.replace(",","."))) if type(amount) == str else int(amount)
    if discount == 100:
        return amount

    return round(amount * (discount / 100))

assert calculate_discount_amount("100", False, 40) == 0
assert calculate_discount_amount("100", True, 40) == 40
assert calculate_discount_amount("100", False, 100) == 0
assert calculate_discount_amount("100", True, 100) == 100

# 2022-12-13 'amount' and 'fee' is in very few cases different, but seems like we can ignore 'fee'
def calculate_amount_to_pay(amount, late_fee, valid:bool=False, discount:int=0) -> int:
    """Total amount to pay, including potential discount
    
    Requirements:
    - Entry must be valid (in scope of discount)
    - Late fee is never part of discount
    """
    amount = int(float(amount.replace(",","."))) if type(amount) == str else int(amount)
    late_fee = 0 if late_fee == "" else int(float(late_fee.replace(",","."))) if type(late_fee) == str else int(float(late_fee))

    if not valid:
        return amount + late_fee

    if discount == 100:
        return late_fee

    return amount - calculate_discount_amount(amount, valid, discount) + late_fee

assert calculate_amount_to_pay(100, 30, False, 40) == 130
assert calculate_amount_to_pay(100, 0, False, 40) == 100
assert calculate_amount_to_pay(0, 50, False, 100) == 50
assert calculate_amount_to_pay(100, 0, True, 40) == 60
assert calculate_amount_to_pay(100, 50, True, 40) == 110
assert calculate_amount_to_pay(100, 0, True, 100) == 0
assert calculate_amount_to_pay(100, 50, True, 100) == 50

def calculate_age(birth_date:str):
    """Calcuate age given birth data"""
    return today.year - int(str(birth_date)[0:4])

# Action
df_members = pd.read_excel(args.member_file)
invoices = parse_data(args.data_file)

df_invoices = pd.json_normalize(invoices,
    record_path=['items'],
    meta=['batchId', 'id',
        ['invoiceDetails', 'e-mail'],
        ['invoiceDetails', 'invoiceNo']],
    meta_prefix='item-')

# Add column for full name to be able to match invoice data frame from Eventor
df_members['Namn'] = df_members['Förnamn'] + ' ' + df_members['Efternamn']
df_members['Ålder'] = df_members['Födelsedatum'].apply(calculate_age)

# Enrich with more columns
df_invoices['Person'] = df_invoices['text'].apply(extract_person_name)
df_invoices['Tävlingsinfo'] = df_invoices['text'].apply(extract_competition_details)
df_invoices['Tävling'] = df_invoices['Tävlingsinfo'].apply(extract_competition)
df_invoices['Klass'] = df_invoices['Tävlingsinfo'].apply(extract_class)

# Rearrange columns
# From: "id", "text", "amount", "fee", "lateFee", "status", "item-batchId", "item-id", "item-invoiceDetails.e-mail", "item-invoiceDetails.invoiceNo", "Person", "Tävlingsinfo", "Tävling", "Klass"
# To: "id", "text", "item-batchId", "item-id", "item-invoiceDetails.e-mail", "item-invoiceDetails.invoiceNo", "Person", "Tävlingsinfo", "Tävling", "Klass", "amount", "fee", "lateFee", "status"
df_invoices = df_invoices[["id", "text", "item-batchId", "item-id", "item-invoiceDetails.e-mail", "item-invoiceDetails.invoiceNo", "Person", "Tävlingsinfo", "Tävling", "Klass", "amount", "fee", "lateFee", "status"]]

df_final = pd.merge(df_invoices, df_members[['Namn','E-postadress','Ålder']], left_on=['Person','item-invoiceDetails.e-mail'], right_on=['Namn','E-postadress'], validate='many_to_one')
df_final.drop(['Namn','E-postadress'], axis=1, inplace=True)

df_final['OK?'] = np.vectorize(valid_entry)(df_final['text'],df_final['status'],df_final['Tävling']) 
df_final['Subvention %'] = np.vectorize(calculate_discount)(df_final['OK?'],df_final['status'],df_final['text'],df_final['Tävling'],df_final['Klass'],df_final['Ålder'])

df_final['Subvention'] = np.vectorize(calculate_discount_amount)(df_final['amount'],df_final['OK?'],df_final['Subvention %'])
df_final['Att betala'] = np.vectorize(calculate_amount_to_pay)(df_final['amount'],df_final['lateFee'],df_final['OK?'],df_final['Subvention %'])

#print(df_final[['text','Tävling','OK?']].head(60))
#print(df_final[['text','Tävling','Ålder','Subvention %']].head(60))

df_final.drop('Tävlingsinfo', axis=1, inplace=True)

# Start building data for invoices
#g1 = df_final.groupby(["item-batchId", "Person"])

#df_test = df_final.loc[df_final['Person'] == "Fabian Alinder"]
#df_test = df_final.loc[df_final['Person'] == "Per-Arne Wahlgren"]

# Group by person
#df_test = df_final.loc[df_final['item-batchId'] == 1033] # TODO: Just test - remove later
df_test = df_final
g = df_test[['Person','Subvention','Att betala']].groupby(["Person"])

subvention = g['Subvention'].aggregate('sum')
att_betala = g['Att betala'].aggregate('sum')

# Object for storing money to pay per person
invoices_data = {}

# Loop all persons
for idx, name in enumerate(df_test["Person"].unique()):
    print(name)
    print(f" - Subvention: {str(subvention.loc[name]).rjust(4, ' ')} kr")
    print(f" - Att betala: {str(att_betala.loc[name]).rjust(4, ' ')} kr")
    invoices_data[name] = {"name":name, "discount": subvention.loc[name], "total_amount": att_betala.loc[name], "invoiceNo": idx+1, "invoiceName": f"Faktura-{idx+1}.pdf"}

#print(invoices_data)

#print(f"  Subvention: {g['Subvention'].aggregate('sum').values}")
#print(f"  Att betala: {g['Att betala'].aggregate('sum')}")

#exit(0)

#g1 = df_test.groupby(["Person"])
#print(g1.head(100))
#print(g1.groups)
#print(f"Subvention: {g1['Subvention'].aggregate('sum').values[0]}")
#print(f"Att betala: {g1['Att betala'].aggregate('sum').values[0]}")
#pay_info = g1.aggregate({'Subvention':'sum', 'Att betala':'sum'}) # Works byt yeilds a multiindex result
#print(f"Att betala: {pay_info[0]} {pay_info[1]}")

def save_excel(df:pd.DataFrame, invoiceData, filename:str):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object. We also turn off the
    # index column at the left of the output dataframe.
    df.to_excel(writer, sheet_name='Aktivitetsöversikt', index=False)
    pd.DataFrame({}).to_excel(writer, sheet_name='Fakturaöversikt', index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet = writer.sheets['Aktivitetsöversikt']
    worksheet2 = writer.sheets['Fakturaöversikt']

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Make the columns wider for clarity.
    worksheet.set_column(0,  max_col - 1, 12)

    # Set the autofilter.
    worksheet.autofilter(0, 0, max_row, max_col - 1)

    # Add an optional filter criteria. The placeholder "Region" in the filter
    # is ignored and can be any string that adds clarity to the expression.
    #worksheet.filter_column(0, 'Region == East')

    # It isn't enough to just apply the criteria. The rows that don't match
    # must also be hidden. We use Pandas to figure our which rows to hide.
    #for row_num in (df.index[(df['Region'] != 'East')].tolist()):
    #    worksheet.set_row(row_num + 1, options={'hidden': True})

    SEK = workbook.add_format({'num_format': '# ##0 kr'})
    bold_format = workbook.add_format({'bold': True})
    valid_format = workbook.add_format({'bg_color': '#C6EFCE'})
    invalid_format = workbook.add_format({'bg_color': '#FFC7CE'})
    eventor_format = workbook.add_format({'bg_color': '#F5D301'})
    eventor_mix_format = workbook.add_format({'bg_color': '#F8E201'})
    sfk_format = workbook.add_format({'bg_color': '#3F9049', 'font_color':'#FFFFFF'})

    col_widths = [5, 50, 4, 6, 17, 5, 23, 24, 12, 11, 8, 6, 6, 6, 8, 6, 11, 11, 11, 11]
    for i, w in enumerate(col_widths):
        worksheet.set_column(i, i, w)

    worksheet.set_column(0, 0, None, bold_format)
    #worksheet.set_column(9, 9, None, SEK)

    # Column colors
    # OK?	Subvention %	Subvention	Att betala	Faktura status	Faktura betalad
    worksheet.write('B1', 'Text', eventor_format)
    worksheet.write('C1', 'BatchId', eventor_format)
    worksheet.write('D1', 'E-id', eventor_format)
    worksheet.write('E1', 'E-mail', eventor_format)
    worksheet.write('F1', 'E-invoiceNo', eventor_format)
    worksheet.write('G1', 'Person', eventor_format)
    worksheet.write('H1', 'Event', eventor_mix_format)
    worksheet.write('I1', 'Klass', eventor_mix_format)
    worksheet.write('J1', 'amount', eventor_format)
    worksheet.write('K1', 'fee', eventor_format)
    worksheet.write('L1', 'lateFee', eventor_format)
    worksheet.write('M1', 'status', eventor_format)
    worksheet.write('N1', 'Ålder', eventor_format)
    worksheet.write('O1', 'OK?', sfk_format)
    worksheet.write('P1', '%', sfk_format)
    worksheet.write('Q1', 'Subvention', sfk_format)
    worksheet.write('R1', 'Att betala', sfk_format)
    worksheet.write('S1', 'Faktura status', sfk_format)
    worksheet.write('T1', 'Faktura betald', sfk_format)

    worksheet.write_comment('B1', 'Underlag från Eventor (datum saknas tyvärr)')
    worksheet.write_comment('J1', 'Avgift - enligt Eventor')
    worksheet.write_comment('K1', 'Oklart - enligt Eventor. Ingnorerad då den sällan skiljer från "amount"')
    worksheet.write_comment('L1', 'Avgift för efteranmälan (subventioneras inte)')
    worksheet.write_comment('M1', 'Om "Ej start" eller inte')
    worksheet.write_comment('O1', 'Om posten ska subventioneras eller inte givet SFK regler')
    worksheet.write_comment('P1', 'Subvention i procent per post enligt SFK regler')
    worksheet.write_comment('Q1', 'Eventuell subvention i kr per post enligt SFK regler')
    worksheet.write_comment('R1', 'Att betala för post efter eventuell subvention enligt SFK regler')

    # If discount if ok or not
    worksheet.conditional_format(1, 14, max_row, 14, {'type':     'cell',
                                        'criteria': '==',
                                        'value':    'True',
                                        'format':   valid_format})
    worksheet.conditional_format(1, 14, max_row, 14, {'type':     'cell',
                                        'criteria': '==',
                                        'value':    'False',
                                        'format':   invalid_format})

    worksheet2.write('A1', 'Fakturanummer', sfk_format)
    worksheet2.write('B1', 'Person', sfk_format)
    worksheet2.write('C1', 'Subvention (kr)', sfk_format)
    worksheet2.write('D1', 'Totalt att betala (kr)', sfk_format)
    worksheet2.write('E1', 'Fakturanamn', sfk_format)
    worksheet2.write_comment('C1', 'Summa subvention (som information) för aktuell person')
    worksheet2.write_comment('D1', 'Total, subventionerad, summa att betala för aktuell person')
    worksheet2.set_column(0, 0, 12)
    worksheet2.set_column(1, 1, 22)
    worksheet2.set_column(2, 2, 12)
    worksheet2.set_column(3, 3, 16)
    worksheet2.set_column(4, 4, 15)
    idx = 0
    for name in invoiceData:
        #worksheet2.write()
        #print(inv)
        idx = idx + 1
        worksheet2.write(idx, 0, invoiceData[name]['invoiceNo'])
        worksheet2.write(idx, 1, invoiceData[name]['name'])
        worksheet2.write(idx, 2, invoiceData[name]['discount'])
        worksheet2.write(idx, 3, invoiceData[name]['total_amount'])
        worksheet2.write(idx, 4, invoiceData[name]['invoiceName'])

    #worksheet2.wrtie


    # Close the Pandas Excel writer and output the Excel file.
    #writer.save()
    writer.close()

df_final['Faktura status'] = ""
df_final['Faktura betalad'] = ""

if True:
    ##df_final.to_excel(args.out_file, engine="openpyxl")
    save_excel(df_final, invoices_data, args.out_file)
    print(f"Save result to file: '{args.out_file}'")
#df_final.to_excel("files/all_invoices2.xlsx", engine="xlsxwriter")


