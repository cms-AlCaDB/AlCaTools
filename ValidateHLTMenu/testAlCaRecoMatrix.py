# testAlCaRecoMatrix.py
# Purpose: check that the three mappings: AlcaRecoMatrix,
# TriggerBits and  HLT menu are all compatible with one another.
# Author: Thiago Tomei
# Date: 2018-04-24

from __future__ import print_function 
import json
import fnmatch

RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
WARNING = "\033[1;93m"

# The AlcaRecoMatrixJSON should be kept up to date by the AlCa-TSG contacts
# It should be checked with whatever is in Tier-0...
# The TriggerBitsJSON should be dumped from CondTools/HLT subsystem
# and brought back here. The HLT menu should be dumped with
# hltGetConfiguration
AlcaRecoMatrixJSON = "AlcaRecoMatrix/AlcaRecoMatrix_2018_HLTv1p0.json"
TriggerBitsJSON = "triggerBits.json"
HLTMenuName = "hlt.py"

with open(AlcaRecoMatrixJSON, 'r') as fp:
    wanted = json.load(fp)

### FIXME - cross-check Tier-0 config
with open('data.json', 'r') as fp:
    tier0Config = json.load(fp)
    
for datasetname in wanted.keys():
   if datasetname not in tier0Config:
      print((RED+"ERROR:"+RESET),"dataset ",datasetname," not known to Tier-0")
   else:
       tier0Alcarecos = set(tier0Config[datasetname])
       wantedAlcarecos = set(wanted[datasetname])
       if not wantedAlcarecos.issubset(tier0Alcarecos):
           print((RED+"ERROR:"+RESET),"some Alcarecos for ",datasetname," not configured at Tier-0")
           print("Wanted: ",wantedAlcarecos)
           print("Tier-0: ",tier0Alcarecos)
### END FIXME

AlcaRecoMatrix = wanted

with open(TriggerBitsJSON, 'r') as fp:
    triggerBits = json.load(fp)

ardsMapping = list()

# Invert the AlcaRecoMatrix.
# Usually we have Dataset --> List of Alcarecos, since that is
# what Tier-0 needs. We want to invert it, having a list of
# AlcaRecos that have to run in one or more datasets.
# To make this easier, we cast the AlcaRecoMatrix as a
# many-to-one function: each line has one Alcareco and one
# dataset. An Alcareco can then have more than one line
# assigned to it, since it can run over more than one dataset.
# Data structure: 
# | Alcareco | Dataset |
for dataset in AlcaRecoMatrix.keys():
    alcarecos = AlcaRecoMatrix[dataset]
    for alcareco in alcarecos:
       ards = (alcareco,dataset)
       ardsMapping.append(ards)

ardsMapping.sort()

#for ards in ardsMapping:
#    print(ards)
#print()


ardstbMapping = list()

# Now we map into the TriggerBits as well. Each Alcareco has
# a list of paths to trigger on, so we just add that list into
# the same line. The Data structure now is:
# | Alcareco | Dataset | TriggerBits |for ards in ardsMapping:
for ards in ardsMapping:    
    alcareco = ards[0]
    dataset = ards[1]
    if alcareco in triggerBits.keys():
        ardstb = (alcareco, dataset, triggerBits[alcareco])
        ardstbMapping.append(ardstb)

ardstbMapping.sort()    

#for ardstb in ardstbMapping:
#    print(ardstb)

# Now the qustion is if the right part of that mapping, namely
# Dataset <--> TriggerBits, makes sense. The place where that is
# defined is the HLT menu itself.

print('\n')

# Parse the HLT menu
### Usually, blindly executing an external file is a security hazard... 
print("Parsing HLT menu...")
execfile(HLTMenuName)

print("List of datasets:")
print(sorted(process.datasets._Parameterizable__parameterNames))

print('\n')

for ardstb in ardstbMapping:
    alcareco = ardstb[0]
    dataset = ardstb[1]
    triggerBits = ardstb[2]

    if dataset == "Express": # Stupid Corner Case
        dataset="ExpressPhysics"
    
    ### For each AlcaReco/Dataset/TriggerBits combo, check if it fires.
    if dataset in process.datasets._Parameterizable__parameterNames:
        theDataset = getattr(process.datasets,dataset)
        triggerBitFires = False

        if len(triggerBits) == 0: # It is stupid that some trigger bits are empty...
            triggerBitFires = True

        for requestedPath in triggerBits:
            if len(fnmatch.filter(theDataset,requestedPath)) != 0:
                triggerBitFires = True

        if triggerBitFires:
            print((GREEN+"SUCCESS: "+RESET),'\t',alcareco," in ",dataset," fires!")
        else:
            print((RED+"FAILURE: "+RESET),'\t',alcareco," in ",dataset,"does not fire...")
    else: ### Ooops, some datasets are not here... maybe they are cosmics?
        print("ERROR: ",'\t',"dataset ",(WARNING+dataset+RESET)," not available in HLT menu")
        continue
