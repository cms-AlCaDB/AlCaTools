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
import CondCore.Utilities.conddblib as conddb

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
     db = options.file
     db = db.replace("sqlite_file:", "").replace("sqlite:", "")
     db = db.replace("frontier://FrontierProd/CMS_CONDITIONS", "pro")
     db = db.replace("frontier://FrontierPrep/CMS_CONDITIONS", "dev")

     con = conddb.connect(url = conddb.make_url(db))
     session = con.session()
     IOV = session.get_dbtype(conddb.IOV)
     iovs = set(session.query(IOV.since).filter(IOV.tag_name == options.tag).all())
     if len(iovs) == 0:
         print("No IOVs found for tag '"+options.tag+"' in database '"+db+"'.")
         sys.exit(1)

     session.close()

     sinces = sorted([int(item[0]) for item in iovs])
     print sinces

     for i,since in enumerate(sinces):
          print i,since

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
