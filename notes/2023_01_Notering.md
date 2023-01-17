# Noteringar

2023-01-17 Skapat nya pdfer (mha create_pdfs.py) och laddat upp till molnet - baserat på P-A's senaste fil som han hade laddat upp ("Fakturor_2022_v3_paw.xlsx")

2023-01-10 Gör om processen för att ha något att jämföra med. Första gången råkade jag tyvärr
skapa överlappande perioder (juli månad). Kör denna omgång för att ha något att jämföra med.

## Prefix

Ladda hem aktuella medlemmar
OBS!
Spara om filen som en modern xlsx-fil:

  files/members_sjovalla_fk_2022.xlsx

## Steg för steg

- Skapa två fakturaperioder i Eventor
    - 2022 Period 1 1/1-30/6 	2022-01-02 	2022-06-26 	109 	170 	137 854,50 SEK (1051)
    - 2022 Period 2 1/7-8/12 	2022-07-02 	2022-12-08 	109 	164 	217 624,38 SEK (1053)
- Installera nytt script (vid behov)
scp /Users/cabo02/dev/github/sfk/eventor-invoices/download_invoices.js molnet:/home/calle/eventor-invoices/
- Kör download_invoices.js i molnet
node download_invoices.js -b 1051 -t >> period_1_2022_1051.txt
node download_invoices.js -b 1053 -t >> period_2_2022_1053.txt
- Ladda hem filerna
scp molnet:/home/calle/eventor-invoices/period_1_2022_1051.txt /Users/cabo02/dev/github/sfk/eventor-invoices/files/
scp molnet:/home/calle/eventor-invoices/period_2_2022_1053.txt /Users/cabo02/dev/github/sfk/eventor-invoices/files/
- Kontroll
grep batchId files/period_1_2022_1051.txt | wc -l -> 170
grep batchId files/period_2_2022_1053.txt | wc -l -> 164
- Gör om till data-filer
grep -h batchId files/period_1_2022_1051.txt files/period_2_2022_1053.txt >> files/data_2022_1051_1053.txt
- Parse data-files
# One-time -> create virtual environment in folder "env"
# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

# Behövs bara en gång - därför bortkommenterat
# python3 -m venv env

source env/bin/activate
python parse_data_files.py files/data_2022_1051_1053.txt files/members_sjovalla_fk_2022.xlsx files/2023-01-11-Verification/2023-01-11_Verification.xlsx

```sh
# Result/output
Start creating Excel for invoices
Saved result to file: 'files/2023-01-11-Verification/2023-01-11_Verification.xlsx'
Saved result backup to: 'files/2023-01-11-Verification/2023-01-11_Verification_Aktiviteter_2023-01-11.json.tar.gz'
Saved result backup to: 'files/2023-01-11-Verification/2023-01-11_Verification_Fakturor_2023-01-11.json.tar.gz'
```

# Leave virtualenv
deactivate