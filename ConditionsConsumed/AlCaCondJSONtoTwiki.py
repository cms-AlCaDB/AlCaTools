############################################
# get AlCa conditions consumed in the CMSSW
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCalAliTrigger2023
############################################

import json
import argparse

def checkTagInJson(tag, data):
    #processing string with "/" separator from tagFile
    stripped_tag = tag.split('/')[0].strip()
    requested_label = tag.split('/')[1].strip()
    for record in data.get(stripped_tag, []):
        if requested_label in record.get('label', '') and record.get('timeLookupPayloadIds', []):
            return "%GREEN% Yes %ENDCOLOR%"
    return ""

def getOneRow(tag, jsonFiles):
    rowName = "|" + tag.strip()
    for file_ in jsonFiles:
        with open(file_, 'r') as file:
            data = json.load(file)
            checkTagInFile_ = checkTagInJson(tag, data)
            rowName = rowName + " | " + checkTagInFile_
    return rowName + " | \n"

def printAllRow(tagFile, jsonFiles, output_table, tableTitle):
    with open(f"outputForTwiki_{output_table}.txt", 'w') as outForTwiki, open(tagFile, 'r') as tag_file: 
        outForTwiki.write(tableTitle)
        for tag in tag_file:
            getOneRow_ = getOneRow(tag, jsonFiles)
            outForTwiki.write(getOneRow_)

def updateTagFile(tagFile, json_files):
    added_rows = set() 
    with open(tagFile, 'w') as new_tagFile:
        for file_ in json_files:
            with open(file_, 'r') as file_content:
                data = json.load(file_content)
                for record, label_info_list in data.items():
                    for label_info in label_info_list:
                        label = label_info.get('label', '')
                        row = f"{record} / {label}"
                        if row not in added_rows: 
                            new_tagFile.write(f"{row}\n")
                            added_rows.add(row) 



def main():
    parser = argparse.ArgumentParser(description='Usage: python3 getAlCaCondInGT.py [options] \n')
    parser.add_argument('-d', '--data', dest='isData', action='store_true', default=False, help='Enter --data -d for data, False for MC. Default: False')
    args = parser.parse_args()


    tagFile = "allAlCaTags.txt"
    if args.isData:
        jsonFiles = [
        "step1_output.json", #step1_L1
        "step2_output.json", #step2_HLT
        "step3_output.json", #step3_AOD
        "step4_output.json", #step4_MINIAOD
        "step5_output.json", #step5_NANOAOD
        ]
    else:
        jsonFiles = [
        "step1_output.json", #step1_GEN   
        "step2_output.json", #step2_SIM
        "step3_output.json", #step3_DIGI
        "step4_output.json", #step4_L1
        "step5_output.json", #step5_DIGI2RAW
        "step6_output.json", #step6_HLT
        "step7_output.json", #step7_AODSIM
        "step8_output.json", #step8_MINIAODSIM
        "step9_output.json", #step9_NANOAODSIM
        #Add remaining JSON filenames if available
        ]

    output_table = "DATA" if args.isData else "MC"
    tableTitle = "|Tags|L1|HLT|AOD|MINIAOD|NANOAOD|\n" if args.isData else "|Tags|GEN|SIM|DIGI|L1|DIGI2RAW|HLT|AOD|MINIAOD|NANOAOD|\n"
    
    updateTagFile(tagFile, jsonFiles)

    printAllRow(tagFile, jsonFiles, output_table, tableTitle)

if __name__ == '__main__':
    main()
