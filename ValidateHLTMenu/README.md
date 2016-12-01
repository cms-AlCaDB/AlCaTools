# Readme

## Inputs:

   * twiki of AlCaReco Matrix: AlCaRecoMatrix.wiki
   * script : 
      * AlCaRecoTriggerBitsRcdRead_FromTag_cfg.py
      * ValidateHLTMenu.py

## Example to run :

```
python ValidateHLTMenu.py /online/collisions/2016/25ns10e33/v1.0/HLT/V3 AlCaRecoHLTpaths8e29_1e31_v7_hlt 271700
```

   * arguments:
      * argv1 : HLT menu on confDB
      * argv2 : triggerbit tag on condDB
      * argv3 : run number

## Flow : 

```  
cmsRun AlCaRecoTriggerBitsRcdRead_FromTag_cfg.py to dump trigger bit into twiki
dump hlt config from confDB
dump hlt stream/datasets/paths into text file
```
  
read the alcareco matrix, trigger bit twiki, stream/datasets/paths to generate validation text file

## Output 

validation.txt 

for each AlCaReco:
   * list its seed in the trigger bit
   * check whether the AlCa Reco is the in the AlCa Reco matrix
   * check whether the trigger is in the same primary dataset as AlCaReco matrix tells:
      * if yes, list all the satified trigger paths in the same primary dataset as AlCaReco matrix tells
      * if not, list the primary dataset as AlCaReco matrix tells  
   * Also, point out the whether the dataset in AlCaReco matrix is also in the HLT menu

## By-products:
   * triggerBits_AlCaRecoHLTpaths8e29_1e31_v7_hlt.twiki : 
   * trigger bits in the IOV that contains the run number
   * dumpStream.txt: stream/datasets/paths in the HLT menu








