#! /usr/bin/env python
# Authors: Yuta Takahashi & Izaak Neutelings (2018)
import os, glob, sys, shlex, re
#import time
from fnmatch import fnmatch
import subprocess
from argparse import ArgumentParser
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TFile, TTree, TH1, Double
import checkFiles
from checkFiles import bcolors, header, ensureDirectory, getSubdir, matchSampleToPattern, naturalSort, compareEventsToDAS
from submit import getFileListLocal, getFileListDAS

if __name__ == '__main__':
    description = '''Check if the job output files are valid, compare the number of events to DAS (-d), hadd them into one file per sample (-m), and merge datasets (-a).'''
    parser = ArgumentParser(prog="checkFiles",description=description,epilog="Good luck!")
    parser.add_argument('-y', '--year',     dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                            help="select year" )
    parser.add_argument('-d', '--das',      dest='compareToDas', default=False, action='store_true',
                                            help="compare number of events in output to das" )
    parser.add_argument('-R', '--rm-bad',   dest='removeBadFiles', default=False, action='store_true',
                                            help="remove files that are bad (zombies, no tree, no cutflow, ...)" )
    parser.add_argument(      '--rm-bug',   dest='removeBuggedFiles', default=False, action='store_true',
                                            help="remove files that have bad LHE_Njets" )
    parser.add_argument('-L', '--local',    dest='useLocal', action='store_true', default=False,
                                            help="get file list from local list" )
    parser.add_argument('-o', '--outdir',   dest='outdir', type=str, default=None, action='store' )
    parser.add_argument('-s', '--sample',   dest='samples', type=str, nargs='+', default=[ ], action='store',
                                            help="samples to run over, glob patterns (wildcards * and ?) are allowed." )
    parser.add_argument('-x', '--veto',     dest='veto', action='store', type=str, default=None,
                                            help="veto this sample" )
    parser.add_argument('-t', '--type',     dest='type', choices=['data','mc'], type=str, default=None, action='store',
                                            help="filter data or MC to submit" )
    parser.add_argument('-l', '--tag',      dest='tag', type=str, default="", action='store',
                                            help="add a tag to the output file" )
    parser.add_argument('-v', '--verbose',  dest='verbose', default=False, action='store_true',
                                            help="set verbose" )
    args = parser.parse_args()
    checkFiles.args = args
else:
  args = None
  


def main(args):
  
  years      = args.years
  tag        = args.tag
  director   = "root://t3dcachedb.psi.ch:1094/" #"root://xrootd-cms.infn.it/"
  
  for year in years:
    samplesdir = args.outdir if args.outdir else "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_%s"%(year)
    
    # GET LIST
    samplelist = [ ]
    for directory in sorted(os.listdir(samplesdir)):
      directory = "%s/%s"%(samplesdir,
      directory)
      if not os.path.isdir(directory): continue
      samplelist.append(directory)
    if not samplelist:
      print "No samples found in %s!"%(samplesdir)
    if args.verbose:
      print 'samplelist = %s\n'%(samplelist)
    
    # CHECK samples
    print header(year,tag)    
    for directory in samplelist:
        
        sample   = directory.split('/')[-1]
        filelist = '%s/*_skim%s*.root'%(directory,tag)
        if args.verbose:
          print "directory  = %s"%(directory)
          print "filelist   = %s"%(filelist)
          print "sample     = %s"%(sample)
        
        # FILE LIST ON SE
        filelist = [director+d for d in sorted(glob.glob(filelist),key=naturalSort)]
        if not filelist: continue
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
          if '/pnfs/' in directory:
            print bcolors.BOLD + bcolors.WARNING + "Warning! Ignoring file on pnfs, " + directory + bcolors.ENDC
            continue
          else:
            infilelist = getFileListDAS(sample)
        if not infilelist:
          print bcolors.BOLD + bcolors.WARNING + "Warning! EMPTY filelist for " + directory + bcolors.ENDC
        elif args.verbose:
          print "infilelist = %s"%(infilelist[0])
          for file in infilelist[1:]:
            print "             "+file
        
        #if checkFiles(filelist,directory,clean=args.removeBadFiles,force=args.force,cleanBug=args.removeBuggedFiles):
        #  print bcolors.BOLD + bcolors.OKGREEN + '[OK] ' + directory + ' ... can be hadded ' + bcolors.ENDC
        
        if not any(s in directory for s in ['LQ3','LQ_']):
          if args.compareToDas:
            compareEventsToDAS(filelist,sample,treename='Events')        
    

def checkFiles():
    """Check files."""
    


if __name__ == '__main__':
    print
    main(args)
    print
    

