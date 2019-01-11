#! /usr/bin/env python

import os, glob, sys, shlex, re
from commands import getoutput
from argparse import ArgumentParser
import checkFiles, submit_qsub
from checkFiles import getSampleShortName, matchSampleToPattern
from submit_qsub import args, bcolors, createJobs, getFileListPNFS, getFileListDAS, submitJobs, split_seq
import itertools
import subprocess
from ROOT import TFile, Double



def main():
    
    batchSystem  = 'psibatch_runner.sh'    
    year         = args.year
    channel      = args.channel
    nFilesPerJob = args.nFilesPerJob
    outdir       = "output_%s/"%(year)
    chunkpattern = re.compile(r".*_(\d+)_[a-z]+\.root")
    
    # GET LIST
    samplelist = [ ]
    for directory in sorted(os.listdir(outdir)):
        if not os.path.isdir(outdir+directory): continue
        if args.samples and not matchSampleToPattern(directory,args.samples): continue
        if args.veto and not matchSampleToPattern(directory,args.veto): continue
        samplelist.append(directory)
    if not samplelist:
      print "No samples found in %s!"%(outdir)
    if args.verbose:
      print samplelist
    
    # RESUBMIT samples
    for directory in samplelist:
        #if directory.find('W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8__ytakahas-NanoTest_20180507_W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8-a7a5b67d3e3590e4899e147be08660be__USER')==-1: continue
        outdir = "output_%s/%s"%(year,directory)
        outfilelist = glob.glob(outdir + '/*_' + args.channel + '.root')
        if not outfilelist: continue
        
        # GET INPUT FILES
        if 'LQ' in directory:
          infiles = getFileListPNFS(directory)
        else:
          infiles = getFileListDAS('/' + directory.replace('__', '/'))
        
        # NFILESPERJOBS CHECKS
        if nFilesPerJob>1 and any(vv==jobName for vv in [ 'WW', 'WZ', 'ZZ' ]):
          print bcolors.BOLD + bcolors.WARNING + "Warning: Setting number of files per job from %s to 1 for %s"%(nFilesPerJob,jobName) + bcolors.ENDC
          nFilesPerJob = 1
        
        infilelists = list(split_seq(infiles,nFilesPerJob))
        
        badchunks   = [ ]
        misschunks  = range(0,len(infilelists))
        jobList = 'joblist/joblist%s_%s_retry.txt'%(directory, args.channel)
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
                print bcolors.BOLD + bcolors.FAIL + '[WN] %s: found chunk %s >= total number of chunks %s ! Please make sure you have chosen the correct -n !'%(filename,chunk,len(infilelists)) + bcolors.ENDC
              else:
                print bcolors.BOLD + bcolors.FAIL + '[WN] %s: found weird chunk %s ! Please check if there is overcounting !'%(filename,chunk,len(infilelists)) + bcolors.ENDC
              file = TFile(filename,'READ')
              if not file.IsZombie() and file.GetListOfKeys().Contains('tree') and file.GetListOfKeys().Contains('cutflow'):
                continue
              infiles = infilelists[chunk]
              createJobs(jobslog,infiles,outdir,directory,chunk,channel,year=year)
              badchunks.append(chunk)
          
          # BAD CHUNKS
          if len(badchunks)>0:
            chunktext = ('chunks ' if len(badchunks)>1 else 'chunk ') + ', '.join(str(ch) for ch in badchunks)
            print bcolors.BOLD + bcolors.WARNING + '[NG] %s, %d/%d failed! Resubmitting %s...'%(directory,len(ids),len(outfilelist),chunktext) + bcolors.ENDC
          
          # MISSING CHUNKS
          if len(misschunks)>0:
            chunktext = ('chunks ' if len(misschunks)>1 else 'chunk ') + ', '.join(str(i) for i in misschunks)
            print bcolors.BOLD + bcolors.WARNING + "[WN] %s missing %d/%d files ! Resubmitting %s..."%(directory,len(misschunks),len(outfilelist),chunktext) + bcolors.ENDC
            for chunk in misschunks:
              infiles = infilelists[chunk]
              createJobs(jobslog,infiles,outdir,directory,chunk,channel,year=year)
        
        # RESUBMIT
        jobName = getSampleShortName(directory)[1]
        nchunks = len(badchunks)+len(misschunks)
        if nchunks>0:
            submitJobs(jobName,jobList,nchunks,outdir,batchSystem)
        else:
            print bcolors.BOLD + bcolors.OKBLUE + '[OK] ' + directory + bcolors.ENDC
        
#    if flag:
#        print bcolors.FAIL + "[NG]" + directory + bcolors.ENDC
#        print '\t', len(files), ' out of ', str(total) + ' files are corrupted ... skip this sample (consider to resubmit the job)'
#
#    else:
#        print bcolors.BOLD + bcolors.OKBLUE + '[OK] ' + directory + bcolors.ENDC


if __name__ == '__main__':
    print
    main()
