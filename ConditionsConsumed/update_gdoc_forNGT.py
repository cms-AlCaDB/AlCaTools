#### Saswati Nandan, INFN/Pisa ###

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", dest="input_txt", default='outputForTwiki_DATA.txt', help="which text file is used to read the tags")
options = parser.parse_args()
input_txt = options.input_txt

os.system('wget --output-file="logs.csv" "https://docs.google.com/spreadsheets/d/1ZgmgSqYIHKZ4yFCihz22HL771EzSsu2vyLWYbgQUZvg/export?format=csv&gid=1215353349" -O "test.csv"')

import csv
lists = []
with open(input_txt, 'r') as f:
    lines = f.readlines()

with open("test.csv", "r") as f:
     reader = csv.reader(f)
     for idx, rows in enumerate(reader):
         if idx ==0:
             hlt_index = rows.index('Consumed at HLT (from documentation)')
             l1_index = rows.index('Consumed at L1 repack (from documentation)')
             lists.append(rows)
             continue
         found = False
         for line in lines:
             if rows[1] != '-':
                 if rows[0] + ' / ' + rows[1] in line or rows[0] + ' / !' + rows[1] in line:
                     found = True
             elif rows[0] in line:
                  found = True
             if found == True:
                 l1 = line.split('|')[2].find('Yes') !=-1
                 hlt = line.split('|')[3].find('Yes') !=-1
                 break
         if found:
             if l1:  rows[l1_index] = 'Yes'
             if hlt: rows[hlt_index] = 'Yes'
         else:
             rows[l1_index] = 'Missing in GT'
             rows[hlt_index] = 'Missing in GT'
         lists.append(rows)

with open('test1.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(lists)
