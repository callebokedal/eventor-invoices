# Fakturor för Sjövalla FK

## Generera underlag

- Exportera aktuell medlemsfil från Eventor https://eventor.orientering.se/OrganisationAdmin/Members?organisationId=321https://eventor.orientering.se/OrganisationAdmin/ExportMembersToExcel/321?year=2023
Öppna filen i Excel och spara sedan ner som 97-2004 format. Annars är det bara en XML-fil som koden just nu inte hanterar.
Sparad som: files/members_sjovalla_fk_2023_converted.xls

- Skapa fakturaperiod i Eventor till exempel mellan 1/1-1/8 (Eventor tar inte med sista dagen, dvs 31/7 effektivt). Id för denna fakturaperiod: 1103
- Logga in på ol-molnet och kör:
```bash
node download_invoices.js -b 1103 -t >> period_1_2023_1103.txt
# Detta skript kan eventuellt rensas en del
``` 

- Ladda hem filerna:
```bash
# <somepath_x> ska bytas ut mot verklig path
scp molnet:"/<somepath_1>/eventor-invoices/period_1_2023_*" /<somepath_2>/eventor-invoices/files
``` 

- Verifiera filerna:
```bash
grep batchId files/period_1_2023_1103.txt | wc -l # Ska vara 197
``` 

- Skapa anpassad fil processning:
```bash
grep batchId files/period_1_2023_1103.txt >> files/period_1_2023_1103_for_py.txt
```

- Kör pythonskript för att skapa Excel:
```bash
source .venv/bin/activate 
# Bara en gång
# python -m pip install -r requirements.txt
# python -m pip install --upgrade pip
python parse_data_files.py files/period_1_2023_1103_for_py.txt files/members_sjovalla_fk_2023_converted.xls files/2023-08-15_Fakturor_Period_1_2023.xlsx
```

- Output blev:
```bash
2023-08-15_Fakturor_Period_1_2023.xlsx
2023-08-15_Fakturor_Period_1_2023_Aktiviteter_2023-08-15.json.tar.gz
2023-08-15_Fakturor_Period_1_2023_Fakturor_2023-08-15.json.tar.gz
```

- Skapat en kopia som jag laddat upp och skickat länk till Ordförande ```2023-08-15_Fakturor_Period_1_2023_v1.xlsx```

## Gå igenom avgifter

## Generera fakturor

## Skicka ut fakturor
