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

from CondCore.Utilities.CondDBFW import querying
#import CondCore.Utilities.CondDBFW.shell as shell

sqlite_db_url = options.file
sqlite_con = querying.connect('sqlite://'+sqlite_db_url,map_blobs=True)
my_dict = sqlite_con.tag(name=options.tag).iovs().as_dicts()
sinces = []
for element in my_dict:
     # print element
     # print element['hash']
     #print element['since']
     sinces.append(element['since'])

     # would be nice to make it work using CondDBFW (sigh!)
     # payload = sqlite_con.payload(hash=element["payload_hash"])
     # sqlite_out = querying.connect('sqlite://testOut.db', map_blobs=True)
     # sqlite_tag = sqlite_con.tag().all().data()[0]
     # sqlite_iovs = sqlite_tag.iovs().data()
     # tag_name = "mytest"
     # new_tag = sqlite_con.models["tag"](sqlite_tag.as_dicts(convert_timestamps=False), convert_timestamps=False)
     # new_tag.name = tag_name
     # sqlite_out.write_and_commit(payload)

for i,since in enumerate(sinces):
     #print i,since
     print "============================================================"
     if(i<len(sinces)-1):
          command = 'conddb_import -c sqlite_file:'+sqlite_db_url.rstrip(".db")+"_"+str(sinces[i])+'.db -f sqlite_file:'+sqlite_db_url+" -i "+options.tag+" -t "+options.tag+" -b "+str(sinces[i])+" -e "+str(sinces[i+1]-1)
          print command
          child = os.popen(command)
          data = child.read()
          err = child.close()
     else:
          command = 'conddb_import -c sqlite_file:'+sqlite_db_url.rstrip(".db")+"_"+str(sinces[i])+'.db -f sqlite_file:'+sqlite_db_url+" -i "+options.tag+" -t "+options.tag+" -b "+str(sinces[i])
          print command
          child = os.popen(command)
          data = child.read()
          err = child.close()

     cmsRunCommand="cmsRun AlCaRecoTriggerBitsRcdUpdate_TEMPL_cfg.py inputDB=sqlite_file:"+sqlite_db_url.rstrip(".db")+"_"+str(sinces[i])+".db inputTag="+options.tag+" outputDB=sqlite_file:"+sqlite_db_url.rstrip(".db")+"_"+str(sinces[i])+"_updated.db outputTag="+options.tag+" firstRun="+str(sinces[i])
     print cmsRunCommand
     child2 = os.popen(cmsRunCommand)
     data2 = child2.read()
     err2 = child2.close()
     
     mergeCommand = 'conddb_import -f sqlite_file:'+sqlite_db_url.rstrip(".db")+"_"+str(sinces[i])+'_updated.db -c sqlite_file:'+options.tag+".db -i "+options.tag+" -t "+options.tag+" -b "+str(sinces[i])
     print mergeCommand
     child3 = os.popen(mergeCommand)
     data3 = child3.read()
     err3 = child3.close()
     

