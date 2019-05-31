#! /bin/bash
# gfal-rm -r gsiftp://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/analysis/LQ_2017/DY

YEAR=2018
OUTPUT="$USER/samples/NANOAOD_${YEAR}"
PNFS_OUTPUT="/pnfs/psi.ch/cms/trivcat/store/user/$OUTPUT"
XRD="root://t3dcachedb.psi.ch:1094"
GFL="gsiftp://t3se01.psi.ch"
function peval { echo ">>> $@"; eval "$@"; }

for dir in `ls $PNFS_OUTPUT | grep "__NANOAOD"`; do
  printf "\n# $dir\n\n"
  
  NEWDIR="${dir//__//}"
  
  echo ">>> create $NEWDIR..."
  if [ ! -e "$PNFS_OUTPUT/$NEWDIR" ]; then
    peval "gfal-mkdir -p $GFL/$PNFS_OUTPUT/$NEWDIR"
    TRY=0
    printf ">>> checking success..."
    while [ ! -e "$PNFS_OUTPUT/$NEWDIR" -a $TRY -lt 25 ]; do
      printf "."; sleep 4; TRY=$((TRY+1))
    done
    echo
    [ ! -e "$PNFS_OUTPUT/$NEWDIR" ] && echo ">>> failed to make $NEWDIR?" && continue
  fi
  
  NFILES=`ls $PNFS_OUTPUT/$dir/ | wc -l`
  [ $NFILES = 0 ] && printf ">>> zero files! Skipping...\n\n" && continue
  echo ">>> moving $NFILES rootfiles..."
  for rootfile in `ls $PNFS_OUTPUT/$dir/`; do
    peval "gfal-rename $GFL/$PNFS_OUTPUT/$dir/$rootfile $GFL/$PNFS_OUTPUT/$NEWDIR/$rootfile"
  done
  echo
  
done
echo

# for dir in /pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/*__NANO*; do peval "uberftp -rm  gsiftp://t3se01.psi.ch/$dir"; done