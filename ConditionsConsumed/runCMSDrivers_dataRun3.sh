#1: L1
echo "------------------------------"
echo "Running step-1/5: L1"
echo "------------------------------"
cmsDriver.py step1  --conditions auto:run3_hlt_relval -n 5 --era Run3 -s L1REPACK:Full --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein /eos/cms/store/data/Run2022D/ZeroBias/RAW/v1/000/357/538/00000/1d71e6ef-2992-459d-a127-4fcfeaef76ec.root --fileout output_step1_L1.root --customise_commands="process.load('Configuration.StandardSequences.Digi_cff') \n process.GlobalTag.DumpStat =cms.untracked.bool(True)" --outputCommands "keep *" |& tee output_step1_L1.log

#2: HLT
echo "------------------------------"
echo "Running step-2/5: HLT"
echo "------------------------------"
cmsDriver.py step2  --conditions auto:run3_hlt_relval -n 5 --era Run3 -s HLT --processName HLT2 --data --scenario pp --datatier FEVTDEBUGHLT --eventcontent FEVTDEBUGHLT --filein file:output_step1_L1.root --fileout output_step2_HLT.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step2_HLT.log

#3 AOD (RAW2DIGI,L1Reco,RECO,EI)
echo "------------------------------"
echo "Running step-3/5: AOD"
echo "------------------------------"
cmsDriver.py step3 --conditions auto:run3_hlt_relval -n 5 --era Run3 -s RAW2DIGI,L1Reco,RECO,EI --data --datatier AOD --eventcontent AOD --filein file:output_step2_HLT.root --fileout output_step3_AOD.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step3_AOD.log

#4 MINIAOD
echo "------------------------------"
echo "Running step-4/5: MINIAOD"
echo "------------------------------"
cmsDriver.py step4 --runUnscheduled --conditions auto:run3_hlt_relval -n 5 --era Run3 -s PAT --data --datatier MINIAOD --eventcontent MINIAOD --filein file:output_step3_AOD.root --fileout output_step4_MINIAOD.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step4_MINIAOD.log

#5 NANOAOD
echo "------------------------------"
echo "Running step-5/5: NANOAOD"
echo "------------------------------"
cmsDriver.py step5 --runUnscheduled --conditions auto:run3_hlt_relval -n 5 --era Run3 -s NANO --data --datatier NANOAOD --eventcontent NANOAOD --filein file:output_step4_MINIAOD.root --fileout output_step5_NANOAOD.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step5_NANOAOD.log
