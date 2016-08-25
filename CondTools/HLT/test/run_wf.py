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
from CondCore.Utilities.CondDBFW import querying
#import CondCore.Utilities.CondDBFW.shell as shell

##############################################
def getCommandOutput(command):
##############################################
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
     
     defaultFile='mySqlite.db'
     defaultTag='myTag'

     parser = optparse.OptionParser(usage = 'Usage: %prog [options] <file> [<file> ...]\n')
     
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

     sqlite_db_url = options.file
     sqlite_con = querying.connect('sqlite://'+sqlite_db_url,map_blobs=True)
     my_dict = sqlite_con.tag(name=options.tag).iovs().as_dicts()
     sinces = []
     for element in my_dict:
          # print element
          # print element['hash']
          # print element['since']
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
               command = 'conddb_import -c sqlite_file:'+sqlite_db_url.rstrip(".db")+"_IOV_"+str(sinces[i])+'.db -f sqlite_file:'+sqlite_db_url+" -i "+options.tag+" -t "+options.tag+" -b "+str(sinces[i])+" -e "+str(sinces[i+1]-1)
               print command
               getCommandOutput(command)
          else:
               command = 'conddb_import -c sqlite_file:'+sqlite_db_url.rstrip(".db")+"_IOV_"+str(sinces[i])+'.db -f sqlite_file:'+sqlite_db_url+" -i "+options.tag+" -t "+options.tag+" -b "+str(sinces[i])
               print command
               getCommandOutput(command)
               
          # update the trigger bits

          cmsRunCommand="cmsRun AlCaRecoTriggerBitsRcdUpdate_TEMPL_cfg.py inputDB=sqlite_file:"+sqlite_db_url.rstrip(".db")+"_IOV_"+str(sinces[i])+".db inputTag="+options.tag+" outputDB=sqlite_file:"+sqlite_db_url.rstrip(".db")+"_IOV_"+str(sinces[i])+"_updated.db outputTag="+options.tag+" firstRun="+str(sinces[i])
          print cmsRunCommand
          getCommandOutput(cmsRunCommand)
     
          # merge the output
          
          mergeCommand = 'conddb_import -f sqlite_file:'+sqlite_db_url.rstrip(".db")+"_IOV_"+str(sinces[i])+'_updated.db -c sqlite_file:'+options.tag+".db -i "+options.tag+" -t "+options.tag+" -b "+str(sinces[i])
          print mergeCommand
          getCommandOutput(mergeCommand)

          # clean the house
     
          cleanCommand = 'rm -fr *updated*.db *IOV_*.db'
          getCommandOutput(cleanCommand)

     

if __name__ == "__main__":        
     main()
