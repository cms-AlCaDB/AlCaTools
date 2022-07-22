# import the part that you want to change
#conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v7_hlt.db -f frontier://FrontierProd/CMS_CONDITIONS -i AlCaRecoHLTpaths8e29_1e31_v7_hlt -t AlCaRecoHLTpaths8e29_1e31_v11_hlt -b 250582 -e 312279
#conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v7_hlt.db -f frontier://FrontierProd/CMS_CONDITIONS -i AlCaRecoHLTpaths8e29_1e31_v7_hlt -t AlCaRecoHLTpaths8e29_1e31_v11_hlt -b 312280
#first IOV of 2018 is 312280

# change it
#python run_wf.py -f AlCaRecoHLTpaths8e29_1e31_v7_hlt.db -t AlCaRecoHLTpaths8e29_1e31_v11_hlt
# get the rest of the tag 
#conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v23_offline.db -f frontier://FrontierProd/CMS_CONDITIONS -i AlCaRecoHLTpaths8e29_1e31_v22_offline -t AlCaRecoHLTpaths8e29_1e31_v23_offline -e 272022


conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v11_hlt_All.db -f sqlite_file:AlCaRecoHLTpaths8e29_1e31_v11_hlt_1_to_247695.db  -i AlCaRecoHLTpaths8e29_1e31_v11_hlt -t AlCaRecoHLTpaths8e29_1e31_v11_hlt -b 1 -e 247695

#conddb [--db target]] copy [object1] [object2] [--destdb DB][--from S][--to E][--type T]
conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v11_hlt_All.db -f sqlite_file:AlCaRecoHLTpaths8e29_1e31_v7_hlt_250582_306552.db  -i AlCaRecoHLTpaths8e29_1e31_v11_hlt -t AlCaRecoHLTpaths8e29_1e31_v11_hlt -b 250582 -e 306552

conddb_import -c sqlite_file:AlCaRecoHLTpaths8e29_1e31_v11_hlt_All.db -f sqlite_file:AlCaRecoHLTpaths8e29_1e31_v11_hlt_312280_to_327051.db  -i AlCaRecoHLTpaths8e29_1e31_v11_hlt -t AlCaRecoHLTpaths8e29_1e31_v11_hlt -b 314406 -e 327051
