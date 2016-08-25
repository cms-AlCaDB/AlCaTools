import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing 

process = cms.Process("readDB")
process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.load("CondCore.CondDB.CondDB_cfi")

options = VarParsing.VarParsing()
options.register( "inputDB", 
                  "frontier://FrontierProd/CMS_CONDITIONS",  #default value
                  VarParsing.VarParsing.multiplicity.singleton, 
                  VarParsing.VarParsing.varType.string,
                  "the input DB"
                  )

options.register( "inputTag", 
                  "BeamSpotObjects_Realistic50ns_13TeVCollisions_Asymptotic_v0_mc",  #default value
                  VarParsing.VarParsing.multiplicity.singleton, 
                  VarParsing.VarParsing.varType.string,
                  "the input tag"
                  )

options.parseArguments()

print "###################################################################"
print "# dumping: "+options.inputTag
print "###################################################################"

process.CondDB.connect = cms.string(options.inputDB)

process.BeamSpotDBSource = cms.ESSource("PoolDBESSource",
                                        process.CondDB,
                                        toGet = cms.VPSet(cms.PSet(record = cms.string('BeamSpotObjectsRcd'),
                                                                   tag = cms.string(options.inputTag)
                                                                   )
                                                          )
                                        )

process.source = cms.Source("EmptySource")

process.maxEvents = cms.untracked.PSet(
            input = cms.untracked.int32(1)
                    )
process.beamspot = cms.EDAnalyzer("BeamSpotFromDB")


process.p = cms.Path(process.beamspot)

