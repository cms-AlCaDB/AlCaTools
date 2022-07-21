
############################################
# get AlCa conditions consumed in the CMSSW
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCalAliTrigger2019
############################################

#input
isData = False
tagFile = "allAlCaTags.txt"
logFiles = []
if(isData):
    logFiles.append("output_step1_L1.log")
    logFiles.append("output_step2_HLT.log")
    logFiles.append("output_step3_AOD.log")
    logFiles.append("output_step4_MINIAOD.log")
    logFiles.append("output_step5_NANOAOD.log")
else:
    logFiles.append("output_step1_GEN.log")
    logFiles.append("output_step2_SIM.log")
    logFiles.append("output_step3_DIGI.log")
    logFiles.append("output_step4_L1.log")
    logFiles.append("output_step5_DIGI2RAW.log")
    logFiles.append("output_step6_HLT.log")
    logFiles.append("output_step7_AODSIM.log")
    logFiles.append("output_step8_MINIAODSIM.log")
    logFiles.append("output_step9_NANOAODSIM.log")

#output
if(isData):
    tableTitle = "|Tags|L1|HLT|AOD|MINIAOD|NANOAOD|\n"
else:
    tableTitle = "|Tags|GEN|SIM|DIGI|L1|DIGI2RAW|HLT|AOD|MINIAOD|NANOAOD|\n"

outputForTwiki = open("outputForTwiki.txt", 'w')
def checkTagInFile(tag, logFile):
    found = False
    checkTagLine =0
    foundTag = False
    foundPayload = False
    for i, line in enumerate(open(logFile)):
        #print i, line
        if tag.strip() in line.strip():
            foundTag = True
            checkTagLine = i
            continue
        if foundTag and "payloadIds" in line and (i == checkTagLine + 2):
            foundPayload = True
        if  foundTag and foundPayload and len(line.split(" ")) > 5 and (i == checkTagLine+3):
            found = True
    if(found):
        #return "Y"
        return "%GREEN% Yes %ENDCOLOR%"
    else:
        return ""

def getOneRow(tag, logFiles):
    rowName = "|" +tag.strip()
    for file_ in logFiles:
        checkTagInFile_ = checkTagInFile(tag, file_)
        rowName = rowName + " | " + checkTagInFile_
    return rowName + " | \n"

def printAllRow(tagFile, logFiles, outForTwiki):
    outForTwiki.write(tableTitle)
    for tag in open(tagFile):
        getOneRow_ = getOneRow(tag, logFiles)
        print getOneRow_
        outForTwiki.write(getOneRow_)

printAllRow(tagFile, logFiles, outputForTwiki)
