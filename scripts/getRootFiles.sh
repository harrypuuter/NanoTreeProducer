#! /bin/bash
# gfal-rm -r gsiftp://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/analysis/LQ_2017/DY

CHANNEL="mutau"
YEAR="2018"
while getopts "c:y:" option; do case "${option}" in
  c) CHANNELS="${OPTARG}";;
  y) YEAR="${OPTARG}";;
esac done
function peval { echo ">>> $@"; eval "$@"; }

CAMPAIGNS=""
if [ $YEAR = 2016 ]; then
  CAMPAIGNS="RunIISummer16 Run2016"
elif [ $YEAR = 2017 ]; then
  CAMPAIGNS="RunIIFall17 Run2017 Fall2017 NanoTest_20180507"
else
  CAMPAIGNS="RunIIAutumn18 Run2018"
fi

PATTERNS=""
for campaign in $CAMPAIGNS; do
  PATTERNS+="joblist/joblist_*${campaign}*_mutau.txt "
done

echo
for year in $YEAR; do
  [[ $year = '#'* ]] && continue
  
  for jobfile in $PATTERNS; do
    
    FILELIST=${jobfile//joblist/filelist}
    FILELIST=${FILELIST//_mutau/}
    peval "grep -Po '(?<=-i )[^ ]+' $jobfile | sed 's|,|\n|g' > $FILELIST"
    peval "wc -l $FILELIST"
    echo
    
  done
done
