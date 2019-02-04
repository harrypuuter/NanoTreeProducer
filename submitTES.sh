#! /bin/bash

YEARS="2018"
CHANNELS='mutau'
SAMPLES="DY"
OPTIONS="-s $SAMPLES"
CHECKDAS=0
RESUBMIT=0
REMOVE=0
TES_FIRST=0.97
TES_LAST=1.03
STEP_SIZE=0.002
TES=`seq $TES_FIRST $STEP_SIZE $TES_LAST`
while getopts "aCc:dcfmRrvy:" option; do case "${option}" in
  a) OPTIONS+=" -a"; CHECKDAS=1;;
  C) CHECKDAS=1;;
  c) CHANNELS="${OPTARG}";;
  d) OPTIONS+=" -d"; CHECKDAS=1;;
  f) OPTIONS+=" -f";;
  m) OPTIONS+=" -m";;
  r) RESUBMIT=1;;
  R) REMOVE=1;;
  y) YEARS="${OPTARG}";;
  v) OPTIONS+=" -v";;
esac done
function peval { echo ">>> $@"; eval "$@"; }

for year in $YEARS; do
  [[ $year = '#'* ]] && continue
  for channel in $CHANNELS; do
    [[ $channel = '#'* ]] && continue
    for tes in $TES; do
      [[ $tes = 1.000 ]] && continue
      for samplename in $SAMPLES; do
        [[ $samplename = '#'* ]] && continue
        
        if [ $CHECKDAS -gt 0 ]; then
          peval "./checkFiles.py -c $channel -y $year --tes $tes $OPTIONS"
        elif [ $RESUBMIT -gt 0 ]; then
          peval "./resubmit.py -c $channel -y $year --tes $tes $OPTIONS"
        elif [ $REMOVE -gt 0 ]; then
          peval "rm output_${year}/${SAMPLES}*/*${channel}_TES${tes/./p}*"
          peval "rm output_${year}/${SAMPLES}*/logs/*${channel}_${year}_TES${tes/./p}*"
        else
          peval "./submit.py -c $channel -y $year --tes $tes $OPTIONS"
        fi
        
      done
    done
  done
done
