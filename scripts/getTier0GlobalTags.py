#!/usr/bin/env python3

import glob
import os
import re
import string
import subprocess
import sys
import time
import json
import datetime
from datetime import datetime

def getFSCR():
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/firstconditionsaferun"])
    response = json.loads(out)["result"][0]
    return int(response)

def getPromptGT():
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/reco_config"])
    response = json.loads(out)["result"][0]['global_tag']
    return response

def getExpressGT():
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/express_config"])
    response = json.loads(out)["result"][0]['global_tag']
    return response

if __name__ == "__main__":
    FSCR = getFSCR()
    promptGT  = getPromptGT()
    expressGT = getExpressGT() 
    print("Current FSCR:",FSCR,"| Express Global Tag",expressGT,"| Prompt Global Tag",promptGT)
