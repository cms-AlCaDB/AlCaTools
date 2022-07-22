#1: L1
echo "------------------------------"
echo "Running step-1/5: L1"
echo "------------------------------"
cmsDriver.py step1  --conditions auto:run2_hlt_relval -n 5 --era Run2_2018 -s L1REPACK:Full --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein /store/data/Run2018D/ZeroBias/RAW/v1/000/320/488/00000/B6F6CC00-A893-E811-A1D5-FA163E302B83.root --fileout output_step1_L1.root --customise_commands="process.load('Configuration.StandardSequences.Digi_cff') \n process.GlobalTag.DumpStat =cms.untracked.bool(True)" --outputCommands "keep *" |& tee output_step1_L1.log

#2: HLT
echo "------------------------------"
echo "Running step-2/5: HLT"
echo "------------------------------"
cmsDriver.py step2  --conditions auto:run2_hlt_relval -n 5 --era Run2_2018 -s HLT:@relval2018 --processName HLT2 --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein file:output_step1_L1.root --fileout output_step2_HLT.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step2_HLT.log

#3 AOD (RAW2DIGI,L1Reco,RECO,EI)
echo "------------------------------"
echo "Running step-3/5: AOD"
echo "------------------------------"
cmsDriver.py step3 --conditions auto:run2_data_promptlike -n 5 --era Run2_2018 -s RAW2DIGI,L1Reco,RECO,EI --data --datatier AOD --eventcontent AOD --filein file:output_step2_HLT.root --fileout output_step3_AOD.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step3_AOD.log

#4 MINIAOD
echo "------------------------------"
echo "Running step-4/5: MINIAOD"
echo "------------------------------"
cmsDriver.py step4 --runUnscheduled --conditions auto:run2_data_promptlike -n 5 --era Run2_2018 -s PAT --data --datatier MINIAOD --eventcontent MINIAOD --filein file:output_step3_AOD.root --fileout output_step4_MINIAOD.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step4_MINIAOD.log

#5 NANOAOD
echo "------------------------------"
echo "Running step-5/5: NANOAOD"
echo "------------------------------"
cmsDriver.py step5 --runUnscheduled --conditions auto:run2_data_promptlike -n 5 --era Run2_2018 -s NANO --data --datatier NANOAOD --eventcontent NANOAOD --filein file:output_step4_MINIAOD.root --fileout output_step5_NANOAOD.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step5_NANOAOD.log
