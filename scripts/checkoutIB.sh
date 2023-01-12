export CMSSW_BRANCH=$1
export MASTER_BRANCH=13_0_X

if [[ ${CMSSW_BRANCH} = "12_2_X" ]]
then
    export SCRAM_ARCH=slc7_amd64_gcc900
elif [[ ${CMSSW_BRANCH} = "12_4_X" ]]
then
    export SCRAM_ARCH=slc7_amd64_gcc10
elif [[ ${CMSSW_BRANCH} = "12_5_X" ]]
then
    export SCRAM_ARCH=slc7_amd64_gcc10
elif [[ ${CMSSW_BRANCH} = "12_6_X" ]]
then
    export SCRAM_ARCH=el8_amd64_gcc10
else
    export SCRAM_ARCH=el8_amd64_gcc11
fi


export CMSSW_VERSION=`scram list -c CMSSW | grep CMSSW_${CMSSW_BRANCH} | tail -1 | awk '{print $2}'`
echo $SCRAM_ARCH
echo $CMSSW_BRANCH
echo $CMSSW_VERSION
scramv1 project CMSSW $CMSSW_VERSION
cd $CMSSW_VERSION/src
eval `scramv1 runtime -sh`
git cms-addpkg Configuration/AlCa

export BRANCH_BASE=`pwd | awk -F '/' '{print $(NF-2)}'`
if [[ ${CMSSW_BRANCH} = ${MASTER_BRANCH} ]]
then
    export BRANCH=alca-${BRANCH_BASE}
else
    export BRANCH=alca-${BRANCH_BASE}_${CMSSW_BRANCH}
fi
git checkout -b ${BRANCH}
