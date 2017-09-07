#!/usr/bin/env python
#
# Author:   Marco MUSICH
#
# Usage:
# python getParentTags.py -H <user defined payload hash>
#

"""
Example script to extract tags given an hash
"""

import os
import sys
import optparse
import hashlib
import tarfile
import netrc
import getpass
import errno
import sqlite3
import json
import tempfile
from prettytable import PrettyTable
import sqlalchemy
import pprint
import subprocess
import CondCore.Utilities.conddblib as conddb


#####################################################################
# we need this check to handle different versions of the CondDBFW 
#####################################################################
def isCMSSWBefore81X( theRelease ):
    if theRelease == None :
        raise ValueError('theRelease is set to %s and yet, it seems to be required. ERRROR.' % (theRelease))
    if int(theRelease.split("_")[1]) < 8 :
        return True
    elif int(theRelease.split("_")[1]) == 8 :
        return int( theRelease.split("_")[2] ) < 1 
    else :
        return False
    
#####################################################################
def getCMSSWRelease( ):
    CMSSW_VERSION='CMSSW_VERSION'
    if not os.environ.has_key(CMSSW_VERSION):
        print "\n CMSSW not properly set. Exiting"
        sys.exit(1)
    release = os.getenv(CMSSW_VERSION)
    return release

#####################################################################
def get_parent_tags(db, theHash):
#####################################################################

    db = db.replace("sqlite_file:", "").replace("sqlite:", "")
    db = db.replace("frontier://FrontierProd/CMS_CONDITIONS", "pro")
    db = db.replace("frontier://FrontierPrep/CMS_CONDITIONS", "dev")

    con = conddb.connect(url = conddb.make_url(db))
    session = con.session()
    IOV = session.get_dbtype(conddb.IOV)
    Tag = session.get_dbtype(conddb.Tag)

    query_result = session.query(IOV.tag_name).filter(IOV.payload_hash == theHash).all()
    tag_names = map(lambda entry : entry[0], query_result)
    
    listOfOccur=[]

    for tag in tag_names:
        synchro = session.query(Tag.synchronization).filter(Tag.name == tag).all()
        iovs = session.query(IOV.since).filter(IOV.tag_name == tag).filter(IOV.payload_hash == theHash).all()
        times = session.query(IOV.insertion_time).filter(IOV.tag_name == tag).filter(IOV.payload_hash == theHash).all()

        synchronization = [item[0] for item in synchro]
        listOfIOVs  = [item[0] for item in iovs]
        listOfTimes = [str(item[0]) for item in times]
        
        for iEntry in range(0,len(listOfIOVs)):                                
            listOfOccur.append({"tag": tag,
                                "synchronization" : synchronization[0],
                                "since" : listOfIOVs[iEntry] ,
                                "insertion_time" : listOfTimes[iEntry] })
                           

        #mapOfOccur[tag] = (synchronization,listOfIOVs,listOfTimes)
        #mapOfOccur[tag]['synchronization'] = synchronization
        #mapOfOccur[tag]['sinces'] = listOfIOVs
        #mapOfOccur[tag]['times']  = listOfTimes

        #print tag,synchronization,listOfIOVs,listOfTimes

    return listOfOccur


#####################################################################
if __name__ == '__main__':
    parser = optparse.OptionParser(usage =
                                   'Usage: %prog [options] <file> [<file> ...]\n'
                                   )

    parser.add_option('-H', '--hash',
                      dest = 'hash',
                      default = "b0e2bc7e4947817d99324ff20f8c3238d06c46fb",
                      help = 'payload hash to check',
                      )
    
    (options, arguments) = parser.parse_args()
    
    theRelease = getCMSSWRelease()
    print "- Getting conddblib from release",theRelease
    connectionString="frontier://FrontierProd/CMS_CONDITIONS"

    tags = get_parent_tags(connectionString,options.hash)

    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(tags)

    #print tags
    #for tag in tags:
    #    print tag

    #print head
    t = PrettyTable(['hash', 'since','tag','synch','insertion time'])
    for element in tags:
        t.add_row([options.hash,element['since'],element['tag'],element['synchronization'],element['insertion_time']])

    print t

#eof
