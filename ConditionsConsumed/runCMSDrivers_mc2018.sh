#1: GEN
echo "------------------------------"
echo "Running step-1/9: GEN"
echo "------------------------------"
cmsDriver.py TTbar_13TeV_TuneCUETP8M1_cfi  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s GEN --fileout output_step1_GEN.root --beamspot Realistic50ns13TeVCollision  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)'|& tee output_step1_GEN.log

#2: SIM
echo "------------------------------"
echo "Running step-2/9: SIM"
echo "------------------------------"
cmsDriver.py step2  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s SIM --datatier GEN-SIM --eventcontent FEVTDEBUG --filein file:output_step1_GEN.root --fileout output_step2_SIM.root --beamspot Realistic50ns13TeVCollision  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step2_SIM.log

#3: DIGI
echo "------------------------------"
echo "Running step-3/9: DIGI"
echo "------------------------------"
cmsDriver.py step3  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s DIGI:pdigi_valid --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step2_SIM.root --fileout output_step3_DIGI.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands 'keep *_simCastorDigis_*_*' |& tee output_step3_DIGI.log

#4: L1
echo "------------------------------"
echo "Running step-4/9: L1"
echo "------------------------------"
cmsDriver.py step4  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s L1 --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step3_DIGI.root --fileout output_step4_L1.root --customise_commands="process.load('Configuration.StandardSequences.Digi_cff') \n process.GlobalTag.DumpStat =cms.untracked.bool(True)" --outputCommands "keep *" |& tee output_step4_L1.log

#5: DIGI2RAW
echo "------------------------------"
echo "Running step-5/9: DIGI2RAW"
echo "------------------------------"
cmsDriver.py step5  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s DIGI2RAW --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step4_L1.root  --fileout output_step5_DIGI2RAW.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step5_DIGI2RAW.log

#6: HLT
echo "------------------------------"
echo "Running step-6/9: HLT"
echo "------------------------------"
cmsDriver.py step6  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s HLT:@relval2018  --datatier GEN-SIM-DIGI-RAW-HLTDEBUG --eventcontent FEVTDEBUGHLT --filein file:output_step5_DIGI2RAW.root --fileout output_step6_HLT.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step6_HLT.log

#7 AODSIM (RAW2DIGI,L1Reco,RECO,RECOSIM,EI)
echo "------------------------------"
echo "Running step-7/9: AODSIM"
echo "------------------------------"
cmsDriver.py step7 --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s RAW2DIGI,L1Reco,RECO,RECOSIM,EI --datatier AODSIM --eventcontent AODSIM --filein file:output_step6_HLT.root --fileout output_step7_AODSIM.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step7_AODSIM.log

#8 MINIAODSIM
echo "------------------------------"
echo "Running step-8/9: MINIADOSIM"
echo "------------------------------"
cmsDriver.py step8 --runUnscheduled --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s PAT --datatier MINIAODSIM --eventcontent MINIAODSIM --filein file:output_step7_AODSIM.root --fileout output_step8_MINIAODSIM.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step8_MINIAODSIM.log

#9 NANOAODSIM
echo "------------------------------"
echo "Running step-9/9: NANOAODSIM"
echo "------------------------------"
cmsDriver.py step9 --runUnscheduled --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s NANO --datatier NANOAODSIM --eventcontent NANOAODSIM --filein file:output_step8_MINIAODSIM.root --fileout output_step9_NANOAODSIM.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step9_NANOAODSIM.log

################# step-7 can be splitted in sub steps ###################
#7a RAW2DIGI
#cmsDriver.py step7a  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s RAW2DIGI --datatier GEN-SIM-RECO --eventcontent RECOSIM --filein file:output_step6_HLT.root --fileout output_step7a_RAW2DIGI.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step7a_RAW2DIGI.log

#7b L1Reco
#cmsDriver.py step7b  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s L1Reco --datatier GEN-SIM-RECO --eventcontent RECOSIM --filein file:output_step7a_RAW2DIGI.root --fileout output_step7b_L1Reco.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step7b_L1Reco.log

#7c RECO
#cmsDriver.py step7c  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run2_2018 -s RECO --datatier GEN-SIM-RECO --eventcontent RECO --filein file:output_step7b_L1Reco.root --fileout output_step7c_RECO.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step7c_RECO.log

#7d, etc
