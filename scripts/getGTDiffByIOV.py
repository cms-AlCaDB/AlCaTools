#!/usr/bin/env python
'''Script that checks for differences at a given run number (or at the last IOV) between two Global Tags
'''

__author__ = 'Marco Musich'
__copyright__ = 'Copyright 2016, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida','Joshua Dawes']
__license__ = 'Unknown'
__maintainer__ = 'Marco Musich'
__email__ = 'marco.musich@cern.ch'
__version__ = 1

import datetime,time
import os,sys
import string, re
import subprocess
import ConfigParser
from optparse import OptionParser,OptionGroup

#####################################################################
def getCommandOutput(command):
#####################################################################
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

#################
def main():            
### MAIN LOOP ###

    if "CMSSW_RELEASE_BASE" in os.environ:
        print "\n"
        print "=================================================="
        print "This script is powered by cmsQueryingMiniFramework"
        print "served to you by",os.getenv('CMSSW_RELEASE_BASE')
        print "==================================================\n"
    else: 
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        print "+ This tool needs cmsQueryingMiniFramework (https://gitlab.cern.ch/jdawes/cmsQueryingMiniFramework)"
        print "+ Easiest way to get it is via CMSSW (>800) is"
        print "+ cmsrel CMSSW_8_0_4"
        print "+ cd CMSSW_8_0_4/src"
        print "+ cmsenv"
        print "+ cd -"
        print "and then you can proceed"
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        sys.exit(1)

    desc="""This is a description of %prog."""
    parser = OptionParser(description=desc,version='%prog version 0.1')
    parser.add_option('-r','--run', help='test run number', dest='testRunNumber', action='store', default='251883')
    parser.add_option('-R','--ReferenceGT',help='Reference Global Tag', dest='refGT', action='store', default='GR_H_V58C')
    parser.add_option('-T','--TargetGT'   ,help='Target Global Tag'   , dest='tarGT', action='store', default='74X_dataRun2_HLTValidation_Queue')
    parser.add_option('-L','--last',help='compares the very last IOV' , dest='lastIOV',action='store_true', default=False)
    (opts, args) = parser.parse_args()

    import CondCore.Utilities.CondDBFW.shell as shell
    con = shell.connect()

    myGTref = con.global_tag(name=opts.refGT).tags(amount=1000).as_dicts()
    myGTtar = con.global_tag(name=opts.tarGT).tags(amount=1000).as_dicts()

    differentTags = {}

    for element in myGTref:
        RefRecord = element["record"]
        RefLabel  = element["label"]
        RefTag    = element["tag_name"]

        for element2 in myGTtar:
            if (RefRecord == element2["record"] and RefLabel==element2["label"]): 
                if RefTag != element2["tag_name"]:
                    differentTags[(RefRecord,RefLabel)]=(RefTag,element2["tag_name"])

    print "| *Record* | *"+opts.refGT+"* | *"+opts.tarGT+"* | Remarks |"
       
    for Rcd in sorted(differentTags):

        #print Rcd,differentTags[Rcd][2]," 1:",differentTags[Rcd][0]," 2:",differentTags[Rcd][1]

        refTagIOVs = con.tag(name=differentTags[Rcd][0]).iovs().as_dicts()
        tarTagIOVs = con.tag(name=differentTags[Rcd][1]).iovs().as_dicts()

        if(opts.lastIOV):

            #print "COMPARING the LAST IOV"

            lastSinceRef=-1
            lastSinceTar=-1

            for i in refTagIOVs:
                if (i["since"]>lastSinceRef):
                    lastSinceRef = i["since"]
                    hash_lastRefTagIOV = i["payload_hash"]
                    time_lastRefTagIOV = str(i["insertion_time"])

            for i in tarTagIOVs:
                if (i["since"]>lastSinceTar):
                    lastSinceTar = i["since"]
                    hash_lastTarTagIOV = i["payload_hash"]
                    time_lastTarTagIOV = str(i["insertion_time"])

            if(hash_lastRefTagIOV!=hash_lastTarTagIOV):
                print "| ="+Rcd[0]+"= ("+Rcd[1]+") | =="+differentTags[Rcd][0]+"==  | =="+differentTags[Rcd][1]+"== | | "
                print "|^|"+hash_lastRefTagIOV+" <br> ("+time_lastRefTagIOV+") "+ str(lastSinceRef) +" | "+hash_lastTarTagIOV+" <br> ("+time_lastTarTagIOV+") " + str(lastSinceTar)+" | ^|"

        else:    

            theGoodRefIOV=-1
            theGoodTarIOV=-1
            theRefPayload=""
            theTarPayload=""
            theRefTime=""
            theTarTime=""

            for IOV in refTagIOVs:
                sinceRefTagIOV = IOV["since"]
                if (sinceRefTagIOV < int(opts.testRunNumber)):
                    theGoodRefIOV=sinceRefTagIOV
                    theRefPayload=IOV["payload_hash"]
                    theRefTime=str(IOV["insertion_time"])
          
            for IOV in tarTagIOVs:
                sinceTarTagIOV = IOV["since"]
                if (sinceTarTagIOV < int(opts.testRunNumber)):
                    theGoodTarIOV=sinceTarTagIOV
                    theTarPayload=IOV["payload_hash"]
                    theTarTime=str(IOV["insertion_time"])
        
                    if(theRefPayload!=theTarPayload):
                        print "| ="+Rcd[0]+"= ("+Rcd[1]+") | =="+differentTags[Rcd][0]+"==  | =="+differentTags[Rcd][1]+"== |"
                        print "|^|"+theRefPayload+" ("+theRefTime+") | "+theTarPayload+" ("+theTarTime+") |"
                       

if __name__ == "__main__":        
    main()


