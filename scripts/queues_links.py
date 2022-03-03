'''
script to write the links of the differences between last versioned GT in autoCond and the corresponding Queue

Script usage:
python3 queues_links.py '123X'

where '123X' can be replaced by any release cycle. 
'''

from Configuration.AlCa import autoCond

autoCond_compare = {}
    
## get the value from each key of release_autoCond and my autoCond:
for i in autoCond.autoCond.keys():
# do not consider the keys from the autoCondModifiers.py or old ones in autoCond.py
    if "Fake" in str(i) or "0T" in str(i) or "ddd" in str(i) or "GRun" in str(i) or "FULL" in str(i) or "HIon" in str(i) or "PIon" in str(i) or "PRef" in str(i) or "_T" in str(i) or "upgradeP" in str(i) or "run2_hlt_hi" in str(i) or "_ppref" in str(i) or str(i) == "mc" or "run1_hlt_relval" in str(i) or "run1_data" in str(i) or str(i) == "startup" or "starthi" in str(i) or "com10" in str(i) or "hltonline" in str(i) or "upgrade2017" in str(i) or "upgrade2021" in str(i):
        continue
        
    autoCond_compare[i] = autoCond.autoCond[i]


import sys
release_cycle = sys.argv[1]

link = 'https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/'
for k in autoCond_compare.keys():    
    gt_version = autoCond.autoCond[k].split('_')[-1]
    gt = autoCond.autoCond[k]
    queue = gt.replace(gt_version, "Queue")
    print(f'**{k}**')
    print(link+f'{queue}/{gt}')
    