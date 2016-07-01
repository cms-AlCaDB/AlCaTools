#!/usr/bin/env python

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
from CondCore.Utilities.CondDBFW import querying
connection = querying.connect("frontier://pro/CMS_CONDITIONS")

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

t = PrettyTable(['hash', 'since','tag','synch','insertion'])


for element in my_dict:
    # print fmt.format(name=element['name'], synch=element['synchronization'], insertion=element['insertion_time'])
    TAG = connection.tag(name=element['name']).iovs().as_dicts()
    for IOV in TAG:
        if (IOV['payload_hash'] == options.hash):  
            #print IOV['payload_hash'],IOV['since'],element['name'],element['synchronization'],element['insertion_time']
            t.add_row([IOV['payload_hash'],IOV['since'],element['name'],element['synchronization'],element['insertion_time']])

print t
