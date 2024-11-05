#!/usr/bin/env python3
'''
Script to retrieve the last IOV of the Tracker Trigger Bits in GT
Usage:

- for Express Global Tag:
python3 printLastIOVTrackerTriggerBits.py --isExpress

- for Prompt Global Tag:
python3 printLastIOVTrackerTriggerBits.py
'''

from datetime import datetime
#from prettytable import PrettyTable
#import ConfigParser
import calendar
from optparse import OptionParser
import glob
import json
import os,sys
import re
import string, re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

##############################################
def getCerts() -> str:
##############################################
    cert_path = os.getenv('X509_USER_CERT', '')
    key_path = os.getenv('X509_USER_KEY', '')

    certs = ""
    if cert_path:
        certs += f' --cert {cert_path}'
    else:
        print("No certificate, nor proxy provided for Tier0 access")
    if key_path:
        certs += f' --key {key_path}'
    return certs

##############################################
def build_curl_command(url, proxy="", certs="", timeout=30, retries=3, user_agent="MyUserAgent"):
##############################################
    """Builds the curl command with the appropriate proxy, certs, and options."""
    cmd = f'/usr/bin/curl -k -L --user-agent "{user_agent}" '

    if proxy:
        cmd += f'--proxy {proxy} '
    else:
        cmd += f'{certs} '

    cmd += f'--connect-timeout {timeout} --retry {retries} {url}'
    return cmd

##############################################
def get_hlt_fcsr(session):
##############################################
    RunInfo = session.get_dbtype(conddb.RunInfo)
    lastRun = session.query(sqlalchemy.func.max(RunInfo.run_number)).scalar()
    fcsr = lastRun+1
    return int(fcsr)

##############################################
def getFCSR(proxy="", certs=""):
##############################################
    url = "https://cmsweb.cern.ch/t0wmadatasvc/prod/firstconditionsaferun"
    cmd = build_curl_command(url, proxy=proxy, certs=certs)
    out = subprocess.check_output(cmd, shell=True)
    response = json.loads(out)["result"][0]
    return int(response)

##############################################
def getPromptGT(proxy="", certs=""):
##############################################
    url = "https://cmsweb.cern.ch/t0wmadatasvc/prod/reco_config"
    cmd = build_curl_command(url, proxy=proxy, certs=certs)
    out = subprocess.check_output(cmd, shell=True)
    response = json.loads(out)["result"][0]['global_tag']
    return response

##############################################
def getExpressGT(proxy="", certs=""):
##############################################
    url = "https://cmsweb.cern.ch/t0wmadatasvc/prod/express_config"
    cmd = build_curl_command(url, proxy=proxy, certs=certs)
    out = subprocess.check_output(cmd, shell=True)
    response = json.loads(out)["result"][0]['global_tag']
    return response

##############################################
def _getFSCR():
##############################################
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/firstconditionsaferun"])
    response = json.loads(out)["result"][0]
    return int(response)

##############################################
def _getPromptGT():
##############################################
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/reco_config"])
    response = json.loads(out)["result"][0]['global_tag']
    return response

##############################################
def _getExpressGT():
##############################################
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/express_config"])
    response = json.loads(out)["result"][0]['global_tag']
    return response

##############################################
def getAlCaRecoTriggerBitTag(GTMap):
##############################################
    for element in GTMap:
        Record = element[0]
        Label  = element[1]
        Tag    = element[2]
        if(Record=="AlCaRecoTriggerBitsRcd"):
            return Tag

        return "NOTATAG"

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
        print ('%s failed w/ exit code %d' % (command, err))
    return data

##############################################
def parseXML(xmlstring):
##############################################
    outDict = {}
    # create element tree object
    tree = ET.ElementTree(ET.fromstring(xmlstring))
  
    # get root element
    root = tree.getroot()

    for child in root:
        #print(child.tag, child.attrib)
        for gc in child:
            #print(gc.tag, gc.attrib)
            for ggc in gc:
                if(ggc.tag=="item"):
                    #print(ggc.tag)
                    alca=""
                    trigger=""
                    for gggc in ggc:
                        #print(gggc.tag, gggc.text)
                        if(gggc.tag=="first"):
                            alca = gggc.text
                        if(gggc.tag=="second"):
                            trigger = gggc.text
                    outDict[alca]=trigger        

    return outDict

##############################################
if __name__ == "__main__":
##############################################

    if "CMSSW_RELEASE_BASE" in os.environ:
        print("\n")
        print("==================================================")
        print("This script is powered by conddblib")
        print("served to you by",os.getenv('CMSSW_RELEASE_BASE'))
        print("==================================================\n")
    else: 
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("+ This tool needs CMSSW libraries")
        print("+ Easiest way to get it is via CMSSW is")
        print("+ cmsrel CMSSW_X_Y_Z  #get your favorite")
        print("+ cd CMSSW_X_Y_Z/src")
        print("+ cmsenv")
        print("+ cd -")
        print("and then you can proceed")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        sys.exit(1)

    parser = OptionParser(usage='Usage: %prog [options] <file> [<file> ...]\n')

    parser.add_option('-E', '--isExpress',
                      dest='express',
                      default=False,
                      action="store_true",
                      help='Set express to True (use for express mode)')
    
    (options, arguments) = parser.parse_args()
    print("value of isExpress =", options.express)
    
    os.environ['X509_USER_KEY'] = os.path.expanduser('~/.globus/userkey.pem')
    os.environ['X509_USER_CERT'] = os.path.expanduser('~/.globus/usercert.pem')
    print("User mode enabled. Using X509_USER_KEY and X509_USER_CERT from ~/.globus/")

    certs = getCerts()
    #FCSR = getFCSR('', certs=certs)

    # Define ANSI color codes for red,green
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    if options.express:
        expressGT = getExpressGT('', certs=certs)
        print(f"Express Global Tag: {RED}{expressGT}{RESET}")
    else:
        promptGT = getPromptGT('', certs=certs)
        print(f"Prompt Global Tag: {RED}{promptGT}{RESET}")
        
    #print("Current FCSR:",FCSR,"| Express Global Tag",expressGT,"| Prompt Global Tag",promptGT,"\n")
    
    ####################################
    # Set up connections with the DB
    ####################################
    import CondCore.Utilities.conddblib as conddb
    con = conddb.connect(url = conddb.make_url("pro"))
    session = con.session()
    IOV     = session.get_dbtype(conddb.IOV)
    TAG     = session.get_dbtype(conddb.Tag)
    GT      = session.get_dbtype(conddb.GlobalTag)
    GTMAP   = session.get_dbtype(conddb.GlobalTagMap)
    RUNINFO = session.get_dbtype(conddb.RunInfo)

    myGlobalTag = expressGT if options.express else promptGT

    GTMap = session.query(GTMAP.record, GTMAP.label, GTMAP.tag_name).\
            filter(GTMAP.global_tag_name == myGlobalTag).\
            order_by(GTMAP.record, GTMAP.label).\
            all()

    myTag = getAlCaRecoTriggerBitTag(GTMap)


    # Print with myTag in red
    print("%s GT AlCaRecoTriggerBit Tag: %s%s%s" % (
        "Express" if options.express else "Prompt", 
        RED, myTag, RESET
    ))
    
    myIOVs = session.query(IOV.since,IOV.payload_hash,IOV.insertion_time).filter(IOV.tag_name == myTag).all()
    myLastIOV = myIOVs[-1]

    # Unpack the tuple for clarity
    since, payload_hash, insertion_time = myLastIOV

    # Format the datetime object
    formatted_time = insertion_time.strftime("%Y-%m-%d %H:%M:%S")

    # Print with labeled fields
    print(f"Last IOV since: {RED}{since}{RESET}, last Payload Hash: {RED}{payload_hash}{RESET}, last insertion time: {RED}{formatted_time}{RESET}\n")

    #print(myLastIOV,"\n")

    if(options.express):
        print("Gonna dump the last express Global Tag IOV. Hang on... ")
    else:
        print("Gonna dump the last prompt Global Tag IOV. Hang on... ")

    command="conddb dump %s" % myLastIOV[1]
    theXML= getCommandOutput(command)
    expressDict = parseXML(theXML)

    print("\n")
    for key, value in expressDict.items():
        if "SiPixel" in key or "SiStrip" in key or "TkAl" in key or "PromptCalib" in key:
            print(f"{RED}{key}{RESET} : [{GREEN}{value}{RESET}]")
            
