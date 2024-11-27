############################################
# get AlCa conditions consumed in the CMSSW
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCalAliTrigger2023
############################################

import json
import argparse
from contextlib import ExitStack

def checkTagInJson(tag, data):
    # processing string with "/" separator from tagFile
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
    unique_rows = set()

# Open files in advance using context managers
    with ExitStack() as stack:
        files = [stack.enter_context(open(file_, 'r')) for file_ in json_files]
        data_list = [json.load(file_content) for file_content in files]

# Process data
    for data in data_list:
        for record, label_info_list in data.items():
            for label_info in label_info_list:
                label = label_info.get('label', '')
                row = f"{record} / {label}"
                unique_rows.add(row)

# Sort and write the sorted lines to a file
    with open(tagFile, 'w') as new_tagFile:
        new_tagFile.write('\n'.join(sorted(unique_rows, reverse=False)))


def main():
    parser = argparse.ArgumentParser(
        description='Usage: python3 getAlCaCondInGT.py [options] \n')
    parser.add_argument('-d', '--data', dest='isData', action='store_true',
                        default=False, help='Enter --data -d for data, False for MC. Default: False')
    args = parser.parse_args()

    tagFile = "allAlCaTags.txt"
    if args.isData:
        jsonFiles = [
            "output_step1_L1.json",  # step1_L1
            "output_step2_HLT.json",  # step2_HLT
            "output_step3_AOD.json",  # step3_AOD
            "output_step4_MINIAOD.json",  # step4_MINIAOD
            "output_step5_NANOAOD.json",  # step5_NANOAOD
        ]
    else:
        jsonFiles = [
            "output_step1_GEN.json",  # step1_GEN
            "output_step2_SIM.json",  # step2_SIM
            "output_step3_DIGI.json",  # step3_DIGI
            "output_step4_L1.json",  # step4_L1
            "output_step5_DIGI2RAW.json",  # step5_DIGI2RAW
            "output_step6_HLT.json",  # step6_HLT
            "output_step7_AODSIM.json",  # step7_AODSIM
            "output_step8_MINIAODSIM.json",  # step8_MINIAODSIM
            "output_step9_NANOAODSIM.json",  # step9_NANOAODSIM

            # Add remaining JSON filenames if available
        ]

    output_table = "DATA" if args.isData else "MC"
    tableTitle = "|Tags|L1|HLT|AOD|MINIAOD|NANOAOD|\n" if args.isData else "|Tags|GEN|SIM|DIGI|L1|DIGI2RAW|HLT|AOD|MINIAOD|NANOAOD|\n"

    updateTagFile(tagFile, jsonFiles)

    printAllRow(tagFile, jsonFiles, output_table, tableTitle)


if __name__ == '__main__':
    main()
