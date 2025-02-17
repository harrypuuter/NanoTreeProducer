#! /usr/bin/env python
# Author: Izaak Neutelings (May 2019)
import os, re, glob
from commands import getoutput
from fnmatch import fnmatch
import itertools
from argparse import ArgumentParser
from submit import getFileListDAS, getFileListLocal, saveFileListLocal, getBlackList, chunkify, checkExistingFiles
import submit, checkFiles
from checkFiles import getSampleShortName, matchSampleToPattern, header, ensureDirectory

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument('-f', '--force',     dest='force', action='store_true', default=False,
                                           help="submit jobs without asking confirmation" )
  parser.add_argument('-p', '--prefetch',  dest='prefetch', action='store_true', default=False,
                                           help="copy nanoAOD files to a temporary directory before run on it" )
  parser.add_argument('-y', '--year',      dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                           help="select year" )
  parser.add_argument('-s', '--sample',    dest='samples', type=str, nargs='+', default=[ ], action='store',
                                           help="filter these samples, glob patterns (wildcards * and ?) are allowed." )
  parser.add_argument('-x', '--veto',      dest='vetos', nargs='+', default=[ ], action='store',
                                           help="veto this sample" )
  parser.add_argument('-t', '--type',      dest='type', choices=['data','mc'], type=str, default=None, action='store',
                                           help="filter data or MC to submit" )
  ###parser.add_argument('-d', '--das',       dest='useDAS', action='store_true', default=False,
  ###                                         help="get file list from DAS" )
  parser.add_argument('-n', '--njob',      dest='nFilesPerJob', action='store', type=int, default=-1,
                                           help="number of files per job" )
  parser.add_argument('-q', '--queue',     dest='queue', choices=['all.q','short.q','long.q'], type=str, default=None, action='store',
                                           help="select queue for submission" )
  parser.add_argument('-m', '--mock',      dest='mock', action='store_true', default=False,
                                           help="mock-submit jobs for debugging purposes" )
  parser.add_argument(      '--test',      dest='testrun', action='store_true', default=False,
                                           help="submit only one job per sample as a test run" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  submit.args = args
  checkFiles.args = args
else:
  args = None

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Diboson (WW, WZ, ZZ) have very large files and acceptance,
# and the jet-binned DY and WJ files need to be run separately because of a bug affecting LHE_Njets
nFilesPerJob_default  = 4
nFilesPerJob_defaults = [
  #( 1, ['DY',"W*J",'WW','WZ','ZZ','ST','TT_',"TTTo2L2Nu","TTToSemiLep*RunIIFall17",'Single','Tau','EGamma','*VectorLQ_']),
  (40, ['LQ3','*_LQ_']),
]



def createSkimJobs(jobsfile, year, name, infiles, outdir, prefetch=False):
    """Create file with commands to execute per job."""
    extraopts = ""
    if prefetch:
      extraopts += " -p"
    cmd = 'bash submit_skim.sh %s %s %s %s%s'%(year,name.replace('__','/'),','.join(infiles),outdir,extraopts)
    if args.verbose:
      print cmd
    jobsfile.write(cmd+'\n')
    return 1
    

def submitSkimJobs(jobName, jobList, nchunks, logdir, batchscript):
    """Submit job."""
    if args.verbose:
      print 'Reading joblist...'
      print jobList
    extraopts = "-t 1-%s -N %s -o %s"%(nchunks,jobName,logdir)
    if args.queue:
      extraopts += " -q %s"%(args.queue)
    #subCmd = 'qsub -t 1-%s -o logs nafbatch_runner_GEN.sh %s' %(nchunks,jobList)
    subCmd = 'qsub %s %s %s'%(extraopts,batchscript,jobList)
    subCmd = subCmd.rstrip()
    print bcolors.BOLD + bcolors.OKBLUE + "Submitting %d jobs with \n    %s"%(nchunks,subCmd) + bcolors.ENDC
    if not args.mock:
      os.system(subCmd)
    return 1
    

def main():
    
    years       = args.years
    outbasedir  = "/scratch/ineuteli"
    batchscript = 'submit_SGE.sh'
    tag         = ""
    
    for year in years:
      
      # READ SAMPLES
      directories = [ ]
      samplelist  = "samples_%s.cfg"%(year)
      with open(samplelist, 'r') as file:
        for line in file:
          line = line.rstrip().lstrip().split(' ')[0].rstrip('/')
          if line[:2].count('#')>0: continue
          if line=='': continue
          if '/pnfs/' in line: continue
          if args.samples and not matchSampleToPattern(line,args.samples): continue
          if args.vetos and matchSampleToPattern(line,args.vetos): continue
          if args.type=='mc' and any(s in line[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): continue
          if args.type=='data' and not any(s in line[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): continue
          directories.append(line)
      if args.testrun:
        directories = directories[:1]
      blacklist = [ ] #getBlackList("filelist/blacklist.txt")
      
      print header(year,tag)
      
      # SUBMIT SAMPLES
      for directory in directories:
          
          if args.verbose:
            print "\ndirectory =",directory            
          print bcolors.BOLD + bcolors.OKGREEN + directory + bcolors.ENDC
          
          # FILE LIST
          files  = [ ]
          name   = '__'.join(directory.split('/')[-3:])
          sample = '/'+name.replace('__','/')
          ###if not args.useDAS:
          ###    files = getFileListLocal(directory,blacklist=blacklist)
          ###if not files:
          ###if not args.useDAS:
          ###  print "Getting file list from DAS..."
          files = getFileListDAS(directory,blacklist=blacklist)
          ###  if files:
          ###    saveFileListLocal(name,files,blacklist=blacklist)
          if not files:
            print bcolors.BOLD + bcolors.WARNING + "Warning! EMPTY filelist for " + directory + bcolors.ENDC
            continue
          elif args.verbose:
            print "FILELIST = "+files[0]
            for file in files[1:]:
              print "           "+file
          if args.testrun:
            files = files[:1]
          
          # JOB LIST
          ensureDirectory('joblist')
          jobList  = 'joblist/joblist_%s_skim%s.txt'%(name,tag)
          print "Creating job file %s..."%(jobList)
          jobName  = getSampleShortName(directory)[1]
          jobName += "_%s_skim"%(year)+tag
          outdir   = "%s/output_%s/%s"%(outbasedir,year,name)
          logdir   = ensureDirectory("skim_logs_%s/%s"%(year,name))
          
          # NFILESPERJOBS
          nFilesPerJob = args.nFilesPerJob
          if nFilesPerJob<1:
            for default, patterns in nFilesPerJob_defaults:
              if matchSampleToPattern(directory,patterns):
                nFilesPerJob = default
                break
            else:
              nFilesPerJob = nFilesPerJob_default # default
          if args.verbose:
            print "nFilesPerJob = %s"%nFilesPerJob
          filelists = chunkify(files,nFilesPerJob)
          
          # CREATE JOBS
          with open(jobList,'w') as jobs:
            nChunks = 0
            for filelist in filelists:
                createSkimJobs(jobs,year,name,filelist,outdir,prefetch=args.prefetch)
                nChunks = nChunks+1
          
          # SUBMIT
          if args.force:
            submitSkimJobs(jobName,jobList,nChunks,logdir,batchscript)
          else:
            submit = raw_input("Do you also want to submit %d jobs to the batch system? [y/n] "%(nChunks))
            if submit.lower()=='force':
              submit = 'y'
              args.force = True
            if submit.lower()=='quit':
              exit(0)
            if submit.lower()=='y':
              submitSkimJobs(jobName,jobList,nChunks,logdir,batchscript)
            else:
              print "Not submitting jobs"
          print
    


if __name__ == "__main__":
    print
    main()
    print "Done\n"
	

