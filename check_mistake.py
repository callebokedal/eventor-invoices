import argparse
import pandas as pd
import numpy as np

"""Kolla vilka som fått fel på sina fakturor pga överlappande Period 1 & 2

Usage:
(env) cabo02:~/dev/github/sfk/eventor-invoices$ python check_mistake.py files/Fakturor_2022_v2_paw.xlsx 
"""

parser = argparse.ArgumentParser()
parser.add_argument("data_file", type=str, help="File with invoice information")
args = parser.parse_args()

# Action
dfa = pd.read_excel(args.data_file, na_filter=False)
#print(df.head())

df = dfa[["id","Text","BatchId","E-id","Person","Event","Klass","OK?", "Subvention", "Att betala", "Justering"]]
print(df.head())

# Skip Hyrbricka etc.
# df = df[df['OK?'] == True]

duplicateRows = df[df.duplicated(['Text', 'BatchId'])] # => 171 rows
#duplicateRows = df[df.duplicated(['Text'])] # => 271 rows
#print(duplicateRows)

events = duplicateRows[["Event"]]
# Index(['Event'], dtype='object')
#print(events.describe)

#print(events)

uniqueEvents = events["Event"].unique()
print("\n".join(np.sort(uniqueEvents).tolist()))

# Save result
pd.DataFrame.to_excel(duplicateRows, "files/duplicate_rows_230110_2.xlsx")
#pd.DataFrame.to_excel(uniqueEvents, "files/unique_events.xlsx")