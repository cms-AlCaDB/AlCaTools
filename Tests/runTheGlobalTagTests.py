#!/usr/bin/env python

import datetime,time
import os,sys
import copy
import string, re
import subprocess
import ConfigParser, json
from optparse import OptionParser

from autoCond_TEMPL import autoCondTemplate as myAutoCond

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

####################--- Helpers ---############################
#replaces .oO[id]Oo. by map[id] in target
def replaceByMap(target, map):
    result = target
    for id in map:
        #print "  "+id+": "+map[id]
        lifeSaver = 10e3
        iteration = 0
        while ".oO[" in result and "]Oo." in result:
            for id in map:
                result = result.replace(".oO["+id+"]Oo.",map[id])
                iteration += 1
            if iteration > lifeSaver:
                problematicLines = ""
                print map.keys()
                for line in result.splitlines():
                    if  ".oO[" in result and "]Oo." in line:
                        problematicLines += "%s\n"%line
                raise StandardError, "Oh Dear, there seems to be an endless loop in replaceByMap!!\n%s\nrepMap"%problematicLines
    return result

##############################################
def execme(command,dryrun=False):    
    '''Wrapper for executing commands.
    '''
    if dryrun:
        print command
    else:
        print " * Executing: %s..."%command
        os.system(command)
        print " * Executed!"

#####################################################################
def getCommandOutput(command):
    """This function executes `command` and returns it output.
    Arguments:
    - `command`: Shell command to be invoked by this function.
    """
    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        print '%s failed w/ exit code %d' % (command, err)
    return data

##############################################
def main():
##############################################

    desc="""This is a description of %prog."""
    parser = OptionParser(description=desc,version='%prog version 0.1')
    parser.add_option('-i','--input',help='set input configuration (overrides default)',dest='inputconfig',action='store',default=None)
    parser.add_option('-r','--release',help='set release to be tested',dest='inputrelease',action='store',default='8_0_X')
    (opts, args) = parser.parse_args()

    ConfigFile = opts.inputconfig
    
    repMap = {}

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
                'RunII_Ideal_scenario': ('run2_design',"Run2 Ideal Simulation"),
                'RunII_Asymptotic_scenario' : ('run2_mc',"Run2 Asymptotic Simulation"),
                'RunII_Startup_scenario' : ('run2_mc_50ns',"Run2 Startup Simulation"),
                'RunII_Heavy_Ions_scenario' : ('run2_mc_hi',"Run2 Heavy Ions Simulation"),
                'RunII_CRAFT_scenario' : ('run2_mc_cosmics',"Run2 CRAFT cosmics Simulation"),
                'RunI_HLT_processing' : ('run1_hlt',"Run1 data HLT processing"),
                'RunI_Offline_processing': ('run1_data',"Run1 data offline processing"),
                'RunII_HLT_processing' : ('run2_hlt',"Run2 data HLT processing"),
                'RunII_HLTHI_processing' : ('run2_hlt_hi', "Run2 data HLT Heavy Ion processing"),
                'RunII_Offline_processing': ('run2_data',"Run2 data offline processing"),
                'RunII_HLT_relval_processing' : ('run2_hlt_relval',"Run2 data HLT RelVal processing"),
                'RunII_Offline_relval_processing' : ('run2_data_relval',"Run2 data offline RelVal processing"),
                'PhaseI_design_scenario': ('phase1_2017_design',"Phase-I 2017 design")}
        
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
        # Get the sections
        ###############################

        sections = ["RunI_Simulation","RunII_Simulation","RunI_Data","RunII_Data","Upgrade"]
        
        for section in sections:

            print "Preparing:",section
            conditions = config.getResultingSection(section)
            if(conditions):
                fout1.write("## "+section.replace("_"," ")+"\n \n")
                for key in conditions:
                    if(("scenario" in key) or ("processing" in key)):
                        params = conditions[key].split(',')
                    
                        fout1.write("   * **"+key.replace("_"," ")+"** : ["+params[0]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+") as ["+params[1]+"](https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[1]+") with the following [changes](https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"): \n")
                        fout1.write("      *\n \n")
                    
                        fout2.write("   * =\'"+dict[key][0]+"\'= ("+dict[key][1]+") : [[https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/"+params[0]+"]["+params[0]+"]],[[https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"+params[0]+"/"+params[1]+"][diff with previous]]: \n")
                        fout2.write("      *\n \n")

                        print "=====>",str(dict[key][0]).ljust(20),":",str(params[0]).ljust(20)
                        #print '{:10s} {:10s}'.format(str(dict[key][0]),str(params[0]))
                        repMap.update({dict[key][0].upper():params[0]})

        ## replace the map of inputs
                        
        theReplacedMap = replaceByMap(myAutoCond,repMap)
        #print repMap
        #print theReplacedMap
        
        filePath = os.path.join(".","autoCond.py")
        theFile = open( filePath, "w" )
        theFile.write(theReplacedMap)
        theFile.close()

        theReleaseList = getCommandOutput("echo `scramv1 l -a | awk '$1==\"CMSSW\" && /CMSSW_"+opts.inputrelease+"/ { print $2  }' | sort`")
        #print theReleaseList
        theRelease = theReleaseList.split()[-1]
        #print theRelease

        commands = []
        commands.append("#!/bin/tcsh")
        commands.append('cd $TMPDIR')
        commands.append('cmsrel %s' % theRelease )
        commands.append('cd %s/src' % theRelease )
        commands.append('cmsenv')
        commands.append('git cms-addpkg Configuration/AlCa')
        commands.append('cp -pr autoCond.py $CMSSW_BASE/src/Configuration/AlCa/pyton')
        commands.append('scramv1 b -j 8')
        commands.append('runTheMatrix.py -l 4.22,5.1,8.0,9.0,25.0,101.0,134.911,135.4,140.53,1000.0,1001.0,1003.0,1306.0,1330.0,10021.0,10024.0,25202.0,50202.0')
        
        theExecutableFile = open("testing.csh", "w" )

        print "-------------------------------------------------------"
        print "Will run the following commands"
        print "-------------------------------------------------------"     
        for command in commands:
            print command
            theExecutableFile.write(command+"\n")
            
        theExecutableFile.close()
        os.system("chmod +x testing.csh")

if __name__ == "__main__":        
    main()
