```
# import the part that you want to change
conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v22_offline.db -f frontier://FrontierProd/CMS_CONDITIONS -i AlCaRecoHLTpaths8e29_1e31_v22_offline -t AlCaRecoHLTpaths8e29_1e31_v23_offline -b 272023
# change it
python run_wf.py -f AlCaRecoHLTpaths8e29_1e31_v22_offline.db -t AlCaRecoHLTpaths8e29_1e31_v23_offline
# get the rest of the tag 
conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v23_offline.db -f frontier://FrontierProd/CMS_CONDITIONS -i AlCaRecoHLTpaths8e29_1e31_v22_offline -t AlCaRecoHLTpaths8e29_1e31_v23_offline -e 272022
```