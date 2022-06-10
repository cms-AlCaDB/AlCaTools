import os

def getGTs():
    ''' 
    look at the keys in the local area autoCond.py dictionary 
    and the one that is in the release.
    output: a dictionary with the GT key
            and a list with the local and release GTs for each key
            
    usage: python3 get_GTdiffs.py 
    '''
    
    file = "Configuration/AlCa/python/autoCond.py"
    new_autoCond = os.environ["CMSSW_BASE"] + "/src/" + file
    old_autoCond = os.environ["CMSSW_RELEASE_BASE"] + "/src/" + file

    print("my autocond = ", new_autoCond)
    print("release autocond = ", old_autoCond)
    
    ## my autoCond:
    from Configuration.AlCa import autoCond 
        
    ## copy the release autoCond to my area:
    os.system(f'cp {old_autoCond} release_autoCond.py')
    
    import release_autoCond as rel_autoCond
    
    autoCond_compare = {}
    
    ## now get the value from each key of release_autoCond and my autoCond:
    for i in rel_autoCond.autoCond.keys():
        # do not consider the keys from the autoCondModifiers.py or old ones in autoCond.py
        if "Fake" in str(i) or "0T" in str(i) or "ddd" in str(i) or "GRun" in str(i) or "FULL" in str(i) or "HIon" in str(i) or "PIon" in str(i) or "PRef" in str(i) or "_T" in str(i) or "upgradeP" in str(i) or "run2_hlt_hi" in str(i) or "_ppref" in str(i) or str(i) == "mc" or "run1_hlt_relval" in str(i) or "run1_data" in str(i) or str(i) == "startup" or "starthi" in str(i) or "com10" in str(i) or "hltonline" in str(i) or "upgrade2017" in str(i) or "upgrade2021" in str(i) or "upgrade2022" in str(i):
            continue
        
        autoCond_compare[i] = [autoCond.autoCond[i], rel_autoCond.autoCond[i]]
        
    #clean up:
    os.system('rm release_autoCond.py')
    os.system('rm -r __pycache__')
    
    return autoCond_compare
    
def do_conddb_diff(autoCond_compare): 
   
    for key,value in autoCond_compare.items():
        if value[0] != value[1]:
            os.system(f'conddb diff {value[0]} {value[1]}')
            
def get_diff_links(autoCond_compare):

    conddbrowser_link = 'https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts' 
    for key,value in autoCond_compare.items():
        if value[0] != value[1]:
            print(f'**{key}**')
            print(f'{conddbrowser_link}/{value[0]}/{value[1]}\n')
    
def main():
    autoCond_dict = getGTs()
    
    do_conddb_diff(autoCond_dict)
    get_diff_links(autoCond_dict)

if __name__ == "__main__":
    main()
