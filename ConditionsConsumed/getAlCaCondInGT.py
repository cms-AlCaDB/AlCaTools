
############################################
# get AlCa conditions consumed in the CMSSW
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCalAliTrigger2022
############################################
import os
import re
import sys
import optparse

def checkTagInFile(tag, logFile):
    checkTagLine = 0
    foundTag = False
    foundPayload = False
    foundConsumed = False

    for i, line in enumerate(open(logFile)):
        if line.startswith(tag.strip()):
            foundTag = True
            checkTagLine = i
            continue
        if foundTag and "payloadIds" in line and (i == checkTagLine + 2):
            foundPayload = True
        if  foundTag and foundPayload and len(line.split(" ")) > 5 and (i == checkTagLine+3):
            foundConsumed = True

    if(foundConsumed):
        return "%GREEN% Yes %ENDCOLOR%"
    else:
        return ""

def escape_wikiwords(text):
    # Use a regular expression to find words starting with a capital letter
    return re.sub(r'\b([A-Z][a-zA-Z0-9]*)', r'!\1', text)

def getOneRow(tag, logFiles):
    escaped_tag = escape_wikiwords(tag.strip())
    rowName = "|" + escaped_tag
    for file_ in logFiles:
        checkTagInFile_ = checkTagInFile(tag, file_)
        rowName = rowName + " | " + checkTagInFile_
    return rowName + " |\n"

def printAllRow(tagFile, logFiles, outForTwiki, tableTitle):
    for file_ in logFiles:
        outfile = open(tagFile, "w")
        with open(file_) as f:
            lines = f.readlines()
            for line in lines:
                if re.search(r'frontier', line):
                    newline = line.split(': frontier:')[0]
                    outfile.write(newline+'\n')
    outfile.close()

    outForTwiki.write(tableTitle)
    for tag in open(tagFile):
        getOneRow_ = getOneRow(tag, logFiles)
        outForTwiki.write(getOneRow_)

def main():

    # Command line options
    parser = optparse.OptionParser(usage = 'Usage: python3 getAlCaCondInGT.py [options] \n')
    parser.add_option('-d', '--isData',
                      dest = 'isData',
                      default = 0,
                      type = int,
                      help = 'enter 1 for data, 0 for MC. Default: 0')
    parser.add_option('-y', '--year',
                      dest = 'year',
                      default = '2024',
                      type = int,
                      help = 'year. Default: 2024')
    (options, arguments) = parser.parse_args()

    # cmsDriver log files to be parsed
    logFiles = []
    if (options.isData):
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

    # Output configurables
    if (options.isData):
        workflow = "data"
        tableTitle = "|Tags|L1|!HLT|!AOD|MINIAOD|NANOAOD|\n"
    else:
        workflow = "mc"
        tableTitle = "|Tags|GEN|SIM|DIGI|L1|!DIGI2RAW|!HLT|!AOD|MINIAOD|NANOAOD|\n"

    # Print in twiki-like table which conditions are consumed for all steps
    outputForTwiki = open(f"outputForTwiki_{workflow}{options.year}.txt", 'w')
    printAllRow(f"allAlCaTags_{workflow}{options.year}.txt", logFiles, outputForTwiki, tableTitle)

if __name__ == '__main__':
    main()

