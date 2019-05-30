#! /bin/bash
# gfal-rm -r gsiftp://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/analysis/LQ_2017/DY


YEAR='2018'
OUTPUT="$USER/samples/NANOAOD_${YEAR}"
PNFS_OUTPUT="/pnfs/psi.ch/cms/trivcat/store/user/$OUTPUT"
XRD="root://t3dcachedb.psi.ch:1094"
GFL="gsiftp://t3se01.psi.ch"
function peval { echo ">>> $@"; eval "$@"; }

for dir in `ls $PNFS_OUTPUT`; do
  printf "\n# $dir\n"
  for oldfile in `ls $PNFS_OUTPUT/$dir/`; do
    newfile="${oldfile%_skim*}_skimmed.root"
    echo $oldfile
    #echo $newfile
    #CMD="gfal-rename $GFL/$PNFS_OUTPUT/$dir/$oldfile $GFL/$PNFS_OUTPUT/$dir/$newfile"
    #peval "$CMD"
  done
done
echo
