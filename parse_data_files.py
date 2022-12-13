import re
import json
import argparse
import datetime
import pandas as pd
import numpy as np
from datetime import date

"""Convert report files from Eventor/OL-molnet into usable data-files (invoice details)"""

today = date.today()

parser = argparse.ArgumentParser()
parser.add_argument("data_file", type=str, help="File to read input from (JSON-lines with invoice data)")
parser.add_argument("member_file", type=str, help="File with Member details exported from Eventor")
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
    #match = re.search(r"^Anmälan för (.*) i", text)
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
    #match = re.search(r" - ([0-9a-zåäö ,#-]*)$", competition_details, re.IGNORECASE)
    res = re.split(" - ", competition_details)
    #print(res)
    #print("".join(res[:-1]))
    return " - ".join(res[:-1])
    #if match != None:
    #    return competition_details.replace(match.group(0),"")
    #return ""

assert extract_competition("Aleträffen - H40") == "Aleträffen"
assert extract_competition("Snötrampen - Insk. 2 km") == "Snötrampen"
assert extract_competition("Vårserien, #2 - Insk. 2 km") == "Vårserien, #2"
assert extract_competition("Midsommarsprinten - Göteborg Syd - Röd") == "Midsommarsprinten - Göteborg Syd"

def extract_class(competition_details:str):
    """Extract class info from competition details"""
    res = re.split(' - ', competition_details)
    return str(res[-1])

assert extract_class("Vårserien, #2 - Insk. 2 km") == "Insk. 2 km"
assert extract_class("Aleträffen - H40") == "H40"
assert extract_class("Midsommarsprinten - Göteborg Syd - Röd") == "Röd"

#    match = re.search(r" - ([0-9a-zåäö ,#-]*)$", competition_details, re.IGNORECASE)
#    if match != None:
#        return match.group(1)
#    return ""

def extract_competition_details(text:str):
    """Extract competition name"""
    valid_entry = re.search(r"^Anmälan för ", text, re.IGNORECASE) != None
    if not valid_entry:
        return ""
    
    name = extract_person_name(text)
    pattern = f"^Anmälan för {name} i "
    remaining = re.sub(pattern, "", text)
    if remaining.startswith("Anmälan"):
        # Case 
        # Anmälan för <Name>, <Team name> i SM, sprint - D20 Kval B
        res = re.split(', ', text)
        #print(text)
        #print(res)
        #print(res[1:])
        #print(", ".join(res[1:]))
        return ", ".join(res[1:])
    return remaining

assert extract_competition_details("Anmälan för Ett Namn, Sjövalla FK 1 i Daladubbeln, stafett  - D16") == "Sjövalla FK 1 i Daladubbeln, stafett  - D16"
assert extract_competition_details("Anmälan för Ett Annat Namn, Göteborg-Majorna OK / IFK Göteborg Orientering / Kungälvs OK / OK Landehof / Sjövalla FK 5 i 25manna - 25manna") == "Göteborg-Majorna OK / IFK Göteborg Orientering / Kungälvs OK / OK Landehof / Sjövalla FK 5 i 25manna - 25manna"
assert extract_competition_details("Anmälan för Ett Annat Namn, Sjövalla FK 1 i 25manna - 25manna") == "Sjövalla FK 1 i 25manna - 25manna"
assert extract_competition_details("Anmälan för Ett Namn i Snötrampen - Insk. 2 km") == "Snötrampen - Insk. 2 km"
assert extract_competition_details("Anmälan för Ett Namn i Vårserien, #2 - Insk. 2 km") == "Vårserien, #2 - Insk. 2 km"
assert extract_competition_details("Anmälan för Ett Namn i Aleträffen - H40") == "Aleträffen - H40"

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

    # TODO: More cases to handle?

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

    #print(f"calculate_amount_to_pay - amount: '{amount}', late fee: '{late_fee}', valid: '{valid}'")
    if not valid:
        return amount + late_fee

    if discount == 100:
        return late_fee

    #return round(amount - (amount * (discount / 100))) + late_fee
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
print(args.member_file)
#df_members = pd.read_excel(args.member_file, engine='xlrd')
df_members = pd.read_excel(args.member_file)
invoices = parse_data(args.data_file)
#print(invoices)

#df = pd.read_json(json.dumps(invoices))
#print(df.head(3))

df_invoices = pd.json_normalize(invoices,
    record_path=['items'],
    meta=['batchId', 'id',
        ['invoiceDetails', 'e-mail'],
        ['invoiceDetails', 'invoiceNo']],
    meta_prefix='item-')
#print(df_invoices.head(30))
#print(df_invoices.info())

# Add column for full name to be able to match invoice data frame from Eventor
df_members['Namn'] = df_members['Förnamn'] + ' ' + df_members['Efternamn']
df_members['Ålder'] = df_members['Födelsedatum'].apply(calculate_age)

# Enrich with more columns
df_invoices['Person'] = df_invoices['text'].apply(extract_person_name)
df_invoices['Tävlingsinfo'] = df_invoices['text'].apply(extract_competition_details)
df_invoices['Tävling'] = df_invoices['Tävlingsinfo'].apply(extract_competition)
df_invoices['Klass'] = df_invoices['Tävlingsinfo'].apply(extract_class)
##df_invoices['Ålder'] = df_members['']

#df_final = pd.merge(df_members[['Namn','E-postadress','Ålder']], df_invoices, left_on=['Namn','E-postadress'], right_on=['Person','item-invoiceDetails.e-mail'], validate='one_to_many')
df_final = pd.merge(df_invoices, df_members[['Namn','E-postadress','Ålder']], left_on=['Person','item-invoiceDetails.e-mail'], right_on=['Namn','E-postadress'], validate='many_to_one')
df_final.drop(['Namn','E-postadress'], axis=1, inplace=True)

df_final['OK?'] = np.vectorize(valid_entry)(df_final['text'],df_final['status'],df_final['Tävling']) 
#def calculate_discount(valid:bool, status:str, text:str, competition:str, klass:str, age) -> float:
df_final['Subvention %'] = np.vectorize(calculate_discount)(df_final['OK?'],df_final['status'],df_final['text'],df_final['Tävling'],df_final['Klass'],df_final['Ålder'])

#def calculate_amount_to_pay(amount:int, late_fee:int, valid:bool, discount:int) -> int:
df_final['Subvention'] = np.vectorize(calculate_discount_amount)(df_final['amount'],df_final['OK?'],df_final['Subvention %'])
df_final['Att betala'] = np.vectorize(calculate_amount_to_pay)(df_final['amount'],df_final['lateFee'],df_final['OK?'],df_final['Subvention %'])

#df_invoices['Aktivitet ok?'] = np.vectorize(valid_activity)(df_invoices['Tävling'],df_invoices['Klass']) 

#print(df_invoices[['text','Person','item-id','item-invoiceDetails.invoiceNo']])

print(df_final[['text','Tävling','OK?']].head(60))
print(df_final[['text','Tävling','Ålder','Subvention %']].head(60))

df_final.drop('Tävlingsinfo', axis=1, inplace=True)
df_final.to_excel("files/all_invoices.xlsx")
#df_invoices[['text','item-id','item-invoiceDetails.invoiceNo']].to_excel("files/data.xlsx", engine='xlsxwriter')


