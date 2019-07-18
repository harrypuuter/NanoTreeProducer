#! /bin/bash
# Author: Izaak Neutelings (May 2019)
# Description: check errors, and which queue/hosts are affected

BASEDIR="/work/ineuteli/analysis/LQ_legacy/NanoTreeProducer"
LOGDIRS="$BASEDIR/skim_logs_201*/*"
[ "$1" ] && LOGDIRS="$1"
ERROR="TNetXNGFile" #"gfal2.GError"
ALLHOSTS=""
SHOWLOGS=1

for logdir in $LOGDIRS; do
  
  printf "\n# ${logdir}\n"
  LOGFILES="$logdir/*"
  BADFILES=`grep -l "$ERROR" $LOGFILES`
  NFILES=`echo $LOGFILES | wc -w`
  
  if [ "$BADFILES" = '' ]; then
    echo "  no instance of '$ERROR' found in any of the $NFILES files"
    continue
  fi
  NBADFILES=`echo $BADFILES | wc -w`
  
  # PRINT AFFECTED HOSTS
  echo "  found instances of '$ERROR' in $NBADFILES / $NFILES files, the affected hosts:"
  HOSTS=`grep -Poh "(?<=queue@host = ).*" $BADFILES | sort | uniq`
  ALLHOSTS+=" $HOSTS"
  for queue in $HOSTS; do
    echo "    $queue"
  done
  
  # PRINT AFFECTED LOG FILES
  if [ $SHOWLOGS -gt 0 ]; then
    echo "  log files:"
    for logfile in $BADFILES; do
      echo "    $logfile"
    done
  fi
  
done

# PRINT SUMMARY OF HOSTS
ALLHOSTS=`echo $ALLHOSTS | xargs -n1 | sort | uniq`
printf "\n# SUMMARY OF HOSTS AFFECTED:\n"
for queue in $ALLHOSTS; do
  echo "    $queue"
done

# CHECK FRACTION OF HOST's jobs affectred
printf "\n# FRACTION OF JOBS ON QUEUE AFFECTED:\n"
for queue in $ALLHOSTS; do
  
  LOGFILES=`grep -Pl "queue@host = $queue" $LOGDIRS/*`
  echo $LOGFILES
  NFILES=`echo $LOGFILES | wc -w`
  NBADFILES=`grep -l "$ERROR" $LOGFILES | wc -l`
  printf "    %3s /%4s: %s\n" $NBADFILES $NFILES $queue
  
done


echo;