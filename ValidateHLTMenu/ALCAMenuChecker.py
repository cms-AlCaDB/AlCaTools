# AlCAMenuChecker.py
# Purpose: check that the HLT menu has all the AlCa mandatory paths
# and that the paths are correctly seeded.
# Author: Thiago Tomei
# Date: 2017-11-02

import sys
import os
import fnmatch
import xml.etree.ElementTree as ET

RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

HLTMenuName="hlt.py"
L1MenuName="l1menu.xml"

# Parse the HLT menu
### Usually, blindly executing an external file is a security hazard... 
execfile(HLTMenuName)

# Parse the L1 menu. Notice that here we are parsing the version that is
# usually available from the Twiki:
# https://twiki.cern.ch/twiki/bin/view/CMS/GlobalTriggerAvailableMenus
# If the parsing fails you probably have a different version...
L1MenuTree = ET.parse(L1MenuName)
root = L1MenuTree.getroot()
listOfAvailableSeeds = []
for algo in root.findall('algorithm'):
    listOfAvailableSeeds.append(algo[0].text)

print(process.process)
pathnames = process.paths.viewkeys()

pathsVsSeeds = dict()
seedPrescales = dict() # Not available, the L1 menu doesn't have prescales
pathPrescales = dict()
L1pathPrescales = dict()

def splitL1seeds(fullSeed):
    fs = fullSeed
    l = fs.split(" OR ") # FIXME: what if there is a more convoluted logic???
    s = [w.strip() for w in l]
    return s

# 0) Get the number of HLT columns
numberOfHLTColumns = len(process.PrescaleService.lvl1Labels)
HLTColumnIndexes = range(0,numberOfHLTColumns)
print("HLT menu has",numberOfHLTColumns,"columns")

# 1) Make the map of path vs list of seeds
for path in process.paths:
    thePath = getattr(process,path)
    moduleNames = thePath.moduleNames()
    for moduleName in moduleNames:
        if "hltL1s" in moduleName:
            L1seedModule = getattr(process,moduleName)
            listOfSeeds = splitL1seeds(L1seedModule.L1SeedsLogicalExpression.value())
            pathsVsSeeds[thePath.label()] = listOfSeeds
        if thePath.label() not in pathsVsSeeds:
            pathsVsSeeds[thePath.label()] = list()

# 2) Make the map of path vs prescales
print("-"*64)
for i in process.PrescaleService.prescaleTable:
	# We don't want the Output paths that may be here
	if "Output" in i.pathName.value(): 
		continue
	pathPrescales[i.pathName.value()] = i.prescales.value()
    #print pathPrescales
# 2.1) Add the missing paths, send warnings for missing paths *except* the ones we know are okay
for pathName in pathsVsSeeds.keys():
	if pathName not in pathPrescales.keys():
		pathPrescales[pathName] = [1]*numberOfHLTColumns
		if not("Calibration" in pathName or "HLTriggerFirstPath" in pathName or "HLTriggerFinalPath" in pathName):
			print(RED+'WARNING:'+RESET,pathName,"has no defined HLT prescales")
	if len(pathsVsSeeds[pathName]) == 0:
		L1pathPrescales[pathName] = [1]*numberOfHLTColumns
		
# NOW come the AlCa checks proper

# 1) Do I have all the AlCa datasets?
print("-"*64)
datasetNames = process.datasets._Parameterizable__parameterNames
mandatoryDatasetsAndPaths = {"ExpressPhysics":["HLT_IsoMu20_v*",
                                               "HLT_IsoMu24_v*",
                                               "HLT_IsoMu27_v*",
                                               "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v*",
                                               "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v*",
                                               "HLT_ZeroBias_v*",
                                               "HLT_Random_v*",
                                               "HLT_Physics_v*",
                                               "HLT_ZeroBias_FirstCollisionAfterAbortGap_v*",
                                               "HLT_ZeroBias_IsolatedBunches_v*"],
                             "ExpressAlignment":["HLT_HT300_Beamspot_v*",
                                                 "HLT_HT450_Beamspot_v*",
                                                 "HLT_ZeroBias_Beamspot_v*"],
                             "AlCaLumiPixels":["AlCa_LumiPixels_Random_v*",
                                               "AlCa_LumiPixels_ZeroBias_v*"],
                             "AlCaPhiSym":["AlCa_EcalPhiSym_v*"],
                             "AlCaP0":["AlCa_EcalEtaEBonly_v*", 
                                       "AlCa_EcalEtaEEonly_v*",
                                       "AlCa_EcalPi0EBonly_v*",
                                       "AlCa_EcalPi0EEonly_v*"],
                             "DQMOnlineBeamspot":["HLT_HT300_Beamspot_v*",
                                                  "HLT_ZeroBias_Beamspot_v*"],
                             "TestEnablesEcalHcal":["HLT_EcalCalibration_v*","HLT_HcalCalibration_v*"],
                             "TestEnablesEcalHcalDQM":["HLT_EcalCalibration_v*","HLT_HcalCalibration_v*"],
                             "EcalLaser":["HLT_EcalCalibration_v*"],
                             "RPCMonitor":["AlCa_RPCMuonNormalisation_v*"]
                             }
mandatoryDatasets = mandatoryDatasetsAndPaths.keys()
mandatoryDatasets.sort()
presentMandatoryDatasets = []
row_format ='{0: <32}'
row_format2 = '{0: <48}'

for mds in mandatoryDatasets:	
    if mds in datasetNames:
        print(row_format.format(mds),GREEN+"PRESENT"+RESET)		
        presentMandatoryDatasets.append(mds)
    else:
        print(row_format.format(mds),RED+"ABSENT"+RESET)
        presentMandatoryDatasets.sort()
        
# 2) Do the datasets have all paths they should have?
print("-"*64)
for mds in presentMandatoryDatasets:
    theDataset = getattr(process.datasets,mds)
    for requestedPath in mandatoryDatasetsAndPaths[mds]:
        pathIsPresent = False
        if len(fnmatch.filter(theDataset,requestedPath)) == 0:
            print(row_format.format(mds),row_format2.format(requestedPath),RED+"ABSENT"+RESET)
        # Do the paths have at least one L1 seed available in the menu?    
        for matchingPath in fnmatch.filter(theDataset,requestedPath):
            hasL1Seed = False
            pathSeeds = pathsVsSeeds[matchingPath]
            if len(pathSeeds) == 0:
                hasL1Seed = True
            for seed in pathSeeds:
                if seed in listOfAvailableSeeds:
                    hasL1Seed = True
            if not hasL1Seed:
                print(row_format.format(mds),row_format2.format(matchingPath),GREEN+"PRESENT"+RESET,"but ",RED+"NO L1 SEED"+RESET)
            elif hasL1Seed:
                print(row_format.format(mds),row_format2.format(matchingPath),GREEN+"PRESENT"+RESET,"and ",GREEN+"HAS L1 SEED"+RESET)


# 3) Check the smart prescales of the Express Datasets:
print("-"*64)
for mds in presentMandatoryDatasets:
	if "Express" in mds:
		normalizedDSName = mds.replace("Physics","")
		print(BOLD+normalizedDSName+RESET)
		smartPrescales = getattr(process,"hltPre"+normalizedDSName+"OutputSmart")
		print(smartPrescales.triggerConditions)
		print("\n")
