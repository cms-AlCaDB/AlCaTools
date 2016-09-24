#!/usr/bin/env python

# originally a .csh script by M. Musich

from subprocess import Popen
import os
import sys

# $ conddb diff 80X_dataRun2_ICHEP16_replay_dontDEPLOYEDinPrompt 80X_dataRun2_Prompt_v10 
# [2016-07-13 18:47:07,070] INFO: Connecting to pro [frontier://PromptProd/cms_conditions]
# Record                            Label  pro::80X_dataRun2_ICHEP16_replay_dontDEPLOYEDinPrompt Tag  pro::80X_dataRun2_Prompt_v10 Tag                  
# --------------------------------  -----  ---------------------------------------------------------  ------------------------------------------------  
# BeamSpotObjectsRcd                -      BeamSpotObjects_2015_LumiBased_v1_offline                  BeamSpotObjects_PCL_byLumi_v0_prompt              
# CSCAlignmentErrorExtendedRcd      -      CSCAlignmentErrorExtended_6x6_offline                      CSCAlignmentErrorExtended_6x6_express             
# CSCAlignmentRcd                   -      CSCAlignment_v10_offline                                   CSCAlignment_2009_v2_express                      
# DTAlignmentErrorExtendedRcd       -      DTAlignmentErrorExtended_6x6_offline                       DTAlignmentErrorExtended_6x6_express              
# DTAlignmentRcd                    -      DTAlignment_v12_offline                                    DTAlignment_2009_v1_express                       
# EBAlignmentRcd                    -      EBAlignment_Run1_Run2_v03_offline                          EBAlignment_measured_v01_express                  
# EEAlignmentRcd                    -      EEAlignment_Run1_Run2_v03_offline                          EEAlignment_measured_v02_express                  
# ESAlignmentRcd                    -      ESAlignment_Run1_Run2_v01_offline                          ESAlignment_measured_v01_express                  
# EcalADCToGeVConstantRcd           -      EcalADCToGeVConstant_Run1_Run2_V03_offline                 EcalADCToGeVConstant_V1_express                   
# EcalPulseShapesRcd                -      EcalPulseShapes_v02_offline                                EcalPulseShapes_hlt                               
# EcalTimeCalibConstantsRcd         -      EcalTimeCalibConstants_v08_offline                         EcalTimeCalibConstants_v01_express                
# GlobalPositionRcd                 -      GlobalAlignment_v10_offline                                GlobalAlignment_2009_v2_express                   
# HcalChannelQualityRcd             -      HcalChannelQuality_v7.00_offline                           HcalChannelQuality_v1.06_hlt                      
# HcalGainsRcd                      -      HcalGains_v6.0_offline                                     HcalGains_v2.08_express                           
# SiPixelGenErrorDBObjectRcd        -      SiPixelGenErrorDBObject_38T_v3_offline                     SiPixelGenErrorDBObject_38T_v2_express            
# SiPixelTemplateDBObjectRcd        -      SiPixelTemplateDBObject_38T_v8_offline                     SiPixelTemplateDBObject38Tv2_express              
# SiStripApvGain2Rcd                -      SiStripApvGain_FromParticles_GR10_v8_offline               SiStripApvGain_FromParticles_GR10_v1_express      
# TrackerAlignmentErrorExtendedRcd  -      TrackerAlignmentExtendedErrors_v5_offline_IOVs             TrackerAlignmentExtendedErr_2009_v2_express_IOVs  
# TrackerAlignmentRcd               -      TrackerAlignment_v16_offline                               TrackerAlignment_PCL_byRun_v0_express               

myTargets = [ "TrackProbabilityCalibration_PDF3D_express",      "EcalADCToGeVConstant_V1_express"  ]


myRefs = [ "TrackProbabilityCalibration_PDF3D_v1_offline",    "EcalADCToGeVConstant_Run1_Run2_V04_offline" ]



if len(myRefs) != len(myTargets):
    sys.stderr.write("myRefs and myTargets must have the same size --> exiting")
    sys.exit(-1)


for index in range ( len(myTargets) ):
    
    # get the payload of the open IOV form designated tag; the since of what you download is set to run 300000
    # ( replace everywhere 300000 with the future run number you want )
    theImportCommand  = "conddb_import -c sqlite_file:to_%s_from_%s.db -f frontier://FrontierProd/CMS_CONDITIONS -t %s -i %s -b 300000" %( myTargets[index], myRefs[index],myTargets[index], myRefs[index], )

    # intercept the since run=300000 and set it to 1 (will this work ok for time- and ls- based tags ? ), 
    # such that the upload service will chose the earliest run nubmer allowed by the syncronization of the tag
    theChangeSinceComman =  "echo \'update IOV set SINCE=1 where SINCE=300000;\' | sqlite3 to_%s_from_%s.db"%( myTargets[index], myRefs[index])

    os.system( theImportCommand )
    os.system( theChangeSinceComman )

    metadata_file = open( "to_%s_from_%s.txt"%(myTargets[index], myRefs[index] ) , "w")
    metadata_string = """   {
    \"destinationDatabase\": "oracle://cms_orcon_prod/CMS_CONDITIONS",
    \"destinationTags\": {
    \"%s\": {}
    },
    \"inputTag\": \"%s\",
    \"since\": null,
    \"userText\": \"Update %s with Sept2016 reprocessing from %s conditions for Run2016H\"
    } """ %( myTargets[index], myTargets[index], myTargets[index],  myRefs[index])
    metadata_file.write(metadata_string)
    metadata_file.close()
