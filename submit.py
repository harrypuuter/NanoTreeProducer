#! /usr/bin/env python
# Authors: Yuta Takahashi & Izaak Neutelings (2018)
import os, re, glob
from commands import getoutput
from fnmatch import fnmatch
import itertools
from argparse import ArgumentParser
import checkFiles
from checkFiles import getSampleShortName, matchSampleToPattern, header, ensureDirectory

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument('-f', '--force',     dest='force', action='store_true', default=False,
                                           help="submit jobs without asking confirmation" )
  parser.add_argument('-y', '--year',      dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                           help="select year" )
  parser.add_argument('-c', '--channel',   dest='channels', choices=['eletau','mutau','tautau','mumu','elemu'], type=str, nargs='+', default=['mutau'], action='store',
                                           help="channels to submit" )
  parser.add_argument('-s', '--sample',    dest='samples', type=str, nargs='+', default=[ ], action='store',
                                           help="filter these samples, glob patterns (wildcards * and ?) are allowed." )
  parser.add_argument('-x', '--veto',      dest='vetoes', nargs='+', default=[ ], action='store',
                                           help="exclude/veto this sample" )
  parser.add_argument('-t', '--type',      dest='type', choices=['data','mc','emb'], type=str, default=None, action='store',
                                           help="filter data or MC to submit" )
  parser.add_argument('-l', '--tag',       dest='tag', type=str, default="", action='store',
                                           help="extra tag for output files" )
  parser.add_argument('-T', '--tes',       dest='tes', type=float, default=1.0, action='store',
                                           help="tau energy scale" )
  parser.add_argument('-L', '--ltf',       dest='ltf', type=float, default=1.0, action='store',
                                           help="lepton to tau fake energy scale" )
  parser.add_argument('-J', '--jtf',       dest='jtf', type=float, default=1.0, action='store',
                                           help="jet to tau fake energy scale" )
  parser.add_argument('-M', '--Zmass',     dest='Zmass', action='store_true', default=False,
                                           help="use Z mass window for dimuon spectrum" )
  parser.add_argument('-d', '--das',       dest='useDAS', action='store_true', default=False,
                                           help="get file list from DAS" )
  parser.add_argument('-S', '--use-skim',  dest='useSkim', action='store_true', default=False,
                                           help="use skimmed samples, if available" )
  parser.add_argument('-n', '--njob',      dest='nFilesPerJob', action='store', type=int, default=-1,
                                           help="number of files per job" )
  parser.add_argument('-q', '--queue',     dest='queue', choices=['all.q','short.q','long.q'], type=str, default=None, action='store',
                                           help="select queue for submission" )
  parser.add_argument('-m', '--mock',      dest='mock', action='store_true', default=False,
                                           help="mock-submit jobs for debugging purposes" )
  parser.add_argument('-p', '--prefetch',  dest='prefetch', action='store_true', default=False,
                                           help="copy nanoAOD files to a temporary directory before run on it" )
  parser.add_argument(      '--test',      dest='testrun', action='store_true', default=False,
                                           help="submit only one job per sample as a test run" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
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
nFilesPerJob_default  = 8 #4
nFilesPerJob_defaults = [
  #( 1, ['DY',"W*J",'WW','WZ','ZZ','ST','TT_',"TTTo2L2Nu","TTToSemiLep*RunIIFall17",'Single','Tau','EGamma','VBF']),
  #( 2, ['*VectorLQ_']),
  (40, ['LQ3','*_LQ_']),
]


def checkExistingFiles(outdir,channel,njob):
    filelist = glob.glob("%s/*%s.root"%(outdir,channel))
    nfiles = len(filelist)
    if nfiles>njob:
      print bcolors.BOLD + bcolors.WARNING + "Warning! There already exist %d files, while the requested number of files per job is %d"%(nfiles,njob) + bcolors.ENDC
      remove = raw_input("Do you want to remove the extra files? [y/n] ")
      if remove.lower()=='y':
        for filename in sorted(filelist):
          matches = re.findall(r"_(\d+)_%s.root"%(channel),filename)
          if matches and int(matches[0])>njob:
            print "Removing %s..."%(filename)
            os.remove(filename)
      else:
        print "Not removing extra files. Please make sure to delete the %d last files before hadd'ing."%(nfiles-njob)
    

def chunkify(iterable, size):
    it     = iter(iterable)
    item   = list(itertools.islice(it,size))
    chunks = [ ]
    while item:
      chunks.append(item)
      item = list(itertools.islice(it,size))
    return chunks
    

def getBlackList(filename):
    """Get blacklist of files from local directory."""
    #filename = "filelist/blacklist_%s.txt"%dataset.lstrip('/').replace('/','__')
    blacklist = [ ]
    if os.path.exists(filename):
      with open(filename,'r') as file:
        for line in file:
          line = line.rstrip('\n')
          if line and '#' not in line:
            blacklist.append(line)
    return blacklist
    

def saveFileListLocal(dataset,filelist,blacklist=[ ],tag=""):
    """Save a list of files to a local directory."""
    if '/pnfs/' in dataset:
      tag += "_pnfs"
    dataset  = '__'.join(dataset.split('/')[-3:])
    filename = "filelist/filelist_%s%s.txt"%(dataset.replace('/','__'),tag)
    with open(filename,'w+') as file:
      for line in filelist:
        if line not in blacklist:
          file.write(line+'\n')
    return filename
    

def getFileListLocal(dataset,blacklist=[ ],tag=""):
    """Get list of files from local directory."""
    if '/pnfs/' in dataset:
      tag += "_pnfs"
    dataset  = '__'.join(dataset.split('/')[-3:])
    filename = "filelist/filelist_%s%s.txt"%(dataset.lstrip('/').replace('/','__'),tag)
    filelist = [ ]
    if os.path.exists(filename):
      with open(filename,'r') as file:
        for line in file:
          line = line.rstrip('\n')
          if line and '#' not in line and line not in blacklist:
            filelist.append(line.rstrip('\n'))
    return filelist
    

def getFileList(dataset,blacklist=[ ]):
    """Get list of files from DAS."""
    if '/pnfs/' in dataset:
      return getFileListPNFS(dataset,blacklist=blacklist)
    elif any(s in dataset for s in ['LQ3','LegacyRun2']):
      if any(s in dataset for s in ['LegacyRun2_2018_LQ_Pair','LegacyRun2_2018_LQ_Single']):
        pnfspath = '/pnfs/psi.ch/cms/trivcat/store/user/rdelburg/'
      else:
        pnfspath = '/pnfs/psi.ch/cms/trivcat/store/user/ytakahas/'
      return getFileListPNFS(pnfspath+dataset)
    return getFileListDAS(dataset,blacklist=blacklist)
    

def getFileListDAS(dataset,blacklist=[ ]):
    """Get list of files from DAS."""
    dataset   = dataset.replace('__','/')
    if dataset[0]!='/':
      dataset = '/'+dataset
    instance  = 'prod/global'
    if 'USER' in dataset:
        instance = 'prod/phys03'
    #cmd='das_client --limit=0 --query="file dataset=%s instance=%s"'%(dataset,instance)
    cmd = 'das_client --limit=0 --query="file dataset=%s instance=%s status=*"'%(dataset,instance)
    if args.verbose:
      print "Executing ",cmd
    cmd_out  = getoutput( cmd )
    tmpList  = cmd_out.split(os.linesep)
    filelist = [ ]
    for line in tmpList:
      if '.root' in line and line not in blacklist:
        #files.append("root://cms-xrd-global.cern.ch/"+line) # global
        filelist.append("root://xrootd-cms.infn.it/"+line) # Eurasia
    filelist.sort()
    return filelist 
    

def getFileListPNFS(dataset,blacklist=[ ]):
    """Get list of files from PSI T3's SE."""
    dataset  = dataset.replace('__','/')
    tmpList  = glob.glob(dataset+'/*.root')
    director = "dcap://t3se01.psi.ch:22125/"
    filelist = [ ]
    for file in tmpList:
      if '.root' in file and file not in blacklist:
        filelist.append(director+file.rstrip())
    if "SingleMuon/Run2018C-Nano14Dec2018-v1/NANOAOD" in dataset: # temporary solution
      file = director+"/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/SingleMuon/Run2018C-Nano14Dec2018-v1/NANOAOD/DA99EFB9-860F-F648-8D46-5AD80205F53B_skimmed.root"
      if file in filelist:
        print bcolors.BOLD + bcolors.WARNING + "FOUND %s !"%file + bcolors.ENDC
      else:
        print bcolors.BOLD + bcolors.WARNING + "ADDED %s !"%file + bcolors.ENDC
        filelist.append(file)
    filelist.sort()
    return filelist
    

def isSkimmed(sample,year):
    """Find skimmed path, if it exists."""
    skimmedpath = "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples"
    skimmedpath = "%s/NANOAOD_%s/%s"%(skimmedpath,year,sample.lstrip('/').replace('__','/'))
    if os.path.exists(skimmedpath):
      return skimmedpath
    return False


def createJobs(jobsfile, infiles, outdir, name, nchunks, channel, year, **kwargs):
    """Create file with commands to execute per job."""
    tag      = kwargs.get('tag',      "") # TODO: add
    tes      = kwargs.get('tes',      1.)
    ltf      = kwargs.get('ltf',      1.)
    jtf      = kwargs.get('jtf',      1.)
    Zmass    = kwargs.get('Zmass',    False)
    prefetch = kwargs.get('prefetch', False)
    cmd = 'python postprocessors/job.py -i %s -o %s -N %s -n %i -c %s -y %s'%(','.join(infiles),outdir,name,nchunks,channel,year)
    if tes!=1.:
      cmd += " --tes %.3f"%(tes)
    if ltf!=1.:
      cmd += " --ltf %.3f"%(ltf)
    if jtf!=1.:
      cmd += " --jtf %.3f"%(jtf)
    if Zmass and channel=='mumu':
      cmd += " --Zmass"
    if prefetch:
      cmd += " -p"
    if tag:
      cmd += " -l %s"%tag
    cmd += " -t %s"%args.type
    if args.verbose:
      print cmd
    jobsfile.write(cmd+'\n')
    return 1
    

def submitJobs(jobName, jobList, nchunks, outdir, batchscript):
    """Submit job."""
    if args.verbose:
      print 'Reading joblist...'
      print jobList
    extraopts = "-t 1-%s -N %s -o %s/logs/"%(nchunks,jobName,outdir)
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
    
    channels    = args.channels
    years       = args.years
    tes         = args.tes
    ltf         = args.ltf
    jtf         = args.jtf
    Zmass       = args.Zmass
    prefetch    = args.prefetch
    batchscript = 'submit_SGE.sh'
    tag         = args.tag
    
    if tag and tag[0]!='_': tag = '_'+tag
    if tes!=1.: tag += "_TES%.3f"%(tes)
    if ltf!=1.: tag += "_LTF%.3f"%(ltf)
    if jtf!=1.: tag += "_JTF%.3f"%(jtf)
    if Zmass:   tag += "_Zmass"
    tag = tag.replace('.','p')
    
    for year in years:
      
      # READ SAMPLES
      directories = [ ]
      samplelist  = "samples_%s.cfg"%(year)
      with open(samplelist, 'r') as file:
        for line in file:
          line = line.rstrip().lstrip().split(' ')[0].rstrip('/')
          if line[:2].count('#')>0: continue
          if line=='': continue
          if line.count('/')<2: continue
          sample = '/'.join(line.split('/')[-3:])
          if args.samples and not matchSampleToPattern(sample,args.samples): continue
          if args.vetoes and matchSampleToPattern(sample,args.vetoes): continue
          if args.type=='mc' and any(s in sample[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): continue
          if args.type=='data' and not any(s in sample[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): continue
          directories.append(line)
      if args.testrun:
        directories = directories[:1]
      #print directories
      blacklist = getBlackList("filelist/blacklist.txt")
      
      for channel in channels:
        print header(year,channel,tag)
        
        # SUBMIT SAMPLES
        for directory in directories:
            
            if args.verbose:
              print "\ndirectory =",directory
            
            # FILTER
            if 'SingleMuon' in directory and channel not in ['mutau','mumu','elemu']: continue
            if ('SingleElectron' in directory or 'EGamma' in directory) and channel!='eletau': continue
            if 'Tau' in directory[:5] and channel!='tautau': continue
            if 'LQ3' in directory[:5] and channel not in ['mutau','eletau','tautau']: continue
            
            # GET SKIMMED
            if args.useSkim and isSkimmed(directory,year):
              directory = isSkimmed(directory,year)
              if args.verbose:
                print "skimmed:", directory
            
            print bcolors.BOLD + bcolors.OKGREEN + directory + bcolors.ENDC
            
            # FILE LIST
            files = [ ]
            if not args.useDAS:
                files = getFileListLocal(directory,blacklist=blacklist)
            if not files:
              if not args.useDAS:
                print "Getting file list from DAS/PNFS..."
              files = getFileList(directory,blacklist=blacklist)
              if files:
                saveFileListLocal(directory,files,blacklist=blacklist)
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
            sample       = '__'.join(directory.split('/')[-3:])
            ensureDirectory('joblist')
            jobList      = 'joblist/joblist_%s_%s%s.txt'%(sample,channel,tag)
            print "Creating job file %s..."%(jobList)
            jobName      = getSampleShortName(directory)[1]
            jobName     += "_%s_%s"%(channel,year)+tag
            jobs         = open(jobList,'w')
            outdir       = ensureDirectory("output_%s/%s"%(year,sample))
            ensureDirectory(outdir+'/logs/')
            
            # NFILESPERJOBS
            nFilesPerJob = args.nFilesPerJob
            if nFilesPerJob<1:
              for default, patterns in nFilesPerJob_defaults:
                if matchSampleToPattern(sample,patterns):
                  nFilesPerJob = default
                  break
              else:
                nFilesPerJob = nFilesPerJob_default
            if args.verbose:
              print "nFilesPerJob = %s"%nFilesPerJob
            filelists = chunkify(files,nFilesPerJob)
            
            # CREATE JOBS
            nChunks = 0
            checkExistingFiles(outdir,channel,len(filelists))
            #filelists = chunkify(files,1)
            for file in filelists:
            #print "FILES = ",f
                createJobs(jobs,file,outdir,sample,nChunks,channel,year=year,tes=tes,ltf=ltf,jtf=jtf,Zmass=Zmass,tag=tag,prefetch=prefetch)
                nChunks = nChunks+1
            jobs.close()
            
            # SUBMIT
            if args.force:
              submitJobs(jobName,jobList,nChunks,outdir,batchscript)
            else:
              submit = raw_input("Do you also want to submit %d jobs to the batch system? [y/n] "%(nChunks))
              if submit.lower()=='force':
                submit = 'y'
                args.force = True
              if submit.lower()=='quit':
                exit(0)
              if submit.lower()=='y':
                submitJobs(jobName,jobList,nChunks,outdir,batchscript)
              else:
                print "Not submitting jobs"
            print



if __name__ == "__main__":
    print
    main()
    print "Done\n"
		
		
		
