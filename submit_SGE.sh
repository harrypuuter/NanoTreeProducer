#! /bin/bash
## Script to run on a Sun Grid Engine batch system
## make sure the right shell will be used
#$ -S /bin/bash
## Black list nodes
##$ -l h=t3wn43.psi.ch
##$ -l h=!t3wn34.psi.ch
##$ -l h=!t3wn5*.psi.ch
##$ -l h=!(t3wn34.psi.ch|t3wn5*.psi.ch)
## the cpu time for this job
#$ -l h_rt=04:20:00
## the maximum memory usage of this job
#$ -l h_vmem=5900M
## Job Name
#$ -N test
## stderr and stdout are merged together to stdout
#$ -j y
## transfer env var from submission host
#$ -V
## set cwd to submission host pwd
#$ -cwd


echo job start at `date`
echo "Running job on machine $((uname -a))"

# export TASKID=$((SGE_TASK_ID))
TASKID=$(($1+1))
JOBLIST=$2
echo "\$SGE_TASK_ID=$TASKID"
echo "\$HOSTNAME=$HOSTNAME"
echo "\$JOBLIST=$JOBLIST"

echo "export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/NanoTreeProducer"
export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/NanoTreeProducer
echo "PYTHONPATH=$PYTHONPATH"
TASKCMD=$(cat $JOBLIST | sed "${TASKID}q;d")

#eval $(scramv1 runtime -sh);
pwd
echo "Going to execute"
echo "  $TASKCMD"
eval $TASKCMD;
ls -lrth

echo "Job complete at $((date))";
