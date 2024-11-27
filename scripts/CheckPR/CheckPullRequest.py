#!/usr/bin/env/python
#script that compares some runTheMatrix.py flows produced by the base CMSSW and the pull request

import urllib
import string
import os
import sys
import array
import LaunchOnCondor
import glob
import time
import commands
import subprocess

# 1st argument is the name of the CMSSW release
# 2nd argument is the ref. number of the pull request, e.g. 14406, read it from the browser

CWD       = os.getcwd()
compare   = [
        #dirname #pull #list of workflows for runTheMatrix.py
       ["vanilla", 0, [["1000.0", 1000], ["1001.0", 1000], ["135.4", 1000], ["140.53", 1000], ["4.22", 1000], ["8.0", 1000]]],
       ["changes", 1, [["1000.0", 1000], ["1001.0", 1000], ["135.4", 1000], ["140.53", 1000], ["4.22", 1000], ["8.0", 1000]]],
]

if os.environ.get('SCRAM_ARCH') != 'slc6_amd64_gcc530':
   os.environ['SCRAM_ARCH']='slc6_amd64_gcc530'

print('SCRAM_ARCH =', os.environ.get('SCRAM_ARCH'))

### equivallent to step 0 -- we prepare the terrain
if len(sys.argv) == 3:
   CMSSWREL = sys.argv[1]
   for toCompare in compare:
      os.system("mkdir %s" % toCompare[0])
      os.chdir("%s/%s" % (CWD, toCompare[0]))
      os.system("scramv1 project %s" % CMSSWREL)
      print("*** Preparing %s ***" % toCompare[0])
      os.chdir("%s/%s/%s/src" % (CWD, toCompare[0], CMSSWREL))
      print("Initializing git repository ...")
      os.system("eval `scramv1 runtime -sh` && git cms-init > ../creation.log 2>&1")
      
      if toCompare[1] == 1:
         print("Applying patch ...")
         os.system("eval `scramv1 runtime -sh` && git cms-merge-topic %s > ../merge.log 2>&1" % sys.argv[2])

      print("Compiling ...")
      os.system("eval `scramv1 runtime -sh` && scramv1 b -j16 > ../compile.log 2>&1")
      
      os.system("mkdir testDir")
      os.chdir(CWD)

elif len(sys.argv) == 2:
   ### submit runTheMatrix workflows to the cluster
   if sys.argv[1] == "1":
      JobName = "AlcaRecoComparison"
      FarmDirectory = "FARM"
      for toCompare in compare:
         CMSSWREL = os.listdir("%s/%s" % (CWD, toCompare[0]))[0]
         os.chdir("%s/%s/%s/src/testDir" % (CWD, toCompare[0], CMSSWREL))
         os.system("eval `scramv1 runtime -sh`")
         LaunchOnCondor.SendCluster_Create(FarmDirectory, JobName)
         for workflow in toCompare[2]:
            LaunchOnCondor.SendCluster_Push (["BASH", "runTheMatrix.py -l %s --command=\"-n %i\"; mv %s* %s/%s/%s/src/testDir/%s/outputs/results_%s" % (workflow[0], workflow[1], workflow[0], CWD, toCompare[0], CMSSWREL, FarmDirectory, workflow[0])])
            LaunchOnCondor.Jobs_FinalCmds = ["rm -f runall-report-step123-.log"]

         os.system("rm -rf %s/%s/%s/src/testDir/%s/outputs/*" % (CWD, toCompare[0], CMSSWREL, FarmDirectory))
         LaunchOnCondor.SendCluster_Submit()
         os.chdir(CWD)

   ### compare the edmEvents stuff
   elif sys.argv[1] == "2":
      for toCompare in compare:
         print('========================================\n*** Creating edm reports for %s ***\n' % toCompare[0])
         CMSSWREL = os.listdir("%s/%s" % (CWD, toCompare[0]))[0]
         os.chdir("%s/%s/%s/src/testDir/FARM/outputs" % (CWD, toCompare[0], CMSSWREL))
         for workflow in toCompare[2]:
            if os.path.isdir("results_%s" % workflow[0]):
               os.chdir("results_%s" % workflow[0])
            else:
               print("results_%s is missing! Could be due to disk quota or other problems." % workflow[0])
               continue

            ListOfFilesToCheck = os.popen("find . -name \"step?_ALCA*.py\" | xargs -I% grep root % | grep -v step | grep -v Names | awk '{print $3}' | cut -c 23- | sed \"s/.root\'),//g\"").read().split()
            if len(ListOfFilesToCheck) == 0:
               print(workflow[0], "\thas no AlCaReco root files.")
               os.chdir("../")
               continue

            print("Creating logs of", workflow[0], ":")
            for toCheck in ListOfFilesToCheck:
               print("   edmEventSize -v -a %s.root > eventSize_%s_%s.log 2>&1" % (toCheck, workflow[0], toCheck))
               os.system("eval `scramv1 runtime -sh` && edmEventSize -v -a %s.root > eventSize_%s_%s.log 2>&1" % (toCheck, workflow[0], toCheck))
               print("   edmDumpEventContent %s.root > eventContent_%s_%s.log 2>&1" % (toCheck, workflow[0], toCheck))
               os.system("eval `scramv1 runtime -sh` && edmDumpEventContent %s.root > eventContent_%s_%s.log 2>&1" % (toCheck, workflow[0], toCheck))
            print("Merging eventSize logs ...")
            print("   cat eventSize_%s* > %s/eventSize_%s_%s.summary" % (workflow[0], CWD, toCompare[0], workflow[0]))
            os.system("cat eventSize_%s* > %s/eventSize_%s_%s.summary" % (workflow[0], CWD, toCompare[0], workflow[0]))
            print("   cat eventContent_%s* > %s/eventContent_%s_%s.summary" % (workflow[0], CWD, toCompare[0], workflow[0]))
            os.system("cat eventContent_%s* > %s/eventContent_%s_%s.summary" % (workflow[0], CWD, toCompare[0], workflow[0]))
            os.chdir("../")
            print("\n")
         os.chdir(CWD)

   ### compare the plots using validate.C
   elif sys.argv[1] == "3":
      print('Not finished yet ...')
      raise SystemExit
      CMSSWREL = os.listdir("%s/%s" % (CWD, compare[0][0]))
      for workflow in compare[0][2]:
         os.chdir("%s/%s/src/testDir/FARM/outputs/" % (CWD, CMSSWREL))

   
   elif sys.argv[1] == "clean":
      for toCompare in compare:
         os.system ("rm -rf %s" % toCompare[0])
