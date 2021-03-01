#! /usr/bin/env python
"""
Perform difference between global tag listed
in autoCond and the corresponding queue.
"""
import re
import os

from Configuration.AlCa.autoCond import autoCond

def global_tags():
    """Get a list of global tags from autoCond"""
    global_tag_list = []
    values = autoCond.values()
    for global_tag in values:
        if isinstance(global_tag, basestring) and global_tag not in global_tag_list:
            global_tag_list.append(global_tag)
    return global_tag_list

def main():
    """Perform difference between autoCond in release
    and the corresponding queue."""
    for global_tag in global_tags():
        queue = re.sub('_v[0-9]*', '_Queue', global_tag)
        queue = re.sub('_Candidate.*', '_Queue', queue)

        # ignore frozen global tags
        if '101X' in global_tag or '103X' in global_tag:
            continue

        # the dataRun2 global tag is currently
        # taken from the 106X_dataRun2_2017_2018_Queue
        if 'dataRun2_v' in global_tag and '105X' not in global_tag and '111X' not in global_tag and '112X' not in global_tag and '113X' not in global_tag:
            queue = queue.replace('Queue', '2017_2018_Queue')

        # this global tag uses a different naming convention
        # for no particular reason
        if 'IdealBS' in global_tag:
            queue = queue.replace('_IdealBS', '')

        # the 'dataRun2_HLT_relval_HI_v' GT is created from
        # the 'dataRun2_HLT_relval' queue
        if 'HLT_relval_HI' in global_tag:
            queue = queue.replace('HI_', '')

        # Diff command
        cmd = 'conddb diff ' + global_tag + ' ' + queue
        os.system(cmd)

if __name__ == "__main__":
    main()