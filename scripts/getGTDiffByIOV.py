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
from prettytable import PrettyTable

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
        print "+ cmsrel CMSSW_8_0_X  #get your favorite"
        print "+ cd CMSSW_8_0_X/src"
        print "+ cmsenv"
        print "+ cd -"
        print "and then you can proceed"
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        sys.exit(1)

    desc="""This is a description of %prog."""
    parser = OptionParser(description=desc,version='%prog version 0.1')
    parser.add_option('-r','--run'        ,help='test run number', dest='testRunNumber', action='store', default='251883')
    parser.add_option('-R','--ReferenceGT',help='Reference Global Tag', dest='refGT', action='store', default='GR_H_V58C')
    parser.add_option('-T','--TargetGT'   ,help='Target Global Tag'   , dest='tarGT', action='store', default='74X_dataRun2_HLTValidation_Queue')
    parser.add_option('-L','--last'       ,help='compares the very last IOV' , dest='lastIOV',action='store_true', default=False)
    parser.add_option('-v','--verbose'    ,help='returns more info', dest='isVerbose',action='store_true',default=False)
    (opts, args) = parser.parse_args()

    import CondCore.Utilities.CondDBFW.shell as shell
    con = shell.connect()

    myGTrefInfo = con.global_tag(name=opts.refGT)
    myGTtarInfo = con.global_tag(name=opts.tarGT)

    text_file = open(("diff_%s_vs_%s.twiki") % (opts.refGT,opts.tarGT), "w")

    refSnap = myGTrefInfo.snapshot_time
    tarSnap = myGTtarInfo.snapshot_time

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

    text_file.write("| *Record* | *"+opts.refGT+"* | *"+opts.tarGT+"* | Remarks | \n")

    t = PrettyTable()

    if(opts.isVerbose):
        t.field_names = ['/','',opts.refGT,opts.tarGT,refSnap,tarSnap]
    else:
        t.field_names = ['/','',opts.refGT,opts.tarGT]

    t.hrules=1
    
    if(opts.isVerbose):
        t.add_row(['Record','label','Reference Tag','Target Tag','hash1:time1:since1','hash2:time2:since2'])
    else:
        t.add_row(['Record','label','Reference Tag','Target Tag'])

    isDifferent=False
 
    for Rcd in sorted(differentTags):

        #print Rcd,differentTags[Rcd][2]," 1:",differentTags[Rcd][0]," 2:",differentTags[Rcd][1]

        refTagIOVs = con.tag(name=differentTags[Rcd][0]).iovs().as_dicts()
        tarTagIOVs = con.tag(name=differentTags[Rcd][1]).iovs().as_dicts()

        if(opts.lastIOV):

            if(sorted(differentTags).index(Rcd)==0):
                print "=== COMPARING ONLY THE LAST IOV ==="

            lastSinceRef=-1
            lastSinceTar=-1

            for i in refTagIOVs:
                if (i["since"]>lastSinceRef):
                    lastSinceRef = i["since"]
                    hash_lastRefTagIOV = i["payload_hash"]
                    time_lastRefTagIOV = str(i["insertion_time"])

            for j in tarTagIOVs:
                if (j["since"]>lastSinceTar):
                    lastSinceTar = j["since"]
                    hash_lastTarTagIOV = j["payload_hash"]
                    time_lastTarTagIOV = str(j["insertion_time"])

            if(hash_lastRefTagIOV!=hash_lastTarTagIOV):
                isDifferent=True
                text_file.write("| ="+Rcd[0]+"= ("+Rcd[1]+") | =="+differentTags[Rcd][0]+"==  | =="+differentTags[Rcd][1]+"== | | \n")
                text_file.write("|^|"+hash_lastRefTagIOV+" <br> ("+time_lastRefTagIOV+") "+ str(lastSinceRef) +" | "+hash_lastTarTagIOV+" <br> ("+time_lastTarTagIOV+") " + str(lastSinceTar)+" | ^| \n")
                
                if(opts.isVerbose):
                    t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0],differentTags[Rcd][1],str(hash_lastRefTagIOV)+"\n"+str(time_lastRefTagIOV)+"\n"+str(lastSinceRef),str(hash_lastTarTagIOV)+"\n"+str(time_lastTarTagIOV)+"\n"+str(lastSinceTar)])
                else:
                    t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0]+"\n"+str(hash_lastRefTagIOV),differentTags[Rcd][1]+"\n"+str(hash_lastTarTagIOV)])

        else:    

            theGoodRefIOV=-1
            theGoodTarIOV=-1
            sinceRefTagIOV=0
            sinceTarTagIOV=0
         
            RefIOVtime = datetime.datetime(1970, 1, 1, 0, 0, 0)
            TarIOVtime = datetime.datetime(1970, 1, 1, 0, 0, 0)

            #print RefIOVtime
            #print refSnap

            theRefPayload=""
            theTarPayload=""
            theRefTime=""
            theTarTime=""

            #print "refIOV[]","RefIOVtime","refSnap","refIOV[]>RefIOVtime","refIOV[]<refSnap"
            for refIOV in refTagIOVs:            

                #print "|",refIOV["insertion_time"],"|",RefIOVtime,"|",refSnap,(refIOV["insertion_time"]>RefIOVtime),(refIOV["insertion_time"]<refSnap), (refIOV["since"] < int(opts.testRunNumber)),(refIOV["since"]>=sinceRefTagIOV)
                    
                if ( (refIOV["since"] <= int(opts.testRunNumber)) and (refIOV["since"]>=sinceRefTagIOV) and (refIOV["insertion_time"]>RefIOVtime) and (refIOV["insertion_time"]<refSnap) ):
                    sinceRefTagIOV = refIOV["since"]   
                    RefIOVtime = refIOV["insertion_time"]
                    theGoodRefIOV=sinceRefTagIOV                
                    theRefPayload=refIOV["payload_hash"]
                    theRefTime=str(refIOV["insertion_time"])
          
            for tarIOV in tarTagIOVs:
                if ( (tarIOV["since"] <= int(opts.testRunNumber)) and (tarIOV["since"]>=sinceTarTagIOV) and (tarIOV["insertion_time"]>TarIOVtime) and (tarIOV["insertion_time"]<tarSnap)):
                    sinceTarTagIOV = tarIOV["since"]
                    tarIOVtime = tarIOV["insertion_time"]
                    theGoodTarIOV=sinceTarTagIOV
                    theTarPayload=tarIOV["payload_hash"]
                    theTarTime=str(tarIOV["insertion_time"])
        
            if(theRefPayload!=theTarPayload):
                isDifferent=True
                text_file.write("| ="+Rcd[0]+"= ("+Rcd[1]+") | =="+differentTags[Rcd][0]+"==  | =="+differentTags[Rcd][1]+"== |\n")
                text_file.write("|^|"+theRefPayload+" ("+theRefTime+") | "+theTarPayload+" ("+theTarTime+") |\n")                       

                if(opts.isVerbose):
                    t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0],differentTags[Rcd][1],str(theRefPayload)+"\n"+str(theRefTime)+"\n"+str(theGoodRefIOV),str(theTarPayload)+"\n"+str(theTarTime)+"\n"+str(theGoodTarIOV)])
                else:
                    t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0]+"\n"+str(theRefPayload),differentTags[Rcd][1]+"\n"+str(theTarPayload)])
            
    if(not isDifferent):
        if(opts.isVerbose):
            t.add_row(["None","None","None","None","None","None"])
        else:
            t.add_row(["None","None","None"])
    print t

if __name__ == "__main__":        
    main()


