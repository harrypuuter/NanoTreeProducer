#! /usr/bin/env python
# Authors: Izaak Neutelings (May 2019)
import os, glob, sys, shlex, re
#import time
from fnmatch import fnmatch
import subprocess
from argparse import ArgumentParser
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TFile, TTree, TH1, Double
import submit, submit_skim, checkFiles
from submit import getFileListLocal, getFileListDAS, nFilesPerJob_defaults, chunkify
from submit_skim import createSkimJobs, submitSkimJobs
from checkFiles import bcolors, header, ensureDirectory, getSampleShortName, matchSampleToPattern, naturalSort, compareEventsToDAS


if __name__ == '__main__':
    description = '''Check if the job output files are valid, compare the number of events to DAS (-d), hadd them into one file per sample (-m), and merge datasets (-a).'''
    parser = ArgumentParser(prog="checkFiles",description=description,epilog="Good luck!")
    parser.add_argument('-y', '--year',     dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                            help="select year" )
    parser.add_argument('-p', '--prefetch', dest='prefetch', action='store_true', default=False,
                                            help="copy nanoAOD files to a temporary directory before run on it" )
    parser.add_argument('-d', '--das',      dest='compareToDas', default=False, action='store_true',
                                            help="compare number of events in output to das" )
    parser.add_argument('-R', '--rm-bad',   dest='removeBadFiles', default=False, action='store_true',
                                            help="remove files that are bad (zombies, no tree, no cutflow, ...)" )
    parser.add_argument(      '--rm-bug',   dest='removeBuggedFiles', default=False, action='store_true',
                                            help="remove files that have bad LHE_Njets" )
    parser.add_argument('-L', '--local',    dest='useLocal', action='store_true', default=False,
                                            help="get file list from local list" )
    parser.add_argument('-o', '--outdir',   dest='outdir', type=str, default=None, action='store' )
    parser.add_argument('-s', '--sample',   dest='samples', default=[ ], type=str, nargs='+', action='store',
                                            help="samples to run over, glob patterns (wildcards * and ?) are allowed." )
    parser.add_argument('-x', '--veto',     dest='vetos', default=[ ], nargs='+', type=str, action='store',
                                            help="veto this sample" )
    parser.add_argument('-t', '--type',     dest='type', choices=['data','mc'], type=str, default=None, action='store',
                                            help="filter data or MC to submit" )
    parser.add_argument('-f', '--force',    dest='force', action='store_true', default=False,
                                            help="submit jobs without asking confirmation" )
    parser.add_argument('-m', '--mock',     dest='mock', action='store_true', default=False,
                                            help="mock-submit jobs for debugging purposes" )
    parser.add_argument('-n', '--njob',     dest='nFilesPerJob', action='store', type=int, default=-1,
                                            help="number of files per job" )
    parser.add_argument('-q', '--queue',    dest='queue', choices=['all.q','short.q','long.q'], type=str, default=None, action='store',
                                            help="select queue for submission" )
    parser.add_argument('-l', '--tag',      dest='tag', type=str, default="", action='store',
                                            help="add a tag to the output file" )
    parser.add_argument('-v', '--verbose',  dest='verbose', default=False, action='store_true',
                                            help="set verbose" )
    args = parser.parse_args()
    submit.args = args
    submit_skim.args = args
    checkFiles.args = args
else:
  args = None
  


def main(args):
  
  years       = args.years
  tag         = args.tag
  outbasedir  = "/scratch/ineuteli"
  batchscript = 'submit_SGE.sh'
  director    = "root://t3dcachedb.psi.ch:1094/" #"root://xrootd-cms.infn.it/"
  
  for year in years:
    samplesdir = args.outdir if args.outdir else "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_%s"%(year)
    
    # GET LIST
    samplelist = [ ]
    for directory in sorted(glob.glob(samplesdir+"/*/*/NANOAOD*")):
      sample = '/'.join(directory.split('/')[-3:])
      if args.samples and not matchSampleToPattern(sample,args.samples): continue
      if args.vetos and matchSampleToPattern(sample,args.vetos): continue
      if args.type=='mc' and any(s in sample[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): continue
      if args.type=='data' and not any(s in sample[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): continue
      if not os.path.isdir(directory): continue
      samplelist.append(directory)
    if not samplelist:
      print "No samples found in %s!"%(samplesdir)
    if args.verbose:
      print 'samplelist = %s\n'%(samplelist)
    
    # CHECK samples
    print header(year,tag)    
    for directory in samplelist:
        
        sample   = '__'.join(directory.split('/')[-3:])
        filelist = '%s/*_skim%s*.root'%(directory,tag)
        if args.verbose:
          print "directory  = %s"%(directory)
          print "filelist   = %s"%(filelist)
          print "sample     = %s"%(sample)
        
        # FILE LIST ON SE
        filelist = [director+d for d in sorted(glob.glob(filelist),key=naturalSort)]
        if not filelist:
          print bcolors.BOLD + bcolors.WARNING + "[WN] %s empty filelist"%directory + bcolors.ENDC
        elif args.verbose:
          print "filelist   = %s"%(filelist[0])
          for file in filelist[1:]:
            print "             "+file
        
        # FILE LIST ON DAS
        infilelist = [ ]
        if args.useLocal:
            infilelist = getFileListLocal(sample)
        if not infilelist:
          if args.useLocal:
            print "Getting file list from DAS/PNFS..."
          infilelist = getFileListDAS(sample)
        if not infilelist:
          print bcolors.BOLD + bcolors.WARNING + "Warning! EMPTY filelist for " + directory + bcolors.ENDC
        elif args.verbose:
          print "infilelist = %s"%(infilelist[0])
          for file in infilelist[1:]:
            print "             "+file
        
        # FILE LIST FOR RESUBMISSION
        nevents, resubmitfiles = checkFiles(filelist,infilelist,directory,clean=args.removeBadFiles,force=args.force,cleanBug=args.removeBuggedFiles)
        if len(resubmitfiles)==0:
          print bcolors.BOLD + bcolors.OKGREEN + '[OK] %s is complete ! '%sample + bcolors.ENDC
        elif len(resubmitfiles)>len(infilelist):
          print bcolors.BOLD + bcolors.FAIL + 'WARNING! %s has more output files %d than %d input files from DAS!'%(sample,len(resubmitfiles),len(infilelist)) + bcolors.ENDC
        else:
          print bcolors.BOLD + bcolors.WARNING + '[WN] %d / %d of %s need to be resubmitted...'%(len(resubmitfiles),len(infilelist),sample) + bcolors.ENDC
        
        if not any(s in directory for s in ['LQ3']):
          compareEventsToDAS(nevents,sample,treename='Events')
        if len(resubmitfiles)==0:
          print
          continue
        
        # JOB LIST
        ensureDirectory('joblist')
        jobList  = 'joblist/joblist_%s_skim%s_retry.txt'%(sample,tag)
        print "Creating job file %s..."%(jobList)
        jobName  = getSampleShortName(directory)[1]
        jobName += "_%s_skim"%(year)+tag
        outdir   = "%s/output_%s/%s"%(outbasedir,year,sample)
        logdir   = ensureDirectory("skim_logs_%s/%s"%(year,sample))
        
        # NFILESPERJOBS
        nFilesPerJob = args.nFilesPerJob
        if nFilesPerJob<1:
          for default, patterns in nFilesPerJob_defaults:
            if matchSampleToPattern(directory,patterns):
              nFilesPerJob = default
              break
          else:
            nFilesPerJob = 1 # default
        if args.verbose:
          print "nFilesPerJob = %s"%nFilesPerJob
        filelists = chunkify(resubmitfiles,nFilesPerJob)
        
        # CREATE JOBS
        with open(jobList,'w') as jobs:
          nChunks = 0
          for filelist in filelists:
              createSkimJobs(jobs,year,sample,filelist,outdir,prefetch=args.prefetch)
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
        
   


def checkFiles(filelist,infilelist,directory,clean=False,force=False,cleanBug=False,treename='Events'):
    """Check if the file is valid."""
    
    if args.verbose:
      print "checkFiles: %s, %s, %s"%(directory,filelist,infilelist)
    
    if isinstance(filelist,str):
      filelist = [filelist]
    infiledict = { f.split('/')[-1].replace('.root',''): f for f in infilelist }
    
    goodfiles = { } # good files
    badfiles  = { } # corrupted files
    bugfiles  = { } # buggy files
    nfiles    = len(filelist)
    
    # CHECK FILES
    # TODO: check timestamp
    ntotevents = 0
    for filename in filelist:
      file    = TFile.Open(filename, 'READ')
      filekey = re.sub(r"(?:_skim.*)?\.root","",filename.split('/')[-1])
      if file==None:
        print bcolors.FAIL + '[NG] file %s is None'%(filename) + bcolors.ENDC
        appendListInDict(badfiles,filekey,filename)
        continue
      elif file.IsZombie():
        print bcolors.FAIL + '[NG] file %s is a zombie'%(filename) + bcolors.ENDC
        appendListInDict(badfiles,filekey,filename)
      else:
        tree = file.Get(treename)
        if not isinstance(tree,TTree):
          print bcolors.FAIL + '[NG] no tree found in ' + filename + bcolors.ENDC
          appendListInDict(badfiles,filekey,filename)
        elif any(s in filename for s in ['DYJets','WJets']) and tree.GetMaximum('LHE_Njets')>10:
          print bcolors.BOLD + bcolors.WARNING + '[WN] %d/%d events have LHE_Njets = %d > 10 in %s'%(tree.GetEntries(),tree.GetEntries("LHE_Njets>10"),tree.GetMaximum('LHE_Njets'),filename) + bcolors.ENDC
          appendListInDict(bugfiles,filekey,filename)
        else:
          appendListInDict(goodfiles,filekey,filename)
        if isinstance(tree,TTree):
          ntotevents += tree.GetEntries()
      file.Close()
    
    # MAKE RESUBMIT LIST
    resubmitfiles = [ ]
    for filename in infilelist:
      filekey   = filename.split('/')[-1].replace('.root','')
      noutfiles = len(goodfiles.get(filekey,[ ])+badfiles.get(filekey,[ ])+bugfiles.get(filekey,[ ]))
      if noutfiles>1:
        print bcolors.BOLD + bcolors.WARNING + '[WN] %s has more than one output file\n\tgood:  %s\n\tbad:   %s\n\tbuggy: %s'%(filename,goodfiles.get(filekey,[ ]),badfiles.get(filekey,[ ]),bugfiles.get(filekey,[ ])) + bcolors.ENDC
      elif noutfiles==0:
        print bcolors.BOLD + bcolors.WARNING + '[WN] %s is missing an output file'%(filename) + bcolors.ENDC
        resubmitfiles.append(filename)
        continue
      elif filekey in badfiles or filekey in bugfiles:
        resubmitfiles.append(filename)
    
    return ntotevents, resubmitfiles
    

def appendListInDict(mydict,key,item):
    """Help function to create empty list for a given key in a dictionary if it does not exist yet,
    and append it with a given item."""
    mydict.setdefault(key,[ ])
    mydict[key].append(item)
    


if __name__ == '__main__':
    print
    main(args)
    print
    

