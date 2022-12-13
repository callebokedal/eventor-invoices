# Noteringar

Det går inte att skapa fakturor för hela året - Eventor klarar inte det.
Två fakturaperioder blir meckigt för alla.

## Prefix

Ladda hem aktuella medlemmar
OBS!
Spara om filen som en modern xlsx-fil

## Test

- Skapa två fakturaperioder i Eventor
    - 2022 Period 1 	2022-01-02 	2022-07-30 	127 	172 	152 404,50 SEK -> 1033
    - 2022 Period 2 	2022-07-02 	2022-12-08 	109 	164 	217 624,38 SEK -> 1034
- Installera nytt script (vid behov)
scp /Users/cabo02/dev/github/sfk/eventor-invoices/download_invoices.js molnet:/home/calle/eventor-invoices/
- Kör download_invoices.js i molnet
node download_invoices.js -b 1033 -t >> period_1_2022_1033.txt
node download_invoices.js -b 1034 -t >> period_2_2022_1034.txt
- Ladda hem filerna
scp molnet:/home/calle/eventor-invoices/period_1_2022_1033.txt /Users/cabo02/dev/github/sfk/eventor-invoices/files/
scp molnet:/home/calle/eventor-invoices/period_2_2022_1034.txt /Users/cabo02/dev/github/sfk/eventor-invoices/files/
- Kontroll
grep batchId files/period_1_2022_1033.txt | wc -l -> 172
grep batchId files/period_2_2022_1034.txt | wc -l -> 164
- Gör om till data-filer
  # grep batchId files/period_1_2022_1033.txt >> files/data_1_2022.txt
  # grep batchId files/period_1_2022_1033.txt >> files/data_2_2022.txt
  # Slagit ihop båda på en gång
  grep -h batchId files/period_1_2022_1033.txt files/period_1_2022_1033.txt >> files/data_2022.txt
- Parse data-files
# One-time -> create virtual environment in folder "env"
# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
python3 -m venv env

source env/bin/activate
python3 parse_data_files.py files/data_2022.txt

# Leave virtualenv
deactivate
