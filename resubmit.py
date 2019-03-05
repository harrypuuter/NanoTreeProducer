#! /usr/bin/env python

import os, glob, sys, shlex, re
from commands import getoutput
from argparse import ArgumentParser
import submit, checkFiles
from checkFiles import getSampleShortName, matchSampleToPattern, header
from submit import args, bcolors, nFilesPerJob_defaults, createJobs, getFileListLocal, getFileListPNFS, getFileListDAS, submitJobs, split_seq
import itertools
import subprocess
from ROOT import TFile, Double

parser = ArgumentParser()
parser.add_argument('-f', '--force',   dest='force', action='store_true', default=False,
                                       help="submit jobs without asking confirmation" )
parser.add_argument('-y', '--year',    dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                       help="select year" )
parser.add_argument('-c', '--channel', dest='channels', choices=['eletau','mutau','tautau','mumu'], type=str, nargs='+', default=['mutau'], action='store',
                                       help="channels to submit" )
parser.add_argument('-s', '--sample',  dest='samples', type=str, nargs='+', default=[ ], action='store',
                                       help="filter these samples, glob patterns (wildcards * and ?) are allowed." )
parser.add_argument('-x', '--veto',    dest='vetos', type=str, nargs='+', default=[ ], action='store',
                                       help="veto this sample" )
parser.add_argument('-t', '--type',    dest='type', choices=['data','mc'], type=str, default=None, action='store',
                                       help="filter data or MC to submit" )
parser.add_argument('-T', '--tes',     dest='tes', type=float, default=1.0, action='store',
                                       help="tau energy scale" )
parser.add_argument('-L', '--ltf',     dest='ltf', type=float, default=1.0, action='store',
                                       help="lepton to tau fake energy scale" )
parser.add_argument('-J', '--jtf',     dest='jtf', type=float, default=1.0, action='store',
                                       help="jet to tau fake energy scale" )
parser.add_argument('-d', '--das',     dest='useDAS', action='store_true', default=False,
                                       help="get file list from DAS" )
parser.add_argument('-n', '--njob',    dest='nFilesPerJob', action='store', type=int, default=-1,
                                       help="number of files per job" )
parser.add_argument('-q', '--queue',   dest='queue', choices=['all.q','short.q','long.q'], type=str, default=None, action='store',
                                       help="select queue for submission" )
parser.add_argument('-m', '--mock',    dest='mock', action='store_true', default=False,
                                       help="mock-submit jobs for debugging purposes" )
parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                                       help="set verbose" )
args = parser.parse_args()
checkFiles.args = args
submit.args = args

def main():
    
    channels     = args.channels
    years        = args.years
    tes          = args.tes
    ltf          = args.ltf
    jtf          = args.jtf
    batchSystem  = 'psibatch_runner.sh'    
    chunkpattern = re.compile(r".*_(\d+)_[a-z]+(?:_[A-Z]+\dp\d+)?\.root")
    tag          = ""
    
    if tes!=1.:
      tag += "_TES%.3f"%(tes)
    if ltf!=1.:
      tag += "_LTF%.3f"%(ltf)
    if jtf!=1.:
      tag += "_JTF%.3f"%(jtf)
    tag = tag.replace('.','p')
    
    for year in years:
      
      # GET LIST
      samplelist = [ ]
      outdir     = "output_%s/"%(year)
      for directory in sorted(os.listdir(outdir)):
          if not os.path.isdir(outdir+directory): continue
          if args.samples and not matchSampleToPattern(directory,args.samples): continue
          if args.vetos and matchSampleToPattern(directory,args.vetos): continue
          if args.type=='mc' and any(s in directory[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau']): continue
          if args.type=='data' and not any(s in directory[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau']): continue
          samplelist.append(directory)
      if not samplelist:
        print "No samples found in %s!"%(outdir)
      if args.verbose:
        print samplelist
      
      # RESUBMIT samples
      for channel in channels:
        print header(year,channel,tag)
        
        for directory in samplelist:
            #if directory.find('W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8__ytakahas-NanoTest_20180507_W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8-a7a5b67d3e3590e4899e147be08660be__USER')==-1: continue
            outdir       = "output_%s/%s"%(year,directory)
            outfilelist  = glob.glob("%s/*_%s%s.root"%(outdir,channel,tag))
            nFilesPerJob = args.nFilesPerJob
            jobName      = getSampleShortName(directory)[1]
            jobName     += "_%s_%s"%(channel,year)+tag
            if not outfilelist: continue            
            
            # FILE LIST
            infiles = [ ]
            if not args.useDAS:
                infiles = getFileListLocal(directory)
            if not infiles:
              if not args.useDAS:
                print "Getting file list from DAS..."
              if 'LQ3' in directory:
                infiles = getFileListPNFS('/pnfs/psi.ch/cms/trivcat/store/user/ytakahas/'+directory)
              else:
                infiles = getFileListDAS('/'+directory)
              if infiles:
                saveFileListLocal(directory,infiles)
            if not infiles:
              print bcolors.BOLD + bcolors.WARNING + "Warning!!! FILELIST empty" + bcolors.ENDC
              continue
            elif args.verbose:
              print "FILELIST = "+infiles[0]
              for file in infiles[1:]:
                print "           "+file
            
            # NFILESPERJOBS
            nFilesPerJob = args.nFilesPerJob
            if nFilesPerJob<1:
              for default, patterns in nFilesPerJob_defaults:
                if matchSampleToPattern(directory,patterns):
                  nFilesPerJob = default
                  break
              else:
                nFilesPerJob = 4
            if args.verbose:
              print "nFilesPerJob = %s"%nFilesPerJob
            infilelists = list(split_seq(infiles,nFilesPerJob))
            
            # JOB LIST
            badchunks   = [ ]
            misschunks  = range(0,len(infilelists))
            jobList = 'joblist/joblist_%s_%s%s_retry.txt'%(directory,channel,tag)
            with open(jobList, 'w') as jobslog:
              for filename in outfilelist:
                  match = chunkpattern.search(filename)
                  if match:
                    chunk = int(match.group(1))
                  else:
                    print bcolors.BOLD + bcolors.FAIL + '[NG] did not recognize output file %s !'%(filename) + bcolors.ENDC
                    exit(1)
                  if chunk in misschunks:
                    misschunks.remove(chunk)
                  elif chunk >= len(infilelists):
                    print bcolors.BOLD + bcolors.FAIL + '[WN] %s: found chunk %s >= total number of chunks %s ! Please make sure you have chosen the correct number of files per job (-n=%s), check DAS, or resubmit everything!'%(filename,chunk,len(infilelists),nFilesPerJob) + bcolors.ENDC
                  else:
                    print bcolors.BOLD + bcolors.FAIL + '[WN] %s: found weird chunk %s ! Please check if there is any overcounting !'%(filename,chunk,len(infilelists)) + bcolors.ENDC
                  file = TFile(filename,'READ')
                  if not file.IsZombie() and file.GetListOfKeys().Contains('tree') and file.GetListOfKeys().Contains('cutflow'):
                    continue
                  infiles = infilelists[chunk]
                  createJobs(jobslog,infiles,outdir,directory,chunk,channel,year=year,tes=tes,ltf=ltf,jtf=jtf)
                  badchunks.append(chunk)
              
              # BAD CHUNKS
              if len(badchunks)>0:
                badchunks.sort()
                chunktext = ('chunks ' if len(badchunks)>1 else 'chunk ') + ', '.join(str(ch) for ch in badchunks)
                print bcolors.BOLD + bcolors.WARNING + '[NG] %s, %d/%d failed! Resubmitting %s...'%(directory,len(badchunks),len(outfilelist),chunktext) + bcolors.ENDC
              
              # MISSING CHUNKS
              if len(misschunks)>0:
                chunktext = ('chunks ' if len(misschunks)>1 else 'chunk ') + ', '.join(str(i) for i in misschunks)
                print bcolors.BOLD + bcolors.WARNING + "[WN] %s missing %d/%d files ! Resubmitting %s..."%(directory,len(misschunks),len(outfilelist),chunktext) + bcolors.ENDC
                for chunk in misschunks:
                  infiles = infilelists[chunk]
                  createJobs(jobslog,infiles,outdir,directory,chunk,channel,year=year,tes=tes,ltf=ltf,jtf=jtf)
            
            # RESUBMIT
            nChunks = len(badchunks)+len(misschunks)
            if nChunks==0:
                print bcolors.BOLD + bcolors.OKBLUE + '[OK] ' + directory + bcolors.ENDC
            elif args.force:
                submitJobs(jobName,jobList,nChunks,outdir,batchSystem)
            else:
              submit = raw_input("Do you also want to submit %d jobs to the batch system? [y/n] "%(nChunks))
              if submit.lower()=='force':
                submit = 'y'
                args.force = True
              if submit.lower()=='quit':
                exit(0)
              if submit.lower()=='y':
                submitJobs(jobName,jobList,nChunks,outdir,batchSystem)
              else:
                print "Not submitting jobs"
            print
      
    
#    if flag:
#        print bcolors.FAIL + "[NG]" + directory + bcolors.ENDC
#        print '\t', len(files), ' out of ', str(total) + ' files are corrupted ... skip this sample (consider to resubmit the job)'
#
#    else:
#        print bcolors.BOLD + bcolors.OKBLUE + '[OK] ' + directory + bcolors.ENDC


if __name__ == '__main__':
    print
    main()
