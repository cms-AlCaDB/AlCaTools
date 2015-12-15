#!/usr/bin/env python

import datetime,time
import os,sys
import copy
import string, re
import subprocess
import ConfigParser, json
from optparse import OptionParser

####################--- Classes ---############################

class BetterConfigParser(ConfigParser.ConfigParser):

    ##############################################
    def optionxform(self, optionstr):
        return optionstr

    ##############################################
    def exists( self, section, option):
         try:
             items = self.items(section) 
         except ConfigParser.NoSectionError:
             return False
         for item in items:
             if item[0] == option:
                 return True
         return False

    ##############################################
    def __updateDict( self, dictionary, section ):
        result = dictionary
        try:
            for option in self.options( section ):
                result[option] = self.get( section, option )
            if "local"+section.title() in self.sections():
                for option in self.options( "local"+section.title() ):
                    result[option] = self.get( "local"+section.title(),option )
        except ConfigParser.NoSectionError, section:
            msg = ("%s in configuration files. This section is mandatory."
                   %(str(section).replace(":", "", 1)))
            #raise AllInOneError(msg)
        return result     

    ##############################################
    def getResultingSection( self, section, defaultDict = {}, demandPars = [] ):
        result = copy.deepcopy(defaultDict)
        for option in demandPars:
            try:
                result[option] = self.get( section, option )
            except ConfigParser.NoOptionError, globalSectionError:
                globalSection = str( globalSectionError ).split( "'" )[-2]
                splittedSectionName = section.split( ":" )
                if len( splittedSectionName ) > 1:
                    localSection = ("local"+section.split( ":" )[0].title()+":"
                                    +section.split(":")[1])
                else:
                    localSection = ("local"+section.split( ":" )[0].title())
                if self.has_section( localSection ):
                    try:
                        result[option] = self.get( localSection, option )
                    except ConfigParser.NoOptionError, option:
                        msg = ("%s. This option is mandatory."
                               %(str(option).replace(":", "", 1).replace(
                                   "section",
                                   "section '"+globalSection+"' or", 1)))
                        #raise AllInOneError(msg)
                else:
                    msg = ("%s. This option is mandatory."
                           %(str(globalSectionError).replace(":", "", 1)))
                    #raise AllInOneError(msg)
        result = self.__updateDict( result, section )
        #print result
        return result

##### method to parse the input file ################################

def ConfigSectionMap(config, section):
    the_dict = {}
    options = config.options(section)
    for option in options:
        try:
            the_dict[option] = config.get(section, option)
            if the_dict[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            the_dict[option] = None
    return the_dict

##############################################
def main():
##############################################

    desc="""This is a description of %prog."""
    parser = OptionParser(description=desc,version='%prog version 0.1')
    parser.add_option('-i','--input',help='set input configuration (overrides default)',dest='inputconfig',action='store',default=None)
    (opts, args) = parser.parse_args()

    ConfigFile = opts.inputconfig
    
    if ConfigFile is not None:
        print "********************************************************"
        print "* Parsing from input file:", ConfigFile," "
        print "********************************************************"
        
        config = BetterConfigParser()
        config.read(ConfigFile)

        #print config.sections()
        #config.getResultingSection(config.sections()[0])

        dict = {'RunI_Ideal_scenario' : ('run1_design',"Run1 Ideal Simulation"),
                'RunI_Realistic_scenario' : ('run1_mc',"Run1 Realistic Simulation"),
                'RunI_Heavy_Ions_scenario' : ('run1_mc_hi',"Run1 Heavy Ion Simulation"),
                'RunI_Proton-Lead_scenario' : ('run1_mc_pa',"Run1 proton-Lead Simulation"),
                'RunII_Ideal_scenario': ('run1_mc_design',"Run2 Ideal Simulation"),
                'RunII_Asymptotic_scenario' : ('run2_mc',"Run2 Asymptotic Simulation"),
                'RunII_Startup_scenario' : ('run2_mc_50ns',"Run2 Startup Simulation"),
                'RunII_Heavy_Ions_scenario' : ('run2_mc_hi',"Run2 Heavy Ions Simulation"),
                'RunI_HLT_processing' : ('run1_hlt',"Run1 data HLT processing"),
                'RunI_Offline_processing': ('run1_data',"Run1 data offline processing"),
                'RunII_HLT_processing' : ('run2_hlt',"Run2 data HLT processing"),
                'RunII_Offline_processing': ('run2_data',"Run2 data offline processing")}
        
        ###############################
        # Get th release
        ###############################
        rel = config.getResultingSection("release")
        for key in rel:
            if("theRelease" in key):
                params = rel[key].split(',')
                
                fout1=open("GitHub"+params[0]+".txt",'w')
                fout2=open("Twiki"+params[0]+".txt",'w')
                
                fout2.write("---++++ "+params[0]+"\n")
                fout2.write("[[https://github.com/cms-sw/cmssw/blob/"+params[0]+"/Configuration/AlCa/python/autoCond.py][Configuration/AlCa/python/autoCond.py]] \n\n")

        ###############################
        # Run1 Simulation
        ###############################
        conditions1 = config.getResultingSection("RunI_Simulation")
        fout1.write("## RunI simulation \n \n")
        for key in conditions1:
            if("scenario" in key):
                params = conditions1[key].split(',')

                fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                fout1.write("      *\n \n")

                fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                fout2.write("      *\n \n")

        ###############################
        # Run2 Simulation
        ###############################
        conditions2 = config.getResultingSection("RunII_Simulation")
        fout1.write("## RunII simulation \n \n")
        for key in conditions2:
            if("scenario" in key):
                params = conditions2[key].split(',')

                fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                fout1.write("      *\n \n")

                fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                fout2.write("      *\n \n")
                
        ###############################
        # Data Run1 
        ###############################
        conditions3 = config.getResultingSection("RunI_Data")
        fout1.write( "## RunI data \n \n")
        for key in conditions3:
            if("processing" in key):
                params = conditions3[key].split(',')

                fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                fout1.write("      *\n \n")
                
                fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                fout2.write("      *\n \n")

        ###############################
        # Data Run2
        ###############################
        conditions4 = config.getResultingSection("RunII_Data")
        fout1.write("## RunI data \n \n")
        for key in conditions4:
            if("processing" in key):
                params = conditions4[key].split(',')

                fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                fout1.write("      *\n \n")

                fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/browser/#list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/browser/#diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                fout2.write("      *\n \n")
                
if __name__ == "__main__":        
    main()
