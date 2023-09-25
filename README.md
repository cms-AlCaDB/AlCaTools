# AlCa
Tools for CMS Alignment and Calibration checks

Check it out via:

```
git clone git@github.com:cms-AlCaDB/AlCaTools.git
```
## Important commands for conddb
### conddb: Usage
  * conddb --help
  * conddb list --h

### conddb: DB Target
  * conddb --db myfile.db
  * conddb --db pro
  * conddb --db dev

### conddb: Search 
  * conddb search RunInfo
  * conddb search CMSSW_8_0_X

### conddb: List db Content
  * conddb --db dev listTags
  * conddb listGTs
  * conddb listGTsForTag runinfo_31X_hlt
  * conddb --db test_output.db list fillinfo_test

### conddb: List Tag/GlobalTag Content
  * conddb --noLimit list runinfo_31X_hlt
  * conddb list runinfo_31X_hlt --limit 200
  * conddb list 80X_dataRun2_HLT_v0 --long

### conddb: Dump payload or tag content
  * conddb dump d55a178a9e56ce9e33f3b2bbeda9fd836c46b5c5

### conddb: Show the difference between Tags or Global Tags
  * conddb --db runinfo.db diff runinfo_1 runinfo_2 --long
  * conddb diff 76X_dataRun2_HLT_frozen_v11 80X_dataRun2_HLTHI_v0

### conddb: Import or copy the Tag/payload 
  * conddb [--db target]] copy [object1] [object2] [--destdb DB][--from S][--to E][--type T]
  * conddb_import -c destdb -f sourcedb -i inputTag -t destTag -b begin -e end
  * conddb_import -c sqlite:runinfo.db -f frontier://FrontierProd/CMS_CONDITIONS -i runinfo_31X_hlt -t runinfo_1 -b 268283 -e 268285

