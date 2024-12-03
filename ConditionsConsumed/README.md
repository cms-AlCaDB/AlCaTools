### Get AlCa conditions from CMSSW at various steps
Run2:
* Run2 conditions:  https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2019

Run3:
* Run3 2022 conditions: https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2022
* Run3 2023 conditions: https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2023
* Run3 2024 conditions: https://twiki.cern.ch/twiki/bin/view/CMS/AlCaDBHLT2024

### Minimal set of instructions
For detailed instructions, please refer to the year-specific twiki links reported above.

Install package:
```
cmsrel CMSSW_X_Y_Z
cd CMSSW_X_Y_Z/src
cmsenv
git clone https://github.com/cms-AlCaDB/AlCaTools.git
cd AlCaTools/ConditionsConsumed
```
Produce cmsDriver logs to be parsed for each step:
```
source runCMSDrivers_[data|mc][year].sh
```
Produce a twiki-like table with conditions consumed in each step:
```
python3 getAlCaCondInGT.py --year [YEAR] --isData [1|0]
```
Command line options:
- `--year`: year for which you are running, default: `2024`
- `--isData`: wheter you are parsing data (`1`) or MC (`0`) logs, default: `0`

### Older instructions:
<details>
<summary> Show old (deprecated) instructions for CMSSW <= 10_6_0 </summary>

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
</details>
