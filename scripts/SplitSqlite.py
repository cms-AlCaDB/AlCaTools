#!/usr/bin/env python
#G.Benelli and Arun Mittal                                                                                                                                                                                  
#Oct 3 2015                                                                                                                                                                                                 
#Quick script to split a large sqlite file (holding all of our Noise payloads (Run1+Run2) into a set of smaller ones.                                                                                       
#Trying to keep the size below 100MB to avoid dropbox issues, we decided after a few test to go for 5 IOVs, the reason being that                                                                           
#a single recent noise payload seem to weight 20MB, and at most one will have 5 payloads for 5 IOVs.                                                                                                        

import subprocess
#Input IOVs:                                                                                                                                                                                                
#Reference for the use of subprocess Popen to execute a command:                                                                                                                                            
#subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.read()                                                                                                         
#Let's prepare a container for the list of IOVs:                                                                                                                                                            
IOVs=[]
#for line in subprocess.Popen("conddb --db dump_one_shot_v1.5_447_256581_258507.db list EcalLaserAPDPNRatios_201510078_256581_258507  --limit 1000",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines():
for line in subprocess.Popen("conddb --noLimit --db dump_one_shot_v1.5_447_232134_256483.db list EcalLaserAPDPNRatios_20151007_232134_256483",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines():
    if "EcalLaserAPDPNRatios" in line:
        IOVs.append((line.split()[2].strip(')')).strip('('))
print IOVs
print "There are %s IOVs!"%len(IOVs)
#Prepare the conddb_import commands template:                                                                                                                                                               
#CommandTemplate="conddb_import -f sqlite:SiStripNoise_GR10_v3_offline.db -c sqlite:SiStripNoise_GR10_v3_offline_%s_%s.db -i SiStripNoise_GR10_v4_offline -t SiStripNoise_GR10_v4_offline -b %s -e %s"      

#Let's assemble the commands now!                                                                                                                                                                           
#Let's pick IOVs every 5:                                                                                                                                                                                   
#RelevantIOVs=[(IOV,IOVs[IOVs.index(IOV)+4],IOVs[IOVs.index(IOV)+5]) for IOV in IOVs if IOVs.index(IOV)==0 or ((IOVs.index(IOV)+1)%5==0 and (IOVs.index(IOV)+5)<len(IOVs))]
RelevantIOVs=[(IOV,IOVs[IOVs.index(IOV)+199],IOVs[IOVs.index(IOV)+200]) for IOV in IOVs if IOVs.index(IOV)==0 or ((IOVs.index(IOV))%200==0 and (IOVs.index(IOV)+200)<len(IOVs))]

RelevantIOVs.append((RelevantIOVs[-1][2],IOVs[-1],IOVs[-1]))

print RelevantIOVs
for i,splitIOVs in enumerate(RelevantIOVs):
    begin=splitIOVs[0]
    end=splitIOVs[1]
    upperLimit=splitIOVs[1]
    print i,begin,end,upperLimit
    command="conddb_import -f sqlite:dump_one_shot_v1.5_447_232134_256483.db -c sqlite:EcalLaserAPDPNRatios_"+begin+"_"+end+".db -i EcalLaserAPDPNRatios_20151007_232134_256483 -t EcalLaserAPDPNRatios -b "+begin\
+" -e "+end
#+" -e "+upperLimit
    print command
    
    #Now if we want to execute it inside Python uncomment the following two lines:                                                                                      
    STDOUT=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.read()                                                             
    print STDOUT                                                                                                                                                           

#for counter in range(0,len(IOVs),5):                                                                                                                                  
#    if counter+1<len(IOVs):                                                                                                                                               
#        print counter, IOVs[counter], IOVs[counter+1]                                                                                                                     
#    else:                                                                                                                                                                  
#        print counter, IOVs[counter]
