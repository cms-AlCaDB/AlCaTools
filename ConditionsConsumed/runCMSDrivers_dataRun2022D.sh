####
# 1 - L1
####

echo "------------------------------"
echo "Running step-1/5: L1"
echo "------------------------------"
cmsDriver.py step1  -s L1REPACK:Full --conditions auto:run3_hlt_relval --data  --eventcontent FEVTDEBUGHLT --datatier FEVTDEBUGHLT --era Run3 -n 10  --filein file:/eos/cms/store/data/Run2022D/ZeroBias/RAW/v1/000/357/538/00000/1d71e6ef-2992-459d-a127-4fcfeaef76ec.root --fileout file:step1.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' > output_step1_L1.log

####
# 2 - HLT
####

echo "------------------------------"
echo "Running step-2/5: HLT"
echo "------------------------------"
cmsDriver.py step2  --process reHLT -s HLT:@relval2022 --conditions auto:run3_hlt_relval --data  --eventcontent FEVTDEBUGHLT --datatier FEVTDEBUGHLT --era Run3 -n 10  --filein file:step1.root --fileout file:step2.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' > output_step2_HLT.log

####
# 3 - AOD (RAW2DIGI,L1Reco,RECO)
####

echo "------------------------------"
echo "Running step-3/5: AOD"
echo "------------------------------"
cmsDriver.py step3  --conditions auto:run3_data_relval -s RAW2DIGI,L1Reco,RECO --datatier RECO --eventcontent RECO --data  --process reRECO --scenario pp --era Run3 --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 -n 10  --filein  file:step2.root  --fileout file:step3.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' > output_step3_AOD.log

####
# 4 - MiniAOD
####

echo "------------------------------"
echo "Running step-4/5: MINIAOD"
echo "------------------------------"
cmsDriver.py step4  --conditions auto:run3_data_relval -s PAT --datatier MINIAOD --eventcontent MINIAOD --data  --scenario pp --era Run3 --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 -n 10  --filein  file:step3.root  --fileout file:step4.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' > output_step4_MINIAOD.log 
 
####
# 5 - NanoAOD
####

echo "------------------------------"
echo "Running step-5/5: NANOAOD"
echo "------------------------------"
cmsDriver.py step5  --conditions auto:run3_data_relval -s NANO:PhysicsTools/NanoAOD/V10/nano_cff --datatier MINIAOD --eventcontent MINIAOD --data  --scenario pp --era Run3 --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 -n 10  --filein  file:step4.root  --fileout file:step5.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' > output_step5_NANOAOD.log  
