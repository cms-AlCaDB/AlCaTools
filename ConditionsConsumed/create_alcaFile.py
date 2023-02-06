import re

'''
this is just an ugly skeleton for creating the file allAlCaTags.txt to be used in script getAlCaCondInGT.py
it reads as input, the output file of the workflow run with the --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)'
and strips out the tag names, to be used to create the table that goes in the twiki
https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2022
'''

outfile = open("allAlCaTags.txt", "w")

with open('step3_PromptGT.log') as f:
    lines = f.readlines()
    for l in lines:
        newl = l.split(': frontier:')[0]
        if re.search(r' / ', newl):
            print(newl)
            outfile.write(newl+'\n')

outfile.close()
