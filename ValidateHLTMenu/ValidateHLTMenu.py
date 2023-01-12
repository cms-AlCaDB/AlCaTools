#!/bin/env python3

# This script dumps the content of the AlCaRecoTriggerBits tag provided in input and checks that all the hlt selection paths are selecting some triggers
# by looking at the HLT menu also provided as input. It does the mapping between AlCaRecos and Primary Datasets with the AlCaRecoMatrix.
# It produces an output file called validation.txt and validation.json with the list of matched triggers including prescales.

import sys
import os
import json
import re

CMSSW_VERSION = os.getenv("CMSSW_VERSION")

if CMSSW_VERSION is None:
    raise ValueError("CMSSW_VERSION environment variable not found.")

TEMPLATE_FNAME = "AlCaRecoTriggerBitsRcdRead_FromTag_cfg.py"
HLT_MENU_DUMP_FNAME = "HLTMenu-dumpStream.txt"


def read_alca_reco_matrix(fpath):
    """
    Open AlcaReco Matrix
    """
    AlCaRecoMatrix = {}
    for line in open(fpath):
        if line.find("*Primary Dataset*") != -1:
            continue
        splittedLine = line.split("|")
        if len(splittedLine) > 2:
            for AlCaReco in splittedLine[2].split(","):
                # Alca reco attached to a PD
                if AlCaReco.strip() not in AlCaRecoMatrix:
                    AlCaRecoMatrix[AlCaReco.strip()] = []
                    AlCaRecoMatrix[AlCaReco.strip()].append(splittedLine[1].strip())
                # If alca reco already attached to another PD, append the new PD
                else:
                    AlCaRecoMatrix[AlCaReco.strip()].append(splittedLine[1].strip())
    return AlCaRecoMatrix


def read_hlt_menu(fpath):
    """
    Open HLTMenu
    """
    HLTMenu = []
    for line in open(fpath):
        if line.startswith("    dataset "):
            HLTMenu.append([])
            HLTMenu[len(HLTMenu)-1].append(line.strip())
        if len(HLTMenu) > 0:
            HLTMenu[len(HLTMenu)-1].append(line.strip())
    return HLTMenu


def read_triggerbits(fpath):
    """
    Open AlCaRecOTriggerBits dump
    """
    AlCaRecoTriggerBits = {}
    isAlCaRecoName = True
    for line in open(fpath):
        if line.find("|") == -1:
            continue
        if isAlCaRecoName:
            AlCaReco = line.split('|')[1].strip().strip("\'")
            isAlCaRecoName = False
        else:
            TriggerBitKey = line.split('|')[1].strip().strip("\'").strip()
            HLTPaths = line.split('|')[2].strip().strip("\'").strip()
            AlCaRecoTriggerBits[TriggerBitKey] = HLTPaths
    return AlCaRecoTriggerBits


def find_hlt_path(PrimaryDataset, HLTpath, HLTMenu, output_file):
    """
    Need to check: trigger names matching the ones in the AlCaRecoTriggerBits, 
    if they are prescaled, if all the PDs required in the alcareco matrix match or not.
    """
    HLTpath = HLTpath.replace("*", "(.*)")
    matching_triggers = []
    PDmatch = ""

    for AlCaRecoPD in PrimaryDataset:
        # loop over all primary dataset that an ALCARECO is in
        for PD in HLTMenu:

            if PD[0].find(f"dataset {AlCaRecoPD}") == -1:
                continue

            if PDmatch == "":
                PDmatch = AlCaRecoPD
            else:
                PDmatch = f"{PDmatch},{AlCaRecoPD}"
                
            for path in PD:
                if path.startswith("dataset") or path.startswith("***") or path.startswith("stream"):
                    continue
                if HLTpath == "*":
                    matching_triggers.append(path.rstrip("\n"))
                else:
                    matches = list(re.finditer(HLTpath, path, re.MULTILINE))
                    if len(matches) > 0:
                        matching_triggers.append(path.rstrip("\n"))

    if len(matching_triggers) == 0:
        output_file.write(f"\nError: no matching triggers found for selection string {HLTpath}\n\n")
        return False, []
    else:
        output_file.write(f"The following matching triggers were found in the Primary Dataset {PDmatch} for trigger selection string \"{HLTpath}\":\n\n")
        for trigger in matching_triggers:
            output_file.write(trigger+"\n")
        output_file.write("\n")
        return True, matching_triggers


def find_pd(primary_dataset):
    """
    """
    pd_match = ""
    pd_unmatch = ""
    for AlCaRecoPD in primary_dataset:
        isInHLTMenu = False
        for PD in HLTMenu:
            print(f"PD in HLT menu {PD[0]}")
            isInHLTMenu = True
            if PD[0].find(f"dataset {AlCaRecoPD}") == -1:
                continue
            if pd_match == "":
                pd_match = AlCaRecoPD
            else:
                pd_match = f"{pd_match},{AlCaRecoPD}"
        if isInHLTMenu == False:
            if pd_unmatch == "":
                pd_unmatch = AlCaRecoPD
            else:
                pd_unmatch = f"{pd_unmatch},{AlCaRecoPD}"
    return pd_match, pd_unmatch


def analyze(AlCaRecoMatrix, AlCaRecoTriggerBits, configuration, HLTMenu, hlt_menu_name, alca_reco_hlt_paths_tag, run_number):
    """
    """
    output_file = open(f"results/validation-{configuration}.txt", "w")
    output = {TriggerBitKey: {} for TriggerBitKey in AlCaRecoTriggerBits}
    result = {
        "Metadata": {
            "CMSSW_VERSION": CMSSW_VERSION,
            "HLTMenuName": hlt_menu_name,
            "AlCaRecoHLTPathsTag": alca_reco_hlt_paths_tag,
            "Configuration": configuration,
            "RunNumber": run_number,
        },
        "Analysis": {
            "AlCaRecoHasNoKeys": {},
            "AlCaRecoNotInMatrix": {},
            "AlCaRecoMatch": {}
        },
        "ValidationMissing": [
            f"| *TriggerBitKey* | *PrimaryDatasets* | *MissingHLTPaths* |"
        ],
        "CrossCheck": {
            "AlCaRecoMatrix (AlCaRecos to be run: PrimaryDataset)": AlCaRecoMatrix,
            "AlCaRecoTriggerBits (TriggerBitKey: HLTPaths)": AlCaRecoTriggerBits
        }
    }

    for TriggerBitKey, HLTPaths in AlCaRecoTriggerBits.items():

            output_file.write("\n\n---------------------------------------------------------------------------------------------------\n")
            output_file.write("Checking AlCaReco: \"" + TriggerBitKey + "\" with selection string: \"" + HLTPaths + "\"\n")
            output_file.write("---------------------------------------------------------------------------------------------------\n\n")

            alca_reco_has_keys = HLTPaths != ""
            is_in_matrix = TriggerBitKey in AlCaRecoMatrix
            primary_dataset = AlCaRecoMatrix.get(TriggerBitKey)

            output[TriggerBitKey]["AlcaRecoHasKeys"] = alca_reco_has_keys
            output[TriggerBitKey]["IsInMatrix"] = is_in_matrix
            output[TriggerBitKey]["PrimaryDataset"] = primary_dataset
            output[TriggerBitKey]["HLTPaths"] = HLTPaths
            output[TriggerBitKey]["MatchingTriggers"] = []
            output[TriggerBitKey]["MissingTriggers"] = []

            if is_in_matrix is False:
                output_file.write("This AlCaReco is not in the matrix\n")
                continue

            if alca_reco_has_keys:
                for HLTPath in HLTPaths.split(","):
                    print(f"Trigger {HLTPath} for AlCaReco {TriggerBitKey}")
                    HLTPath = HLTPath.strip().strip("\'")
                    is_matching, matching_triggers = find_hlt_path(primary_dataset, HLTPath, HLTMenu, output_file)
                    if is_matching:
                        output[TriggerBitKey]["MatchingTriggers"].append({
                            "HLTPath": HLTPath,
                            "HasMatchingTriggers": is_matching,
                            "MatchingTriggers": matching_triggers
                        })
                    else:
                        output[TriggerBitKey]["MissingTriggers"].append({
                            "HLTPath": HLTPath,
                            "HasMatchingTriggers": is_matching,
                            "MatchingTriggers": matching_triggers
                        })            
            else:
                pd_match, pd_unmatch = find_pd(primary_dataset)
                output[TriggerBitKey]["PDMatch"] = pd_match
                output[TriggerBitKey]["PDUnMatch"] = pd_unmatch
                if pd_match == "":
                    output_file.write(f"This AlCaReco has no keys. But It is either disabled or accepting everything but the PD {pd_unmatch} not in the HLT menu\n")
                    output[TriggerBitKey]["Content"] = f"This AlCaReco has no keys. It is either disabled or accepting everything but the PD {pd_unmatch} not in the HLT menu"
                elif pd_unmatch == "":
                    output_file.write(f"This AlCaReco has no keys. It is either disabled or accepting everything in the PD {pd_match} in the menu\n")
                    output[TriggerBitKey]["Content"] = f"This AlCaReco has no keys. It is either disabled or accepting everything in the PD {pd_match} in the menu"
                else:
                    output_file.write(f"This AlCaReco has no keys. It is either disabled or accepting everything in the PD {pd_match} in the menu but PD {pd_unmatch} not the menu\n")
                    output[TriggerBitKey]["Content"] = f"This AlCaReco has no keys. It is either disabled or accepting everything in the PD {pd_match} in the menu but PD {pd_unmatch} not the menu"

    output_file.close()
    for TriggerBitKey, out in output.items():
        if out.get("AlcaRecoHasKeys") is False:
            result["Analysis"]["AlCaRecoHasNoKeys"][TriggerBitKey] = out
        elif out.get("IsInMatrix") is False:
            result["Analysis"]["AlCaRecoNotInMatrix"][TriggerBitKey] = out
        else:
            result["Analysis"]["AlCaRecoMatch"][TriggerBitKey] = out

    for TriggerBitKey, out in result["Analysis"]["AlCaRecoMatch"].items():
        if len(out.get("MissingTriggers")) > 0:
            PrimaryDatasets = ", ".join(out.get("PrimaryDataset"))
            MissingHLTPaths = ", ".join([o.get("HLTPath") for o in out.get("MissingTriggers")])
            out_str = f"| {TriggerBitKey} | {PrimaryDatasets} | {MissingHLTPaths} |"
            result["ValidationMissing"].append(out_str)

    print(f"Comparison done. Please, check the validation-{configuration}.txt file for details.")

    with open(f"results/validation-{configuration}.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: ValidateHLTMenu.py HLTMenu AlCaRecoHLTpathsTag [RunNumber]")
        print("Example: ./ValidateHLTMenu.py /online/collisions/2012/7e33/v2.1/HLT AlCaRecoHLTpaths8e29_5e33_v2_prompt prompt")
        print("If no run number is provided the number 1000000 will be used.")
        sys.exit()

    hlt_menu_name = sys.argv[1]
    alca_reco_hlt_paths_tag = sys.argv[2]
    configuration = sys.argv[3]
    run_number = sys.argv[4] if len(sys.argv) == 5 else 1000000

    alca_reco_matrix_fname = f"AlCaRecoMatrix-{configuration}.wiki"

    # Create new cfg file from template
    validation_fname = f'{alca_reco_hlt_paths_tag}_BitsRcdRead_FromTag_cfg.py'
    cmd = f'cp {TEMPLATE_FNAME} {validation_fname}'
    os.system(cmd)
    triggerbits_output_file = f"triggerBits_{alca_reco_hlt_paths_tag}.twiki"

    # Overwrite `alca_reco_hlt_paths_tag` from validation file
    cmd = f"sed -i 's/alca_reco_hlt_paths_tag = None/alca_reco_hlt_paths_tag = \"{alca_reco_hlt_paths_tag}\"/g' {validation_fname}"
    os.system(cmd)

    # Overwrite `run_number` from validation file
    cmd = f"sed -i 's/run_number = None/run_number = {run_number}/g' {validation_fname}"
    os.system(cmd)

    # Run cfg with cmsRun to generate twiki
    cmd = f"cmsRun {validation_fname}"
    os.system(cmd)

    # Dump menu
    cmd1 = f'hltGetConfiguration {hlt_menu_name} --unprescale --offline > hlt.py'
    cmd2 = f'hltDumpStream hlt.py > {HLT_MENU_DUMP_FNAME}'
    os.system(cmd1)
    os.system(cmd2)

    print("Validating AlCaRecoTriggerBits with HLT menu")
    print("Extract the list of PDs and associated triggers from the menu")

    AlCaRecoMatrix = read_alca_reco_matrix(alca_reco_matrix_fname)
    HLTMenu = read_hlt_menu(HLT_MENU_DUMP_FNAME)
    AlCaRecoTriggerBits = read_triggerbits(triggerbits_output_file)
    output = analyze(AlCaRecoMatrix, AlCaRecoTriggerBits, configuration, HLTMenu, hlt_menu_name, alca_reco_hlt_paths_tag, run_number)
