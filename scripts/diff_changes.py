#! /usr/bin/env python
"""
Performs the difference between the GTs in your CMSSW release
directory (including the modifications) with those in $CMSSW_RELEASE_BASE
and prints out a list of URLs showing the set of GT diffs for use in a PR description.
"""
import re
import os
import subprocess
import sys

descriptions = {
    'mcRun1_design' : '**Run 1 design**',
    'mcRun1_realistic' : '**Run 1 realistic**',
    'mcRun1_HeavyIon' : '**Run 1 heavy ion**',
    'mcRun1_pA' : '**Run 1 proton-heavy ion**',
    'mcRun2_startup' : '**Run 2 startup**',
    'mcRun2_asymptotic_l1stage1' : '**Run 2 (L1 trigger stage 1)**',
    'mcRun2_design' : '**2016 design**',
    'mcRun2_asymptotic_preVFP' : '**2016 realistic pre-VFP era**',
    'mcRun2_asymptotic' : '**2016 realistic post-VFP era**',
    'mcRun2cosmics_startup_deco' : '**2016 cosmics (startup conditions)**',
    'mcRun2cosmics_asymptotic_deco' : '**2016 cosmics (asymptotic conditions)**',
    'mcRun2_HeavyIon' : '**Run 2 heavy ion**',
    'mcRun2_pA' : '**Run 2 proton-lead**',
    'dataRun2' : '**Offline data**',
    'dataRun2_2017_2018' : '**Offline data**',
    'dataRun2_HEfail' : '**Offline data (HEM failure)**',
    'dataRun2_relval' : '**Offline data relval**',
    'dataRun2_PromptLike' : '**Prompt-like data**',
    'dataRun2_PromptLike_HEfail' : '**Prompt-like data (HEM15/15 failure)**',
    'dataRun2_PromptLike_HI' : '**Prompt-like HI data**',
    'dataRun2_HLT_frozen' : '**Data (Frozen HLT GT)**',
    'dataRun2_HLT_relval' : '**Run 2 HLT RelVals**',
    'dataRun2_HLT_relval_HI' : '**Run 2 HI HLT RelVals**',
    'dataRun2_HLTHI_frozen' : '**Run 2 HLT for HI (not 2018 HI)**',
    'dataRun3_Express' : '**Run 3 data (express)**',
    'dataRun3_Prompt' : '**Run 3 data (prompt)**',
    'mc2017_design' : '**2017 design**',
    'mc2017_design_IdealBS' : '**2017 design**',
    'mc2017_realistic' : '**2017 realistic**',
    'mc2017cosmics_realistic_deco' : '**2017 realistic cosmics (tracker deco mode)**',
    'mc2017cosmics_realistic_peak' : '**2017 realistic cosmics (tracker peak mode)**',
    'upgrade2018_design' : '**2018 design**',
    'upgrade2018_realistic' : '**2018 realistic**',
    'upgrade2018_realistic_RD' : '**2018 Run-dependent MC**',
    'upgrade2018_realistic_HEfail' : '**2018 realistic (HEM15/16 failure)**',
    'upgrade2018cosmics_realistic_deco' : '**2018 cosmics (tracker deco mode)**',
    'upgrade2018cosmics_realistic_peak' : '**2018 cosmics (tracker peak mode)**',
    'upgrade2018_realistic_HI' : '**2018 heavy ion**',
    'upgrade2021_design' : '**2021 design**',
    'upgrade2021_realistic' : '**2021 realistic**',
    'upgrade2021cosmics_realistic_deco' : '**2021 cosmics**',
    'mcRun3_2021_design' : '**2021 design**',
    'mcRun3_2021cosmics_realistic_deco' : '**2021 cosmics**',
    'mcRun3_2021_realistic' : '**2021 realistic**',
    'mcRun3_2021_realistic_HI' : '**2021 heavy ion**',
    'mcRun3_2023_realistic' : '**2023 realistic**',
    'mcRun3_2024_realistic' : '**2024 realistic**',
    'upgrade2023_realistic' : '**2023 realistic**',
    'mcRun4_realistic' : '**Phase 2 realistic**'}

def global_tags(new_gt):
    """Get a list of global tags that have
    changed since release."""
    file = "Configuration/AlCa/python/autoCond.py"
    manipulations = " | grep '>' | grep X | cut -d ':' -f 2 | sed 's/ //g' | cut -d ',' -f 1"
    manipulations += " | sed \"s/'//g\""
    if new_gt:
        manipulations = manipulations.replace('>', '<')
    cmd = "diff " + os.environ["CMSSW_BASE"] + "/src/" + file
    cmd += " " + os.environ["CMSSW_RELEASE_BASE"] + "/src/" + file
    output = os.popen(cmd + manipulations).read()
    # remove trailing newline as well
    return output[:-1].split('\n')

def checkEnvironment():

    currDir = os.getcwd()

    if not "CMSSW" in currDir:
        sys.exit('!! WARNING !! this script should be executed from the $CMSSW_BASE/src dirctory, exiting!')

    if "CMSSW_BASE" not in os.environ:
        sys.exit('!! WARNING !! This script should be executed after invoking the \'cmsenv\' command, exiting!')

    cmsswBase = os.environ["CMSSW_BASE"]
    if cmsswBase+'/src' != currDir:
        sys.exit('!! WARNING !! This script should be executed in the same $CMSSW_BASE/src directory used to invoke the \'cmsenv\' command, exiting!')

    if not os.path.isdir(currDir+'/Configuration/AlCa'):
        sys.exit('!! WARNING !! Please checkout the Configuration/AlCa package before running this script, exiting!')

def main():
    """Performs the difference between the GTs in your CMSSW release
    directory (including the modifications) with those in $CMSSW_RELEASE_BASE
    and prints out a list of URLs showing the set of GT diffs for use in a PR description."""
    checkEnvironment()
    new_gts = global_tags(True)
    old_gts = global_tags(False)
    diff_links_base = "https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/"
    diff_links = []

    for new_gt in new_gts:
        gt_base = re.sub('_v[0-9]*', '_', new_gt)
        if int(gt_base.split('_')[0][0:2]) < 111:
            gt_base = re.sub('_2017_2018_Candidate.*', '_', gt_base)
        gt_base = re.sub('_Candidate.*', '_', gt_base)
        gt_base = re.sub('_Queue', '_', gt_base)
        old_gt = ''
        for gt in old_gts:
            gt_stripped = re.sub('_v[0-9]*', '_', gt)
            gt_stripped = re.sub('_Candidate.*', '_', gt_stripped)
            if gt_base == gt_stripped:
                old_gt = gt
                break
        cmd = 'conddb diff ' + old_gt + ' ' + new_gt
        diff_link = diff_links_base + old_gt + '/' + new_gt
        if diff_link not in diff_links:
            diff_links.append(diff_link)
        print(cmd)
        os.system(cmd)

    for diff_link in diff_links:
        new_gt = diff_link.split('/')[-1][5:]
        new_gt_base = re.sub('_v[0-9]*', '', new_gt)
        new_gt_base = re.sub('_Candidate.*', '', new_gt_base)
        print(descriptions[new_gt_base])
        print(diff_link + '\n')

if __name__ == "__main__":
    main()
