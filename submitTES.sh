#! /bin/bash

YEARS="2016 2017 2018"
CHANNELS='mutau'
SAMPLES="DY"
OPTIONS=""
CHECKDAS=0
RESUBMIT=0
REMOVE=0
VARFLAG="--tes"
TES_FIRST=0.972
TES_LAST=1.028
STEP_SIZE=0.002
VARIATIONS=`seq $TES_FIRST $STEP_SIZE $TES_LAST`
while getopts "aBCc:dcfJLmRrs:Tvx:y:" option; do case "${option}" in
  a) OPTIONS+=" -a"; CHECKDAS=1;;
  B) OPTIONS+=" --rm-bad --rm-bug";;
  C) CHECKDAS=1;;
  c) CHANNELS="${OPTARG}";;
  d) OPTIONS+=" -d"; CHECKDAS=1;;
  f) OPTIONS+=" -f";;
  J) VARFLAG="--jtf"; VARIATIONS="0.900 1.100"; SAMPLES="DY W*J TT";;
  L) VARFLAG="--ltf"; VARIATIONS="0.970 1.030"; SAMPLES="DY TT";;
  m) OPTIONS+=" -m";;
  R) RESUBMIT=1;;
  r) OPTIONS+=" -r"; REMOVE=1;;
  s) SAMPLES="${OPTARG}";;
  T) VARFLAG="--tes"; VARIATIONS="0.970 1.030"; SAMPLES="DY TT";;
  v) OPTIONS+=" -v";;
  x) OPTIONS+=" -x ${OPTARG}";;
  y) YEARS=${OPTARG//,/ };;
esac done
OPTIONS="-s ${SAMPLES}${OPTIONS}"
function peval { echo ">>> $@"; eval "$@"; }

for year in $YEARS; do
  [[ $year = '#'* ]] && continue
  for channel in $CHANNELS; do
    [[ $channel = '#'* ]] && continue
    for var in $VARIATIONS; do
      [[ $var = 1.000 ]] && continue
      
      if [ $CHECKDAS -gt 0 ]; then
        peval "./checkFiles.py -c $channel -y $year $VARFLAG $var $OPTIONS"
      elif [ $RESUBMIT -gt 0 ]; then
        peval "./resubmit.py -c $channel -y $year $VARFLAG $var $OPTIONS"
      elif [ $REMOVE -gt 0 ]; then
        for samplename in $SAMPLES; do
          peval "rm output_${year}/${samplename}*/*${channel}_TES${var/./p}*"
          peval "rm output_${year}/${samplename}*/logs/*${channel}_${year}_TES${var/./p}*"
        done
      else
        peval "./submit.py -c $channel -y $year $VARFLAG $var $OPTIONS"
      fi
      
    done
  done
done
