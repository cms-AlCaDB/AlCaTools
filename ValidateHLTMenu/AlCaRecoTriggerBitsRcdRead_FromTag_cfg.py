import FWCore.ParameterSet.Config as cms

# variables overwritten with ValidateHLTMenu
run_number = None
alca_reco_hlt_paths_tag = None

# instanciate Process
process = cms.Process("READ")

# load logger
process.load("FWCore.MessageLogger.MessageLogger_cfi")

# the module writing to DB
process.load("CondTools.HLT.AlCaRecoTriggerBitsRcdRead_cfi")

# 'twiki' is default - others are text, python (future: html?)
#process.AlCaRecoTriggerBitsRcdRead.outputType = 'twiki'
# If rawFileName stays empty (default), use the message logger for output.
# Otherwise use the file name specified, adding a suffix according to outputType:
process.AlCaRecoTriggerBitsRcdRead.rawFileName = 'triggerBits_' + alca_reco_hlt_paths_tag

# No data, but might want to specify the 'firstRun' to check (default is 1):
process.source = cms.Source(
    "EmptySource",
    numberEventsInRun=cms.untracked.uint32(1), # do not change!
    firstRun=cms.untracked.uint32(run_number)
)

# With 'numberEventsInRun = 1' above,
# this will check IOVs until run (!) number specified as 'input' here,
# so take care to choose a one that is not too small...:
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(1))

# Input for AlCaRecoTriggerBitsRcd,
# either via GloblalTag (use of _cfi instead of _cff sufficient and faster):
from Configuration.AlCa.autoCond import autoCond

# Setting global tag manually
# process.load("Configuration.StandardSequences.CondDBESSource_cff")
# process.GlobalTag.globaltag = '80X_dataRun2_v13' #autoCond['run2_data'] #choose your tag

# Specifying database and tag
process.load("Configuration.StandardSequences.CondDBESSource_cff")
process.load("CondCore.CondDB.CondDB_cfi")

process.CondDB.connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
process.poolDBESSource = cms.ESSource(
    "PoolDBESSource",
    process.CondDB,
    timetype = cms.untracked.string('Run'),
    toGet = cms.VPSet(
        cms.PSet(
            record = cms.string('AlCaRecoTriggerBitsRcd'),
            tag = cms.string(alca_reco_hlt_paths_tag)
        )
    )
)

# Put module in path:
process.p = cms.Path(process.AlCaRecoTriggerBitsRcdRead)
