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

### Usually, blindly executing an external file is a security hazard...
HLTMenuName="hlt.py"
L1MenuName="l1prescales.xml"

execfile(HLTMenuName)

L1PrescalesTree = ET.parse(L1MenuName)
root = L1PrescalesTree.getroot()
columnNamesElement = root[0][1][0].text
columnNames = [x.split(":")[1] for x in columnNamesElement.split(",")[1:]]

print process.process
pathnames = process.paths.viewkeys()

pathsVsSeeds = dict()
seedPrescales = dict()
pathPrescales = dict()
L1pathPrescales = dict()

def splitL1seeds(fullSeed):
    l = fullSeed.split(" OR ") # Spaces around to not pick seeds that have OR in their names
    s = [w.strip() for w in l]
    return s


# 0) Get the number of HLT columns
numberOfColumns = len(process.PrescaleService.lvl1Labels)
columnIndexes = range(0,numberOfColumns)
print "HLT menu has",numberOfColumns,"columns"
print "L1 menu has",len(columnNames),"columns"
print "Columns from L1: ",columnNames

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
print "-"*64
for i in process.PrescaleService.prescaleTable:
	# We don't want the Output paths that may be here
	if "Output" in i.pathName.value(): 
		continue
	pathPrescales[i.pathName.value()] = i.prescales.value()
    #print pathPrescales
# 2.1) Add the missing paths, send warnings for missing paths *except* the ones we know are okay
for pathName in pathsVsSeeds.keys():
	if pathName not in pathPrescales.keys():
		pathPrescales[pathName] = [1]*numberOfColumns
		if not("Calibration" in pathName or "HLTriggerFirstPath" in pathName or "HLTriggerFinalPath" in pathName):
			print RED+'WARNING:'+RESET,pathName,"has no defined HLT prescales"
	if len(pathsVsSeeds[pathName]) == 0:
		L1pathPrescales[pathName] = [1]*numberOfColumns
		

# 3) Make the map of seed vs prescales
for row in root[0][1][2]:
    L1seed = row.text.split(",")[0]
    L1prescales = [int(p) for p in row.text.split(",")[1:]]
    seedPrescales[L1seed]=L1prescales

# 4) Extensive check of columns structure
for pathName in pathPrescales:
    numberOfHLTColumns = len(pathPrescales[pathName])
    #print pathName, pathPrescales[pathName]
    for seedName in seedPrescales:
        numberOfL1Columns = len(seedPrescales[seedName])
        #print seedName, seedPrescales[seedName]
        #if (numberOfL1Columns != numberOfHLTColumns):
            #print "ERROR: we found a combination of HLT path and L1 seed that doesn't seem to have compatible number of columns!"

checkForWeirdness = False
print "-"*64
if (checkForWeirdness == False):
	print "Skipping weirdness checks (not relevant for ALCA anyway)"
	
# Check for weirdness in the L1 prescales
if checkForWeirdness:
	for seedName in seedPrescales:
		for columnIndex in columnIndexes[0:]:
			thisPrescale = seedPrescales[seedName][columnIndex]
			nextPrescale = seedPrescales[seedName][columnIndex+1]
			if (thisPrescale < nextPrescale and thisPrescale != 0):
				print "Weird, seed ",seedName," has PS = ",thisPrescale," in column ",columnNames[columnIndex], " and PS = ",nextPrescale," in column ",columnNames[(columnIndex+1)]

# Now analyze each HLT path in detail. Here particularly we will get the
# "effective L1 prescale", i.e., the lowest non-null prescale that feeds
# into the HLT path

for pathName in pathPrescales:
#for pathName in ["HLT_DoubleEle33_CaloIdL_MW_v10"]:
    #print "Checking path",pathName
    if pathName not in pathsVsSeeds.keys():
        print "Path",pathName,"does not have L1 seeding modules"
        continue
    pathSeeds = pathsVsSeeds[pathName]
    #print pathSeeds
    effectiveL1Prescales = list()
    for columnIndex in columnIndexes[0:]:
        # Now we check what kind of path this is
        isL1PrescaledPath = False
        isL1ZeroedPath = True
        isHLTPrescaledPath = False
        isHLTZeroedPath = False

        # Check HLT prescales for this path
        #print "HLT prescale in column ",columnIndex," is ",pathPrescales[pathName][columnIndex]
        if(pathPrescales[pathName][columnIndex] > 1):
            isHLTPrescaledPath = True
        if(pathPrescales[pathName][columnIndex] is 0):
            isHLTZeroedPath = True
        
        smallestNonNullPrescale = 9999999
        largestPrescale = 0
        # Check L1 prescales for this path
        if (len(pathSeeds) is 0):
            continue
        for seedName in pathSeeds:
            thisSeedPrescale = seedPrescales[seedName][columnIndex]
            #print "L1 seed ",seedName," has prescale ",thisSeedPrescale," in column ",columnIndex 
            if (thisSeedPrescale < smallestNonNullPrescale and thisSeedPrescale != 0):
                smallestNonNullPrescale = thisSeedPrescale
            if thisSeedPrescale > largestPrescale:
                largestPrescale = thisSeedPrescale
            if thisSeedPrescale != 0:
                isL1ZeroedPath = False
        # Now we have gone through the prescales of all L1 seeds of the path for this column
        if smallestNonNullPrescale != 1:
            isL1PrescaledPath = True
        
        if checkForWeirdness:
			if (isL1ZeroedPath is True and isHLTZeroedPath is False):
				print "ERROR TYPE ALPHA, path ",pathName," has prescale 0 at L1 but not at HLT for column ",columnIndex 
			if (isL1PrescaledPath is False and isHLTPrescaledPath is True):
				print "ERROR TYPE BETA, path ",pathName," is unprescaled at L1 but not at HLT for column ",columnIndex 
        
        if (largestPrescale is 0):
            effectiveL1Prescales.append(0)
        else:
            effectiveL1Prescales.append(smallestNonNullPrescale)
        L1pathPrescales[pathName] = effectiveL1Prescales



# NOW come the AlCa checks proper


# 1) Do I have all the AlCa datasets?
print "-"*64
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
							 						"HLT_HT450_Beamspot_v*"],
							 "AlCaLumiPixels":["AlCa_LumiPixels_Random_v*",
							 					"AlCa_LumiPixels_ZeroBias_v*"],
							 "AlCaPhiSym":["AlCa_EcalPhiSym_v*",],
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
		print row_format.format(mds),GREEN+"PRESENT"+RESET		
		presentMandatoryDatasets.append(mds)
	else:
		print row_format.format(mds),RED+"ABSENT"+RESET
presentMandatoryDatasets.sort()

# 2) Do the datasets have all paths they should have?
print "-"*64
for mds in presentMandatoryDatasets:
	theDataset = getattr(process.datasets,mds)
	for requestedPath in mandatoryDatasetsAndPaths[mds]:
			pathIsPresent = False
			if len(fnmatch.filter(theDataset,requestedPath)) == 0:
				print row_format.format(mds),row_format2.format(requestedPath),RED+"ABSENT"+RESET
			for matchingPath in fnmatch.filter(theDataset,requestedPath):
				totalPrescales = [l1*hlt for l1,hlt in zip(L1pathPrescales[matchingPath], pathPrescales[matchingPath])]
				print row_format.format(mds),row_format2.format(matchingPath),GREEN+"PRESENT"+RESET,totalPrescales

# 3) Check the smart prescales of the Express Datasets:
print "-"*64
for mds in presentMandatoryDatasets:
	if "Express" in mds:
		normalizedDSName = mds.replace("Physics","")
		print BOLD+normalizedDSName+RESET
		smartPrescales = getattr(process,"hltPre"+normalizedDSName+"OutputSmart")
		print smartPrescales.triggerConditions
		print "\n"
