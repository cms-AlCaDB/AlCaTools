#1: L1
echo "------------------------------"
echo "Running step-1/5: L1"
echo "------------------------------"
cmsDriver.py step1  --conditions auto:run3_hlt_relval -n 5 --era Run3_2023 -s L1REPACK:Full --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein /store/data/Run2023D/JetMET0/RAW/v1/000/369/978/00000/00b9eba7-c847-465b-a6de-98bceae93613.root --fileout output_step1_L1.root --customise_commands="process.load('Configuration.StandardSequences.Digi_cff') \n process.GlobalTag.DumpStat =cms.untracked.bool(True)" --outputCommands "keep *" |& tee output_step1_L1.log

#2: HLTlt
echo "------------------------------"
echo "Running step-2/5: HLT"
echo "------------------------------"
cmsDriver.py step2  --conditions auto:run3_hlt_relval -n 5 --era Run3_2023 -s HLT:@relval2023 --processName HLT2 --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein file:output_step1_L1.root --fileout output_step2_HLT.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step2_HLT.log
#cmsDriver.py step2  --conditions auto:run3_hlt_relval -n 5 --era Run3_2023 -s HLT:@relval2023 --processName HLT2 --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein file:output_step1_L1.root --fileout output_step2_HLT.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *, drop  *_hlt*Legacy_*_*" |& tee output_step2_HLT.log

#3 AOD (RAW2DIGI,L1Reco,RECO)
echo "------------------------------"
echo "Running step-3/5: AOD"
echo "------------------------------"
cmsDriver.py step3 --conditions auto:run3_data_prompt_relval -n 5 --era Run3_2023 -s RAW2DIGI,L1Reco,RECO --data --datatier AOD --eventcontent AOD --filein file:output_step2_HLT.root --fileout output_step3_AOD.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 |& tee output_step3_AOD.log

#4 MINIAOD
echo "------------------------------"
echo "Running step-4/5: MINIAOD"
echo "------------------------------"
cmsDriver.py step4 --runUnscheduled --conditions auto:run3_data_prompt_relval -n 5 --era Run3_2023 -s PAT --data --datatier MINIAOD --eventcontent MINIAOD --filein file:output_step3_AOD.root --fileout output_step4_MINIAOD.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 |& tee output_step4_MINIAOD.log

#5 NANOAOD
echo "------------------------------"
echo "Running step-5/5: NANOAOD"
echo "------------------------------"
cmsDriver.py step5 --runUnscheduled --conditions auto:run3_data_prompt_relval -n 5 --era Run3_2023 -s NANO --data --datatier NANOAOD --eventcontent NANOAOD --filein file:output_step4_MINIAOD.root --fileout output_step5_NANOAOD.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step5_NANOAOD.log
