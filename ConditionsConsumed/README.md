### Get AlCa conditions from CMSSW at various steps
* Run2 conditions:  https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2019
* Run3 2022 conditions: https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2022
* Run3 2023 conditions: https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2023

## Setup CMSSW (old, see instructions for any given period in the links here above)
* ssh user@lxplus7.cern.ch
* export SCRAM_ARCH=slc7_amd64_gcc700
* cmsrel CMSSW_10_6_0_pre1
* cd CMSSW_10_6_0_pre1/src/

## Setup cmsDrivers (old, see instructions for any given period in the links here above)
* git clone git@github.com:ravindkv/MyAlCaTools.git
* ./runCMSDrivers.sh
* python getAlCaCondInGT.py

The final output will be stored in outputForTwiki.txt

Please note that the following command: 
--customise_commands='process.GlobalTag.DumpStat = cms.untracked.bool(True)'
is used to dump the conditions consumed in the GT.
