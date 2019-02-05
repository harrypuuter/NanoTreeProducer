#! /bin/bash

CHANNELS='mutau mumu tautau'
YEAR="2018"
while getopts "c:y:" option; do case "${option}" in
  c) CHANNELS="${OPTARG}";;
  y) YEAR="${OPTARG}";;
esac done

[ "$YEAR" != 2016 -a "$YEAR" != 2018 ] && echo ">>> ERROR! Year $YEAR not valid!" && exit 1

SCRATCHOLD="/scratch/ineuteli/analysis/LQ_2017"
SCRATCHNEW="/scratch/ineuteli/analysis/LQ_$YEAR"

if [ "$YEAR" == "2016" ]; then
  SAMPLES="
    DY/DY3JetsToLL_M-50
    DY/DY4JetsToLL_M-50
  "
else
  SAMPLES="
    DY/DY4JetsToLL_M-50
    WJ/WJetsToLNu
    ST/ST_t-channel_top
    ST/ST_t-channel_antitop
  "
fi

for channel in $CHANNELS; do
  [[ $channel = '#'* ]] && continue
  for samplename in $SAMPLES; do
    [[ $samplename = '#'* ]] && continue
    echo $samplename
    
    fileold="$SCRATCHOLD/${samplename}_${channel}.root"
    filenew="$SCRATCHNEW/${samplename}_${channel}.root"  
    [ ! -e $fileold ] && echo "Warning! $fileold does not exist!" && continue 
    
    echo "Copying $fileold to $filenew!"
    cp -v $fileold $filenew
  done
done
