#! /bin/bash
# gfal-rm -r gsiftp://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/analysis/LQ_2017/DY

CHANNEL="mutau"
YEAR="2018"
PATTERN=""
TAG="_norecoil"
while getopts "c:s:t:y:" option; do case "${option}" in
  c) CHANNELS="${OPTARG}";;
  s) PATTERN="${OPTARG}";;
  t) TAG="${OPTARG}";;
  y) YEAR="${OPTARG}";;
esac done
function peval { echo ">>>   $@"; eval "$@"; }

for year in $YEAR; do
  [[ $year = '#'* ]] && continue
  
  OUTPUT="ineuteli/analysis/LQ_$year"
  PNFS_OUTPUT="/pnfs/psi.ch/cms/trivcat/store/user/$OUTPUT"
  SCRATCH_OUTPUT="/scratch/$OUTPUT"
  XRD="root://t3dcachedb.psi.ch:1094"
  
  cd "$SCRATCH_OUTPUT"
  FILES=`ls $PNFS_OUTPUT/*/${PATTERN}*${CHANNEL}.root`
  
  i=0
  N=`echo $FILES | wc -w`
  for f in $FILES; do
    i=$((i+1))
    outfile="$(basename $(dirname $f))/$(basename $f)"
    outfile="$SCRATCH_OUTPUT/${outfile/.root/${TAG}.root}"
    CMD="xrdcp -f ${XRD}/$f $outfile"
    echo
    echo ">>> ${i}/${N}: ${f}"
    peval "$CMD"
  done
  echo
  
done
