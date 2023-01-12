
############################################
# get AlCa conditions consumed in the CMSSW
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCalAliTrigger2022
############################################
import os
import sys
import optparse

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

def printAllRow(tagFile, logFiles, outForTwiki, tableTitle):
    outForTwiki.write(tableTitle)
    for tag in open(tagFile):
        getOneRow_ = getOneRow(tag, logFiles)
        #print (getOneRow_)
        outForTwiki.write(getOneRow_)

def main():
    
    #Default input
    defaultData = False
    
    parser = optparse.OptionParser(usage = 'Usage: python3 getAlCaCondInGT.py [options] \n')

    parser.add_option('-d', '--data',
                      dest = 'isData',
                      default = defaultData,
                      help = 'enter True for data, False for MC. Default: False')

    (options, arguments) = parser.parse_args()

    #isData = False
    output_table = "MC" 
    tagFile = "allAlCaTags.txt"
    logFiles = []
    if(options.isData):
        logFiles.append("output_step1_L1.log")
        logFiles.append("output_step2_HLT.log")
        logFiles.append("output_step3_AOD.log")
        logFiles.append("output_step4_MINIAOD.log")
        logFiles.append("output_step5_NANOAOD.log")
    else:
        logFiles.append("output_step2_SIM.log")
        logFiles.append("output_step3_DIGI.log")
        logFiles.append("output_step4_L1.log")
        logFiles.append("output_step5_DIGI2RAW.log")
        logFiles.append("output_step6_HLT.log")
        logFiles.append("output_step7_AODSIM.log")
        logFiles.append("output_step8_MINIAODSIM.log")
        logFiles.append("output_step9_NANOAODSIM.log")

    #output
    if(options.isData):
        output_table = "DATA"
        tableTitle = "|Tags|L1|HLT|AOD|MINIAOD|NANOAOD|\n"
    else:
        tableTitle = "|Tags|GEN-SIM|DIGI|L1|DIGI2RAW|HLT|AOD|MINIAOD|NANOAOD|\n"

    outputForTwiki = open(f"outputForTwiki_{output_table}.txt", 'w')

    printAllRow(tagFile, logFiles, outputForTwiki, tableTitle)

if __name__ == '__main__':
    main()

