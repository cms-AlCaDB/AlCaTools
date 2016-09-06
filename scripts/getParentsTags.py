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
    
    #### Needs cmsrel inside a CMSSW > 80X
    theRelease = getCMSSWRelease()
    print "- Getting CondDBFW from release",theRelease
    connectionString=""

    if isCMSSWBefore81X( theRelease ):
        connectionString="frontier://pro/CMS_CONDITIONS"
    else:
        connectionString="frontier://FrontierProd/CMS_CONDITIONS"
        
    from CondCore.Utilities.CondDBFW import querying
    connection = querying.connect(connectionString)

    payload = connection.payload(hash=options.hash)
    my_dict = payload.parent_tags().as_dicts()

    fldmap = (
        'name',  's',
        'synch', 's',
        'insertion', '',
        )

    # Leave these alone for unquoted, tab-delimited record format.
    head = '\t'.join(fldmap[0:len(fldmap):2]) + '\n'

    #print head
    t = PrettyTable(['hash', 'since','tag','synch','insertion time'])

    for element in my_dict:
        # print fmt.format(name=element['name'], synch=element['synchronization'], insertion=element['insertion_time'])
        TAG = connection.tag(name=element['name']).iovs().as_dicts()
        for IOV in TAG:
            if (IOV['payload_hash'] == options.hash):  
                #print IOV['payload_hash'],IOV['since'],element['name'],element['synchronization'],element['insertion_time']
                t.add_row([IOV['payload_hash'],IOV['since'],element['name'],element['synchronization'],IOV['insertion_time']])

    print t

#eof
