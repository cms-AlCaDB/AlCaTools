#2: SIM
echo "------------------------------"
echo "Running step-1/7: GEN-SIM"
echo "------------------------------"
cmsDriver.py TTbar_14TeV_TuneCP5_cfi  -s GEN,SIM -n 5 --conditions auto:phase1_2022_realistic --beamspot Run3RoundOptics25ns13TeVLowSigmaZ --datatier GEN-SIM --eventcontent FEVTDEBUG --fileout output_step2_SIM.root --geometry DB:Extended --era Run3 --relval 9000,100 --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)'|& tee output_step2_SIM.log

#3: DIGI
echo "------------------------------"
echo "Running step-3/7: DIGI "
echo "------------------------------"
cmsDriver.py step1  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s DIGI:pdigi_valid --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step2_SIM.root --fileout output_step3_DIGI.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands 'keep *_simCastorDigis_*_*' |& tee output_step3_DIGI.log

#4: L1
echo "------------------------------"
echo "Running step-2/7: L1"
echo "------------------------------"
cmsDriver.py step2  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s L1 --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step3_DIGI.root --fileout output_step4_L1.root --customise_commands="process.load('Configuration.StandardSequences.Digi_cff') \n process.GlobalTag.DumpStat =cms.untracked.bool(True)" --outputCommands "keep *" |& tee output_step4_L1.log



#4.1: L1+DIGI
cmsDriver.py step3  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s DIGI:pdigi_valid,L1 --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step2_SIM.root --fileout output_step3_DIGI_L1.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands 'keep *_simCastorDigis_*_*' |& tee output_step3_DIGI_l1.log


#5: DIGI2RAW
# echo "------------------------------"
# echo "Running step-4/8: DIGI2RAW"
# echo "------------------------------"
#cmsDriver.py step5  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s DIGI2RAW --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step3_DIGI.root  --fileout output_step5_DIGI2RAW.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step5_DIGI2RAW.log
cmsDriver.py step5  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s DIGI2RAW --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step4_L1.root  --fileout output_step5_DIGI2RAW.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step5_DIGI2RAW.log

#5.1: DIGI+L1+DIGI2RAW
cmsDriver.py step5  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s DIGI:pdigi_valid,L1,DIGI2RAW --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step2_SIM.root --fileout output_step3_DIGI_L1_DIGI2RAW.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands 'keep *_simCastorDigis_*_*' |& tee output_step3_DIGI_L1_DIGI2RAW.log


#6: HLT
echo "------------------------------"
echo "Running step-4/7: HLT"
echo "------------------------------"
#DIGI:pdigi_valid,L1,DIGI2RAW,HLT:@relval2022
cmsDriver.py step6  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s HLT:@relval2022  --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step3_DIGI_L1_DIGI2RAW.root --fileout output_step6_HLT.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step6_HLT.log


#6.1: DIGI_L1+DIGI2RAW+HLT
cmsDriver.py step3  --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s DIGI:pdigi_valid,L1,DIGI2RAW,HLT:@relval2022 --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT --filein file:output_step2_SIM.root --fileout output_step3_DIGI_L1_DIGI2RAW_HLT.root  --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands 'keep *_simCastorDigis_*_*' |& tee output_step3_DIGI_L1_DIGI2RAW_HLT.log


#7 AODSIM (RAW2DIGI,L1Reco,RECO,RECOSIM,EI)
echo "------------------------------"
echo "Running step-5/7: AODSIM"
echo "------------------------------"
cmsDriver.py step7 --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s RAW2DIGI,L1Reco,RECO,RECOSIM --datatier AODSIM --eventcontent AODSIM --filein file:output_step3_DIGI_L1_DIGI2RAW_HLT.root --fileout output_step7_AODSIM.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step7_AODSIM.log


#7.1 AODSIM+DIGI_L1+DIGI2RAW+HLT

#8 MINIAODSIM
echo "------------------------------"
echo "Running step-6/7: MINIADOSIM"
echo "------------------------------"
cmsDriver.py step8 --runUnscheduled --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s PAT --datatier MINIAODSIM --eventcontent MINIAODSIM --filein file:output_step7_AODSIM.root --fileout output_step8_MINIAODSIM.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' |& tee output_step8_MINIAODSIM.log



#9 NANOAODSIM
echo "------------------------------"
echo "Running step-7/7: NANOAODSIM"
echo "------------------------------"
# cmsDriver.py step5 --runUnscheduled --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s NANO --datatier NANOAODSIM --eventcontent NANOAODSIM --filein file:output_step7_AODSIM.root --fileout output_step9_NANOAODSIM.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step9_NANOAODSIM.log
cmsDriver.py step5 --runUnscheduled --conditions auto:phase1_2022_realistic -n 5 --era Run3 -s RAW2DIGI,L1Reco,RECO,RECOSIM,PAT,NANO --datatier NANOAODSIM --eventcontent NANOAODSIM --filein file:output_step8_MINIAODSIM.root --fileout output_step9_NANOAODSIM.root --customise_commands='process.GlobalTag.DumpStat=cms.untracked.bool(True)' |& tee output_step9_NANOAODSIM.log


################# step-7 can be splitted in sub steps ###################
#7a RAW2DIGI
#cmsDriver.py step7a  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run3 -s RAW2DIGI --datatier GEN-SIM-RECO --eventcontent RECOSIM --filein file:output_step6_HLT.root --fileout output_step7a_RAW2DIGI.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step7a_RAW2DIGI.log

#7b L1Reco
#cmsDriver.py step7b  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run3 -s L1Reco --datatier GEN-SIM-RECO --eventcontent RECOSIM --filein file:output_step7a_RAW2DIGI.root --fileout output_step7b_L1Reco.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step7b_L1Reco.log

#7c RECO
#cmsDriver.py step7c  --conditions 105X_upgrade2018_realistic_v6 -n 5 --era Run3 -s RECO --datatier GEN-SIM-RECO --eventcontent RECO --filein file:output_step7b_L1Reco.root --fileout output_step7c_RECO.root --customise_commands='process.GlobalTag.DumpStat =cms.untracked.bool(True)' --outputCommands "keep *" |& tee output_step7c_RECO.log

#7d, etc
