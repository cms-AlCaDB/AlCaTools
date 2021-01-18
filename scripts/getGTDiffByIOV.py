#!/usr/bin/env python
'''Script that checks for differences at a given run number (or at the last IOV) between two Global Tags
'''

__author__ = 'Marco Musich'
__copyright__ = 'Copyright 2016, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida']
__license__ = 'Unknown'
__maintainer__ = 'Marco Musich'
__email__ = 'marco.musich@cern.ch'
__version__ = 1

import datetime,time
import os,sys
import string, re
import subprocess
import ConfigParser
import calendar
from optparse import OptionParser,OptionGroup
from prettytable import PrettyTable
import CondCore.Utilities.conddblib as conddb

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
        print "This script is powered by conddblib"
        print "served to you by",os.getenv('CMSSW_RELEASE_BASE')
        print "==================================================\n"
    else: 
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        print "+ This tool needs CMSSW libraries"
        print "+ Easiest way to get it is via CMSSW is"
        print "+ cmsrel CMSSW_X_Y_Z  #get your favorite"
        print "+ cd CMSSW_X_Y_Z/src"
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
    parser.add_option('-m','--match'      ,help='print only matching',dest='stringToMatch',action='store',default='')
    (opts, args) = parser.parse_args()

    ####################################
    # Set up connections with the DB
    ####################################

    con = conddb.connect(url = conddb.make_url("pro"))
    session = con.session()
    IOV     = session.get_dbtype(conddb.IOV)
    TAG     = session.get_dbtype(conddb.Tag)
    GT      = session.get_dbtype(conddb.GlobalTag)
    GTMAP   = session.get_dbtype(conddb.GlobalTagMap)
    RUNINFO = session.get_dbtype(conddb.RunInfo)

    ####################################
    # Get the time info for the test run
    ####################################

    bestRun = session.query(RUNINFO.run_number, RUNINFO.start_time, RUNINFO.end_time).filter(RUNINFO.run_number == int(opts.testRunNumber)).first()
    if bestRun is None:
        raise Exception("Run %s can't be matched with an existing run in the database." % opts.testRunNumber)

    print "Run",opts.testRunNumber," |Start time",bestRun[1]," |End time",bestRun[2],"."

    ####################################
    # Get the Global Tag snapshots
    ####################################

    refSnap = session.query(GT.snapshot_time).\
        filter(GT.name == opts.refGT).all()[0][0]

    tarSnap = session.query(GT.snapshot_time).\
        filter(GT.name == opts.tarGT).all()[0][0]

    print "reference GT (",opts.refGT ,") snapshot: ",refSnap," | target GT (",opts.tarGT,") snapshot",tarSnap

    ####################################
    # Get the Global Tag maps
    ####################################
    
    GTMap_ref = session.query(GTMAP.record, GTMAP.label, GTMAP.tag_name).\
        filter(GTMAP.global_tag_name == opts.refGT).\
        order_by(GTMAP.record, GTMAP.label).\
        all()

    GTMap_tar = session.query(GTMAP.record, GTMAP.label, GTMAP.tag_name).\
        filter(GTMAP.global_tag_name == opts.tarGT).\
        order_by(GTMAP.record, GTMAP.label).\
        all()

    text_file = open(("diff_%s_vs_%s.twiki") % (opts.refGT,opts.tarGT), "w")

    differentTags = {}

    for element in GTMap_ref:
        RefRecord = element[0]
        RefLabel  = element[1]
        RefTag    = element[2]

        for element2 in GTMap_tar:
            if (RefRecord == element2[0] and RefLabel==element2[1]): 
                if RefTag != element2[2]:
                    differentTags[(RefRecord,RefLabel)]=(RefTag,element2[2])

    ####################################
    ## Search for Records,Label not-found in the other list
    ####################################

    temp1 = [item for item in GTMap_ref if (item[0],item[1]) not in zip(zip(*GTMap_tar)[0],zip(*GTMap_tar)[1])]
    for elem in temp1:
        differentTags[(elem[0],elem[1])]=(elem[2],"")

    temp2 = [item for item in GTMap_tar if (item[0],item[1]) not in zip(zip(*GTMap_ref)[0],zip(*GTMap_ref)[1])]
    for elem in temp2:
        differentTags[(elem[0],elem[1])]=("",elem[2])    

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
 
    ####################################
    # Loop on the difference
    ####################################

    for Rcd in sorted(differentTags):
         
        # empty lists at the beginning
        refTagIOVs=[]
        tarTagIOVs=[]

        if( differentTags[Rcd][0]!=""):
            refTagIOVs = session.query(IOV.since,IOV.payload_hash,IOV.insertion_time).filter(IOV.tag_name == differentTags[Rcd][0]).all()
            refTagInfo = session.query(TAG.synchronization,TAG.time_type).filter(TAG.name == differentTags[Rcd][0]).all()[0]
        if( differentTags[Rcd][1]!=""):
            tarTagIOVs = session.query(IOV.since,IOV.payload_hash,IOV.insertion_time).filter(IOV.tag_name == differentTags[Rcd][1]).all()
            tarTagInfo = session.query(TAG.synchronization,TAG.time_type).filter(TAG.name == differentTags[Rcd][1]).all()[0]

        if(differentTags[Rcd][0]!="" and differentTags[Rcd][1]!=""): 
            if(tarTagInfo[1] != refTagInfo[1]):
                print bcolors.WARNING+" *** Warning *** found mismatched time type for",Rcd,"entry. \n"+differentTags[Rcd][0],"has time type",refTagInfo[1],"while",differentTags[Rcd][1],"has time type",tarTagInfo[1]+". These need to be checked by hand. \n\n"+ bcolors.ENDC

        if(opts.lastIOV):

            if(sorted(differentTags).index(Rcd)==0):
                print "=== COMPARING ONLY THE LAST IOV ==="

            lastSinceRef=-1
            lastSinceTar=-1

            for i in refTagIOVs:            
                if (i[0]>lastSinceRef):
                    lastSinceRef = i[0]
                    hash_lastRefTagIOV = i[1]
                    time_lastRefTagIOV = str(i[2])

            for j in tarTagIOVs:
                if (j[0]>lastSinceTar):
                    lastSinceTar = j[0]
                    hash_lastTarTagIOV = j[1]
                    time_lastTarTagIOV = str(j[2])

            if(hash_lastRefTagIOV!=hash_lastTarTagIOV):
                isDifferent=True
                text_file.write("| ="+Rcd[0]+"= ("+Rcd[1]+") | =="+differentTags[Rcd][0]+"==  | =="+differentTags[Rcd][1]+"== | | \n")
                text_file.write("|^|"+hash_lastRefTagIOV+" <br> ("+time_lastRefTagIOV+") "+ str(lastSinceRef) +" | "+hash_lastTarTagIOV+" <br> ("+time_lastTarTagIOV+") " + str(lastSinceTar)+" | ^| \n")
                
                if(opts.isVerbose):
                    t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0],differentTags[Rcd][1],str(hash_lastRefTagIOV)+"\n"+str(time_lastRefTagIOV)+"\n"+str(lastSinceRef),str(hash_lastTarTagIOV)+"\n"+str(time_lastTarTagIOV)+"\n"+str(lastSinceTar)])
                else:
                    t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0]+"\n"+str(hash_lastRefTagIOV),differentTags[Rcd][1]+"\n"+str(hash_lastTarTagIOV)])

        else:    

            ### reset all defaults
            
            theGoodRefIOV=-1
            theGoodTarIOV=-1
            sinceRefTagIOV=0
            sinceTarTagIOV=0
         
            RefIOVtime = datetime.datetime(1970, 1, 1, 0, 0, 0)
            TarIOVtime = datetime.datetime(1970, 1, 1, 0, 0, 0)

            theRefPayload=""
            theTarPayload=""
            theRefTime=""
            theTarTime=""

            ### loop on the reference IOV list
            for refIOV in refTagIOVs:

                ## logic for retrieving the the last payload active on a given IOV
                ## - the new IOV since is less than the run under consideration
                ## - the payload insertion time is lower than the GT snapshot
                ## - finall either:
                ##   - the new IOV since is larger then the last saved
                ##   - the new IOV since is equal to the last saved but it has a more recent insertion time
                
                if ( (refIOV[0] <= int(opts.testRunNumber)) and (refIOV[0]>sinceRefTagIOV) or ((refIOV[0]==sinceRefTagIOV) and (refIOV[2]>RefIOVtime)) and (refIOV[2]<=refSnap) ):
                    sinceRefTagIOV = refIOV[0]   
                    RefIOVtime = refIOV[2]
                    theGoodRefIOV=sinceRefTagIOV                
                    theRefPayload=refIOV[1]
                    theRefTime=str(refIOV[2])
                    print Rcd[0],"updated!",sinceRefTagIOV

          
            ### loop on the target IOV list
            for tarIOV in tarTagIOVs:
                if ( (tarIOV[0] <= int(opts.testRunNumber)) and (tarIOV[0]>sinceTarTagIOV) or ((tarIOV[0]==sinceTarTagIOV) and (tarIOV[2]>=TarIOVtime)) and (tarIOV[2]<=tarSnap) ):
                    sinceTarTagIOV = tarIOV[0]
                    tarIOVtime = tarIOV[2]
                    theGoodTarIOV=sinceTarTagIOV
                    theTarPayload=tarIOV[1]
                    theTarTime=str(tarIOV[2])

            #print Rcd[0],theRefPayload,theTarPayload
        
            if(theRefPayload!=theTarPayload):
                isDifferent=True
                text_file.write("| ="+Rcd[0]+"= ("+Rcd[1]+") | =="+differentTags[Rcd][0]+"==  | =="+differentTags[Rcd][1]+"== |\n")
                text_file.write("|^|"+theRefPayload+" ("+theRefTime+") | "+theTarPayload+" ("+theTarTime+") |\n")                       

                ### determinte if it is to be shown

                isMatched=False
                tokens=opts.stringToMatch.split(",")
                decisions = [bool(Rcd[0].find(x)!=-1) for x in tokens]
                for decision in decisions:
                    isMatched = (isMatched or decision)
                    
                if(opts.isVerbose):
                    if (opts.stringToMatch=="" or isMatched): 
                        t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0],differentTags[Rcd][1],str(theRefPayload)+"\n"+str(theRefTime)+"\n"+str(theGoodRefIOV),str(theTarPayload)+"\n"+str(theTarTime)+"\n"+str(theGoodTarIOV)])
                else:
                    if (opts.stringToMatch=="" or isMatched): 
                        t.add_row([Rcd[0],Rcd[1],differentTags[Rcd][0]+"\n"+str(theRefPayload),differentTags[Rcd][1]+"\n"+str(theTarPayload)])
            
    if(not isDifferent):
        if(opts.isVerbose):
            t.add_row(["None","None","None","None","None","None"])
        else:
            t.add_row(["None","None","None"])
    print t

if __name__ == "__main__":        
    main()
