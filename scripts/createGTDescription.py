#!/usr/bin/env python

'''
Script to create GT documentation
'''

__author__ = 'Marco Musich'
__copyright__ = 'Copyright 2015, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida', 'Gregor Mittag', 'Andreas Pfeiffer']
__license__ = 'Unknown'
__maintainer__ = 'AlCa/DB Conveners'
__email__ = 'cms-PPD-conveners-AlCaDB@cern.ch'
__version__ = 1

import datetime,time
import os,sys
import copy
import string, re
import subprocess
import ConfigParser, json
import os.path
from optparse import OptionParser

import collections


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
        keylist = result.keys()
        resultSorted = collections.OrderedDict()
        #print keylist
        print sorted(keylist)
        for key in sorted(keylist):
            resultSorted[key]=result[key]
        #print resultSorted
        return resultSorted

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

##### method to get input and print it in the description ###########
def getInput(default, prompt = ''):
    '''Like raw_input() but with a default and automatic strip().
    '''
    
    text = ""
    stopword = ""
    while True:
        answer = raw_input(prompt)
        if answer.strip() == stopword:
            break
        text += "%s\n" % answer
    for line in text.splitlines():
        print "-",line
    return text.strip()
    
    #answer = raw_input(prompt)
    #if answer:
    #    return answer.strip()
    #
    #return default.strip()

##############################################
def main():
##############################################

    desc="""This is a description of %prog."""
    parser = OptionParser(description=desc,version='%prog version 0.1')
    parser.add_option('-i','--input',help='set input configuration (overrides default)',dest='inputconfig',action='store',default=None)
    (opts, args) = parser.parse_args()

    ConfigFile = opts.inputconfig
    
    if (ConfigFile is not None and os.path.exists("./"+ConfigFile)) :
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
                'RunII_Proton-Lead_scenario' : ('run2_mc_pa',"Run2 Proton Lead Simulation"),
                'RunII_CRAFT_scenario' : ('run2_mc_cosmics',"Run2 CRAFT cosmics Simulation"),
                'RunI_HLT_processing' : ('run1_hlt',"Run1 data HLT processing"),
                'RunII_Prompt_processing' : ('run2_data_promptlike',"Run 2 data prompt processing"),
                'RunI_Offline_processing': ('run1_data',"Run1 data offline processing"),
                'RunII_HLT_processing' : ('run2_hlt',"Run2 data HLT processing"),
                'RunII_HLTHI_processing' : ('run2_hlt_hi', "Run2 data HLT Heavy Ion processing"),
                'RunII_Offline_processing': ('run2_data',"Run2 data offline processing"),
                'RunII_HLT_relval_processing' : ('run2_hlt_relval',"Run2 data HLT RelVal processing"),
                'RunII_Offline_relval_processing' : ('run2_data_relval',"Run2 data offline RelVal processing"),
                'PhaseI_2017_design_scenario': ('phase1_2017_design',"Phase-I 2017 design"),
                'PhaseI_2017_realistic_scenario': ('phase1_2017_realistic',"Phase-I 2017 realistic"),
                'PhaseI_2017_cosmics_scenario': ('phase1_2017_cosmics',"Phase-I 2017 deco cosmics"),
                'PhaseI_2017_cosmics_peak_scenario': ('phase1_2017_cosmics',"Phase-I 2017 peak cosmics"),
                'PhaseI_2017_HcalDev_scenario' :('phase1_2017_hcaldev',"Phase-I 2017 hcal development"),
                'PhaseI_2018_design_scenario': ('phase1_2018_design',"Phase-I 2018 design"),
                'PhaseI_2018_realistic_scenario': ('phase1_2018_realistic',"Phase-I 2018 realistic"),
                'PhaseI_2018_cosmics_scenario': ('phase1_2018_cosmics',"Phase-I 2018 cosmics"),
                'PostLS2_realistic_scenario': ('postLS2_realistic',"postLS2 realistic"),
                'PhaseII_realistic_scenario' :('phase2_2023_realistic',"Phase-II 2023 realistic")
        }
        
        thePR=""
        theRelease=""
        ###############################
        # Get the release
        ###############################
        rel = config.getResultingSection("release")
        for key in rel:
            if("theRelease" in key):
                theRelease = rel[key].split(',')[0]
                
            if("pullrequest" in key):
                thePR = rel[key].split(',')[0]
        
        if (len(thePR)!=0 and len(theRelease)!=0):
            fout1=open("GitHub_"+theRelease+"_"+thePR+".txt",'w')
            fout2=open("Twiki_"+theRelease+"_"+thePR+".txt",'w')
        else:
            fout1=open("GitHub_"+theRelease+".txt",'w')
            fout2=open("Twiki_"+theRelease+".txt",'w')

        fout1.write("# Summary of changes in Global Tags \n \n")    
        fout2.write("---++++ "+theRelease+"\n")
        fout2.write("[[https://github.com/cms-sw/cmssw/blob/"+theRelease+"/Configuration/AlCa/python/autoCond.py][Configuration/AlCa/python/autoCond.py]] \n\n")
        
        ###############################
        # Run1 Simulation
        ###############################
        conditions1 = config.getResultingSection("RunI_Simulation")
        if(conditions1):
            fout1.write("## RunI simulation \n \n")
            for key in conditions1:
                if("scenario" in key):
                    params = conditions1[key].split(',')
                    description = getInput('None', '\nWhat differs between '+params[0]+' and '+params[1]+' ?\n[leave empty to stop and go to next item...]: ')

                    fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                    for line in description.splitlines():
                        fout1.write("      * "+line+"\n")
                    fout1.write("\n")
                    
                    fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                    for line in description.splitlines():
                        fout2.write("      * "+line+"\n")
                    fout2.write("\n")

        ###############################
        # Run2 Simulation
        ###############################
        conditions2 = config.getResultingSection("RunII_Simulation")
        if(conditions2):
            fout1.write("## RunII simulation \n \n")
            for key in conditions2:
                if("scenario" in key):
                    params = conditions2[key].split(',')
                    description = getInput('None', '\nWhat differs between '+params[0]+' and '+params[1]+' ?\n[leave empty to stop and go to next item...]: ')
                    
                    fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                    for line in description.splitlines():
                        fout1.write("      * "+line+"\n")
                    fout1.write("\n")
                    
                    fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                    for line in description.splitlines():
                        fout2.write("      * "+line+"\n")
                    fout2.write("\n")
                  
        ###############################
        # Data Run1 
        ###############################
        conditions3 = config.getResultingSection("RunI_Data")
        if(conditions3):
            fout1.write( "## RunI data \n \n")
            for key in conditions3:
                if("processing" in key):
                    params = conditions3[key].split(',')
                    description = getInput('None', '\nWhat differs between '+params[0]+' and '+params[1]+' ?\n[leave empty to stop and go to next item...]: ')
                    
                    fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                    for line in description.splitlines():
                        fout1.write("      * "+line+"\n")
                    fout1.write("\n")
                  
                    fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                    for line in description.splitlines():
                        fout2.write("      * "+line+"\n")
                    fout2.write("\n")
              
        ###############################
        # Data Run2
        ###############################
        conditions4 = config.getResultingSection("RunII_Data")
        if(conditions4):
            fout1.write("## RunII data \n \n")
            for key in conditions4:
                if("processing" in key):
                    params = conditions4[key].split(',')
                    description = getInput('None', '\nWhat differs between '+params[0]+' and '+params[1]+' ?\n[leave empty to stop and go to next item...]: ')
                    
                    fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                    for line in description.splitlines():
                        fout1.write("      * "+line+"\n")
                    fout1.write("\n")

                    fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                    for line in description.splitlines():
                        fout2.write("      * "+line+"\n")
                    fout2.write("\n")
              
        ###############################
        # Upgrade
        ###############################
        conditions5 = config.getResultingSection("Upgrade")
        if(conditions5):
            fout1.write("## Upgrade \n \n")
            for key in conditions5:
                if("scenario" in key):
                    params = conditions5[key].split(',')
                    description = getInput('None', '\nWhat differs between '+params[0]+' and '+params[1]+' ?\n[leave empty to stop and go to next item...]: ')
                    
                    fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                    for line in description.splitlines():
                        fout1.write("      * "+line+"\n")
                    fout1.write("\n")
                    
                    fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                    for line in description.splitlines():
                        fout2.write("      * "+line+"\n")
                    fout2.write("\n")
                    
                    fout2.write("[[https://github.com/cms-sw/cmssw/pull/"+thePR+"][Pull Request]]")

        ###############################
        # 2017 MC
        ###############################
        conditions6 = config.getResultingSection("2017_MC")
        if(conditions6):
            fout1.write("## 2017_MC \n \n")
            for key in conditions6:
                if("scenario" in key):
                    params = conditions6[key].split(',')
                    description = getInput('None', '\nWhat differs between '+params[0]+' and '+params[1]+' ?\n[leave empty to stop and go to next item...]: ')
                    
                    fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                    for line in description.splitlines():
                        fout1.write("      * "+line+"\n")
                    fout1.write("\n")
                    
                    fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                    for line in description.splitlines():
                        fout2.write("      * "+line+"\n")
                    fout2.write("\n")
                    
                    fout2.write("[[https://github.com/cms-sw/cmssw/pull/"+thePR+"][Pull Request]]")



        #########################
        # Print output
        #########################
        print "Output will be found at:"
        print "  - GitHub_"+theRelease+"_"+thePR+".txt"
        print "  - Twiki_"+theRelease+"_"+thePR+".txt"

    else:
        print "\n"
        print "ERROR in calling createDescription.py "
        print "  An input file has not been specified"
        print "  Please enter the command in the format: "
        print "  python createGTDescription.py -i GT_changes.ini"
        print " =====> exiting..."
        print "\n"
        exit(1)

if __name__ == "__main__":        
    main()
