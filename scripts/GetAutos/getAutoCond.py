#!/usr/bin/env python
#
# Author:   Marco MUSICH
#
# Usage:
# python getAutoCond.py (-k <name of the key>)

import os
import sys
import optparse
import pprint

#####################################################################
def getCMSSWRelease( ):
    CMSSW_VERSION='CMSSW_VERSION'
    if not os.environ.has_key(CMSSW_VERSION):
        print("\n CMSSW not properly set. Exiting")
        sys.exit(1)
    release = os.getenv(CMSSW_VERSION)
    return release

#####################################################################
if __name__ == '__main__':

    parser = optparse.OptionParser(usage =
                                   'Usage: %prog [options] <file> [<file> ...]\n'
                                   )

    parser.add_option('-k', '--key',
                      dest = 'key',
                      default = "def",
                      help = 'key you want to use to get GT',
                      )
    
    (options, arguments) = parser.parse_args()

    theRelease = getCMSSWRelease()
    print("theRelease:",theRelease)
    
    if(theRelease):
        from Configuration.AlCa.autoCond import autoCond

        listOfKeys=[]

        for key, value in autoCond.iteritems() :
            listOfKeys.append(key)
            
        if(options.key!="def"):
            print(options.key,":",autoCond[options.key])
        else:
            #print(listOfKeys)
            pp = pprint.PrettyPrinter(depth=6)
            pp.pprint(autoCond)
        
