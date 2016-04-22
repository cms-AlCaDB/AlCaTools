#!/usr/bin/env python

"""
Example script to test reading from local sqlite db.
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

defaultFile='mySqlite.db'
defaultTag='myTag'

parser = optparse.OptionParser(usage =
                               'Usage: %prog [options] <file> [<file> ...]\n'
                               )

parser.add_option('-f', '--file',
                  dest = 'file',
                  default = defaultFile,
                  help = 'file to inspect',
                  )

parser.add_option('-t', '--tag',
                  dest = 'tag',
                  default = defaultTag,
                  help = 'tag to be inspected',
                  )

(options, arguments) = parser.parse_args()

#print len(options)
#if len(options) < 2:
#    parser.print_help()
#    sys.exit("=======> Exiting: Not enough parameters")

from CondCore.Utilities.CondDBFW import querying

def unpackLumiId(since):
    kLowMask = 0XFFFFFFFF
    run  = since >> 32
    lumi = since & kLowMask
    return run, lumi

sqlite_db_url = options.file
sqlite_con = querying.connect({"host" : "sqlite", "db_alias" : sqlite_db_url})
my_dict = sqlite_con.tag(name=options.tag).iovs().as_dicts()
for element in my_dict:
    run, lumi = unpackLumiId(element['since'])
    print "packed",element['since']," ===> run:",run," ls:",lumi

