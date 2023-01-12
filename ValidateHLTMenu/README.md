# Readme

Documented at: https://twiki.cern.ch/twiki/bin/view/CMS/ValidateHLTMenu

## Inputs:

   * twiki of AlCaReco Matrix: [AlCaRecoMatrix.wiki](https://twiki.cern.ch/twiki/bin/view/CMS/AlCaRecoMatrix)
   * script : 
      * AlCaRecoTriggerBitsRcdRead_FromTag_cfg.py
      * ValidateHLTMenu.py

## Setup (in LXLPUS):

```

cmsrel CMSSW_12_3_3_patch1
cd CMSSW_12_3_3_patch1/src/
cmsenv
git clone https://github.com/cms-AlCaDB/AlCaTools
cd AlCaTools/ValidateHLTMenu
```

## Example to run:

```
python3 ValidateHLTMenu.py {} {} {} {}
```

* arguments:
   * argv1 : HLT menu on confDB
   * argv2 : triggerbit tag on condDB
   * argv3 : AlCaRecoMatrix configuration (express, prompt)
   * argv4 : run number

### Express Configuration

```
python3 ValidateHLTMenu.py adg:/cdaq/special/2022/900GeVCollisionsTest/v1.0/HLT/V2 AlCaRecoHLTpaths8e29_1e31_v11_hlt express 351810
```

### Prompt Configuration

```
python3 ValidateHLTMenu.py adg:/cdaq/special/2022/900GeVCollisionsTest/v1.0/HLT/V2 AlCaRecoHLTpaths8e29_5e33_v7_prompt prompt 351635
```

## Flow : 

```  
cmsRun AlCaRecoTriggerBitsRcdRead_FromTag_cfg.py to dump trigger bit into twiki
dump hlt config from confDB
dump hlt stream/datasets/paths into text file
```

Read the alcareco matrix, trigger bit twiki, stream/datasets/paths to generate validation text file and validation json file

## Output 

results/validation-{configuration}.txt and results/valation-{configuration}.json

for each AlCaReco:
   * list its seed in the trigger bit
   * check whether the AlCa Reco is the in the AlCa Reco matrix
   * check whether the trigger is in the same primary dataset as AlCaReco matrix tells:
      * if yes, list all the satified trigger paths in the same primary dataset as AlCaReco matrix tells
      * if not, list the primary dataset as AlCaReco matrix tells  
   * Also, point out the whether the dataset in AlCaReco matrix is also in the HLT menu

## By-products:
   * triggerBits_{TriggerBitTag}.twiki : 
   * trigger bits in the IOV that contains the run number
   * HLTMenu-dumpStream.txt: stream/datasets/paths in the HLT menu








