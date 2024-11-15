#!/usr/bin/env python

'''Script to compare all the paylaods in two GTs at a give IOV
'''

__author__ = 'Marco Musich'
__copyright__ = 'Copyright 2015, CERN CMS'
__credits__ = ['Salvatore Di Guida']
__license__ = 'Unknown'
__maintainer__ = 'Marco Musich'
__email__ = 'marco.musich@cern.ch'
__version__ = 1

import datetime,time
import os,sys
import string, re
import subprocess
from optparse import OptionParser,OptionGroup

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
        print('%s failed w/ exit code %d' % (command, err))
    return data

#################
def main():            
### MAIN LOOP ###

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"

    desc="""This is a description of %prog."""
    parser = OptionParser(description=desc,version='%prog version 0.1')
    parser.add_option('-r','--run', help='test run number', dest='testRunNumber', action='store', default='251883')
    parser.add_option('-R','--ReferenceGT',help='Reference Global Tag', dest='refGT', action='store', default='GR_H_V58C')
    parser.add_option('-T','--TargetGT'   ,help='Target Global Tag'   , dest='tarGT', action='store', default='74X_dataRun2_HLTValidation_Queue')
    (opts, args) = parser.parse_args()

    out = getCommandOutput("conddb diff "+opts.refGT+" "+opts.tarGT) 

    lines = out.split('\n')
    listOfRefTags = []
    listOfTarTags = []
    listOfRecords = []
    listOfLabels = []

    for line in lines[2:]:
        tags = line.split(" ")
        tag_list = filter(None, tags) # fastest
        #print(tag_list)
        if(len(tag_list)>0):
            listOfRecords.append(tag_list[0])
            listOfRefTags.append(tag_list[2])
            listOfTarTags.append(tag_list[3])
            listOfLabels.append(tag_list[1])

    #print(listOfRefTags)
    #print(listOfTarTags)
    #print(listOfRecords)

    print("The two GTs differ by",len(listOfRefTags),"tags")

    fout=open("diff_"+opts.refGT+"_vs_"+opts.tarGT+"_atRun_"+opts.testRunNumber+".txt",'w+b')
    fout2=open("diff_"+opts.refGT+"_vs_"+opts.tarGT+"_atRun_"+opts.testRunNumber+".twiki",'w+b')  

    count=0

    myDict = {}

    for i in range(len(listOfRefTags)):
        if(("-" in listOfRefTags[i]) or ("-" in listOfTarTags[i]) ):
            continue
        #if(i>10):
        #break
        out2 = getCommandOutput("conddb diff "+listOfRefTags[i]+" "+listOfTarTags[i]+" -s")
        rawIOVs = out2.split('\n')
        for rawIOV in rawIOVs[2:]:
            IOV = rawIOV.split(" ")
            filteredIOVs = filter(None,IOV) # fastest
            if(len(filteredIOVs) > 0):
                b_run = int((filteredIOVs[0].replace('[','')).replace(',',''))
                e_run = -999999
                if ('Infinity' in filteredIOVs[1]):
                    e_run = 9999999
                else:
                    e_run = int(filteredIOVs[1].replace(')',''))
                if (b_run < int(opts.testRunNumber) and e_run > int(opts.testRunNumber)):
                    print("===================================================================")
                    fout.write("=================================================================== \n")
                    count = count+1
                    #print(rawIOVs[0])
                    listOfTags=[]
                    for element in rawIOVs[0].split(" "):
                        if ("pro::" in element):
                            #print(element)
                            listOfTags.append(element.replace("pro::",""))
                    #print(rawIOVs[1])
                    #print(b_run,"-",e_run,filteredIOVs[2],filteredIOVs[3])
                    print("N. "+str(count)+" |Record:",listOfRecords[i]," |label ("+listOfLabels[i]+") differs in IOV:",b_run,"-",e_run)
                    fout.write("N. "+str(count)+" |Record: "+listOfRecords[i]+" |label ("+listOfLabels[i]+") differs in IOV: "+str(b_run)+"-"+str(e_run)+" \n")

                    #out3 = getCommandOutput("conddb search "+filteredIOVs[2]+" --limit 1")
                    #out4 = getCommandOutput("conddb search "+filteredIOVs[3]+" --limit 1")


                    #fout.write("\n")
                    #fout.write(rawIOVs[0]+" \n")
                    #fout.write(rawIOVs[1]+" \n")
                    #fout.write(str(b_run)+"-"+str(e_run)+" "+filteredIOVs[2]+" "+filteredIOVs[3]+" \n")

                    p1 = subprocess.Popen(["conddb","search",filteredIOVs[2]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (out3, err3) = p1.communicate()
   
                    p2 = subprocess.Popen(["conddb","search",filteredIOVs[3]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (out4, err4) = p2.communicate()

                    #print(out3,out4)
                    rawInfoRef = out3.split('\n')
                    rawInfoRefSplit = filter(None,rawInfoRef[5].split(" "))
                    rawInfoTar = out4.split('\n')
                    rawInfoTarSplit = filter(None,rawInfoTar[5].split(" "))
                    
                    refStripDateTime = datetime.datetime.strptime(rawInfoRefSplit[3].replace('-',''), '%Y%m%d').date()
                    tarStripDateTime = datetime.datetime.strptime(rawInfoTarSplit[3].replace('-',''), '%Y%m%d').date()

                    fout.write(rawInfoRefSplit[0]+" "+rawInfoRefSplit[3]+" "+rawInfoRefSplit[4]+" "+listOfTags[0]+" \n")
                    fout.write(rawInfoTarSplit[0]+" "+rawInfoTarSplit[3]+" "+rawInfoTarSplit[4]+" "+listOfTags[1]+" \n")

                    myDict[listOfRecords[i]] = (rawInfoRefSplit[0],rawInfoRefSplit[3],rawInfoRefSplit[4],listOfTags[0],rawInfoTarSplit[0],rawInfoTarSplit[3],rawInfoTarSplit[4],listOfTags[1])

                    if( refStripDateTime <= datetime.date(2015,1,6) ):
                        print(FAIL + rawInfoRefSplit[0]," ",rawInfoRefSplit[3],rawInfoRefSplit[4]," ",listOfTags[0] + ENDC)
                    else:
                        print(rawInfoRefSplit[0]," ",rawInfoRefSplit[3],rawInfoRefSplit[4]," ",listOfTags[0])

                    if( tarStripDateTime < datetime.date(2015,1,6) ):
                        print(FAIL + rawInfoTarSplit[0]," ",rawInfoTarSplit[3],rawInfoTarSplit[4]," ",listOfTags[1] + ENDC)
                    else:
                        print(rawInfoTarSplit[0]," ",rawInfoTarSplit[3],rawInfoTarSplit[4]," ",listOfTags[1])

    fout2.write("| *Record* | *"+opts.refGT+"* | *"+opts.tarGT+"* |\n")
    for key in myDict:
        #print key, 'corresponds to', myDict[key]
        fout2.write("| ="+key+"= | =="+myDict[key][3]+"==  | =="+myDict[key][7]+"== |\n")
        fout2.write("|^| "+myDict[key][0]+" ("+myDict[key][1]+" "+myDict[key][2]+") | "+myDict[key][4]+" ("+myDict[key][5]+" "+myDict[key][6]+") |\n") 

if __name__ == "__main__":        
    main()


