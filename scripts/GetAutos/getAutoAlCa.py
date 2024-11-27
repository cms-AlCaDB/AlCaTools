#!/usr/bin/env python
#
# Author:   Marco MUSICH
#
# Usage:
# python getAutoAlCa.py (-k <name of the key>)

import os
import sys
import optparse
import pprint

#####################################################################
def getCMSSWRelease( ):
    CMSSW_VERSION='CMSSW_VERSION'
    if not CMSSW_VERSION in os.environ:
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
        from Configuration.AlCa.autoAlca import AlCaRecoMatrix

        listOfKeys=[]

        for key, value in AlCaRecoMatrix.iteritems() :
            listOfKeys.append(key)
            
        if(options.key!="def"):
            print(options.key,":",AlCaRecoMatrix[options.key])
        else:
            print(listOfKeys)

        #pp = pprint.PrettyPrinter(depth=6)
        #pp.pprint(autoCond)
