import os

"""Create commands to send mail"""


with open('log_invoices_2022-12-23.txt', 'r') as file:
    for line in file:
        if line.startswith("Invoice: "):
            line = line.replace("Invoice: ","")
            line = line.replace("\n","")
            parts = line.split("|")
            print(f"cat fakturor_2022.txt | mail -s  \"Faktura-{parts[0]} från Sjövalla FK Orientering\" {parts[2]} -A Faktura-{parts[0]}.pdf ")
            #print(parts)


# ['91', 'Wilmer Kroon', 'jojjepersson@yahoo.se', 'files/pdfs/Faktura-91.pdf']
# echo "Exempel 8" | mail -s "Faktura - Exempel 8" calle.bokedal@gmail.com -A Faktura-133.pdf