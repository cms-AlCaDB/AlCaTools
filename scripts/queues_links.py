'''
script to write the links of the differences between last versioned GT in autoCond and the corresponding Queue
Script usage, to be run in a release area (after cmsrel, cmsenv, etc.):
python3 queues_links.py '123X'
where '123X' can be replaced by any release cycle. 
or leave blank to get comparison from all GT keys in autoCond.
'''

from Configuration.AlCa import autoCond
import sys

try:
    release_cycle = sys.argv[1]
    print('**************')
    print(f'** Printing differences between {release_cycle} GTs and Queues in autoCond.py **')
    print('If all GT differences are printed, it means there are no GTs from this release cycle in autoCond.')
    print('**************')
    
except:
    release_cycle = ''
    print('**************')
    print('** Printing differences between all GTs and Queues in autoCond.py **')
    print('**************')
    
autoCond_compare = {}

link = 'https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts'
    
## get the value from each key of release_autoCond and my autoCond:
for i in autoCond.autoCond.keys():
    # do not consider the keys from the autoCondModifiers.py or old ones in autoCond.py
    if "Fake" in str(i) or "0T" in str(i) or "ddd" in str(i) or "GRun" in str(i) or "FULL" in str(i) or "HIon" in str(i) or "PIon" in str(i) or "PRef" in str(i) or "_T" in str(i) or "upgradeP" in str(i) or "run2_hlt_hi" in str(i) or "_ppref" in str(i) or str(i) == "mc" or "run1_hlt_relval" in str(i) or "run1_data" in str(i) or str(i) == "startup" or "starthi" in str(i) or "com10" in str(i) or "hltonline" in str(i) or "upgrade2017" in str(i) or "upgrade2021" in str(i) or "upgrade2022" in str(i) or "run3_mc_2022v11" in str(i) or "run3_hlt_2022v11" in str(i) or "run3_data_2022v11" in str(i):
        continue
        
    autoCond_compare[i] = autoCond.autoCond[i]
    
    gt_version = autoCond.autoCond[i].split('_')[-1]
    release = autoCond.autoCond[i].split('_')[0]
    gt = autoCond.autoCond[i]
    queue = gt.replace(gt_version, "Queue")
        
    if release == release_cycle:
        print(f'**{i}**')
        print(f'{link}/{queue}/{gt}')
        break
    else:
        print(f'**{i}**')
        print(f'{link}/{queue}/{gt}')