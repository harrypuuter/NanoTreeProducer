#! /usr/bin/env python
# Authors: Yuta Takahashi & Izaak Neutelings (2018)
import os, glob, sys, shlex, re
#import time
from fnmatch import fnmatch
import subprocess
from argparse import ArgumentParser
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TFile, TTree, TH1, Double

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    description = '''Check if the job output files are valid, compare the number of events to DAS (-d), hadd them into one file per sample (-m), and merge datasets (-a).'''
    parser = ArgumentParser(prog="checkFiles",description=description,epilog="Good luck!")
    parser.add_argument('-y', '--year',     dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                            help="select year" )
    parser.add_argument('-c', '--channel',  dest='channels', choices=['mutau','eletau','tautau','mumu','elemu'], nargs='+', default=['tautau'], action='store' )
    parser.add_argument('-m', '--make',     dest='make', default=False, action='store_true',
                                            help="hadd all output files" )
    parser.add_argument('-a', '--hadd',     dest='haddother', default=False, action='store_true',
                                            help="hadd some samples into one (e.g. all data sets, or the extensions)" )
    parser.add_argument('-d', '--das',      dest='compareToDas', default=False, action='store_true',
                                            help="compare number of events in output to das" )
    parser.add_argument('-D', '--das-ex',   dest='compareToDasExisting', default=False, action='store_true',
                                            help="compare number of events in existing output to das" )
    parser.add_argument('-C', '--check-ex', dest='checkExisting', default=False, action='store_true',
                                            help="check existing output (e.g. 'LHE_Njets')" )
    parser.add_argument('-f', '--force',    dest='force', default=False, action='store_true',
                                            help="overwrite existing hadd'ed files" )
    parser.add_argument('-r', '--clean',    dest='cleanup', default=False, action='store_true',
                                            help="remove all output files after hadd" )
    parser.add_argument('-R', '--rm-bad',   dest='removeBadFiles', default=False, action='store_true',
                                            help="remove files that are bad (zombies, no tree, no cutflow, ...)" )
    parser.add_argument(      '--rm-bug',   dest='removeBuggedFiles', default=False, action='store_true',
                                            help="remove files that have bad LHE_Njets" )
    parser.add_argument('-o', '--outdir',   dest='outdir', type=str, default=None, action='store' )
    parser.add_argument('-s', '--sample',   dest='samples', nargs='+', default=[ ], type=str, action='store',
                                            help="samples to run over, glob patterns (wildcards * and ?) are allowed." )
    parser.add_argument('-x', '--veto',     dest='vetos', nargs='+', default=[ ], type=str, action='store',
                                            help="exclude/veto this sample" )
    parser.add_argument('-t', '--type',     dest='type', choices=['data','mc'], type=str, default=None, action='store',
                                            help="filter data or MC to submit" )
    parser.add_argument('-l', '--tag',      dest='intag', type=str, default="", action='store',
                                            help="add a tag to the output file" )
    parser.add_argument(      '--outtag',   dest='outtag', type=str, default="", action='store',
                                            help="add a tag to the output file" )
    parser.add_argument('-T', '--tes',      dest='tes', type=float, default=1.0, action='store',
                                            help="tau energy scale" )
    parser.add_argument('-L', '--ltf',      dest='ltf', type=float, default=1.0, action='store',
                                            help="lepton to tau fake energy scale" )
    parser.add_argument('-J', '--jtf',      dest='jtf', type=float, default=1.0, action='store',
                                            help="jet to tau fake energy scale" )
    parser.add_argument('-M', '--Zmass',    dest='Zmass', action='store_true', default=False,
                                            help="use Z mass window for dimuon spectrum" )
    parser.add_argument('-v', '--verbose',  dest='verbose', default=False, action='store_true',
                                            help="set verbose" )
    args = parser.parse_args()
else:
  args = None

subdirs = [ 'TT', 'DY', 'W*J', 'ST', 'LQ', 'Tau', 'SingleMuon', 'SingleElectron' ]
sample_dict = [
   ('DY',             "DYJetsToLL_M-10to50",              "DYJetsToLL_M-10to50_Tune*madgraph*pythia8"                ),
   ('DY',             "DYJetsToLL_M-10to50_nlo",          "DYJetsToLL_M-10to50_Tune*amcatnlo*pythia8"                ),
   ('DY',             "DYJetsToLL_M-50_ext",              "DYJetsToLL_M-50_Tune*madgraph*pythia8/*ext1"              ), # ext before reg !
   #('DY',             "DYJetsToLL_M-50",                  "DYJetsToLL_M-50_Tune*madgraph*pythia8/RunIIAutumn18"      ), # ext before reg !
   ('DY',             "DYJetsToLL_M-50_reg",              "DYJetsToLL_M-50_Tune*madgraph*pythia8"                    ),
   ('DY',             "DY1JetsToLL_M-50_ext",             "DY1JetsToLL_M-50_Tune*madgraph*pythia8/RunIIFall17*ext1"  ),
   ('DY',             "DY1JetsToLL_M-50_reg",             "DY1JetsToLL_M-50_Tune*madgraph*pythia8/RunIIFall17"       ),
   ('DY',             "DY2JetsToLL_M-50_ext",             "DY2JetsToLL_M-50*/RunIIFall17*ext1"                       ), # ext before reg !
   ('DY',             "DY2JetsToLL_M-50_reg",             "DY2JetsToLL_M-50*/RunIIFall17"                            ),
   ('DY',             "DY3JetsToLL_M-50_ext",             "DY3JetsToLL_M-50*/RunIIFall17*ext1"                       ), # ext before reg !
   ('DY',             "DY3JetsToLL_M-50_reg",             "DY3JetsToLL_M-50*/RunIIFall17"                            ),
   ('DY',             "DY1JetsToLL_M-50",                 "DY1JetsToLL_M-50_Tune*madgraph*pythia8"                   ),
   ('DY',             "DY2JetsToLL_M-50",                 "DY2JetsToLL_M-50_Tune*madgraph*pythia8"                   ),
   ('DY',             "DY3JetsToLL_M-50",                 "DY3JetsToLL_M-50_Tune*madgraph*pythia8"                   ),
   ('DY',             "DY4JetsToLL_M-50",                 "DY4JetsToLL_M-50_Tune*madgraph*pythia8"                   ),
   ('WJ',             "WJetsToLNu_ext",                   "WJetsToLNu_Tune*madgraph*pythia8/*ext1"                   ), # ext before reg !
   ('WJ',             "WJetsToLNu_ext",                   "WJetsToLNu_Tune*madgraph*pythia8/*ext2"                   ), # ext before reg !
   ('WJ',             "WJetsToLNu_reg",                   "WJetsToLNu_Tune*madgraph*pythia8/RunIISummer16"           ),
   ('WJ',             "WJetsToLNu_reg",                   "WJetsToLNu_Tune*madgraph*pythia8/RunIIFall17"             ),
   ('WJ',             "WJetsToLNu",                       "WJetsToLNu_Tune*madgraph*pythia8"                         ),
   ('WJ',             "W2JetsToLNu_ext",                  "W2JetsToLNu_Tune*madgraph*pythia8/RunIISummer16*ext"      ), # ext before reg !
   ('WJ',             "W2JetsToLNu_reg",                  "W2JetsToLNu_Tune*madgraph*pythia8/RunIISummer16"          ),
   ('WJ',             "W3JetsToLNu_ext",                  "W3JetsToLNu_Tune*madgraph*pythia8/RunIISummer16*ext"      ), # ext before reg !
   ('WJ',             "W3JetsToLNu_reg",                  "W3JetsToLNu_Tune*madgraph*pythia8/RunIISummer16"          ),
   ('WJ',             "W4JetsToLNu_ext1",                 "W4JetsToLNu_Tune*madgraph*pythia8/RunIISummer16*ext1"     ), # ext before reg !
   ('WJ',             "W4JetsToLNu_ext2",                 "W4JetsToLNu_Tune*madgraph*pythia8/RunIISummer16*ext2"     ), # ext before reg !
   ('WJ',             "W4JetsToLNu_reg",                  "W4JetsToLNu_Tune*madgraph*pythia8/RunIISummer16"          ),
   ('WJ',             "W1JetsToLNu",                      "W1JetsToLNu_Tune*madgraph*pythia8"                        ),
   ('WJ',             "W2JetsToLNu",                      "W2JetsToLNu_Tune*madgraph*pythia8"                        ),
   ('WJ',             "W3JetsToLNu",                      "W3JetsToLNu_Tune*madgraph*pythia8"                        ),
   ('WJ',             "W4JetsToLNu",                      "W4JetsToLNu_Tune*madgraph*pythia8"                        ),
   ('ST',             "ST_t-channel_antitop",             "ST_t-channel_antitop_4f_inclusiveDecays"                  ),
   ('ST',             "ST_t-channel_top",                 "ST_t-channel_top_4f_inclusiveDecays"                      ),
   ('ST',             "ST_t-channel_top",                 "ST_t-channel_top_5f_TuneCP5"                              ),
   ('ST',             "ST_t-channel_antitop",             "ST_t-channel_antitop_4f_InclusiveDecays"                  ),
   ('ST',             "ST_t-channel_top",                 "ST_t-channel_top_4f_InclusiveDecays"                      ),
   ('ST',             "ST_tW_antitop",                    "ST_tW_antitop_5f_inclusiveDecays"                         ),
   ('ST',             "ST_tW_top",                        "ST_tW_top_5f_inclusiveDecays"                             ),
   ('ST',             "ST_s-channel",                     "ST_s-channel_4f_hadronicDecays"                           ),
   #('TT',             "TT_ext",                           "TT_Tune*powheg*pythia8/*ext"                              ),
   ('TT',             "TT",                               "TT_Tune*powheg*pythia8"                                   ),
   ('TT',             "TTTo2L2Nu",                        "TTTo2L2Nu"                                                ),
   ('TT',             "TTToHadronic",                     "TTToHadronic"                                             ),
   ('TT',             "TTToSemiLeptonic",                 "TTToSemiLeptonic"                                         ),
   ('VV',             "WWTo1L1Nu2Q",                      "WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8"           ),
   ('VV',             "WWTo2L2Nu",                        "WWTo2L2Nu_NNPDF31_TuneCP5_PSweights_13TeV-powheg-pythia8" ),
   ('VV',             "WWToLNuQQ_ext",                    "WWToLNuQQ_NNPDF31_TuneCP5_13TeV-powheg-pythia8/*ext"      ), # ext before reg !
   ('VV',             "WWToLNuQQ_reg",                    "WWToLNuQQ_NNPDF31_TuneCP5_13TeV-powheg-pythia8"           ),
   ('VV',             "WW",                               "WW_Tune*pythia8"                                          ),
   ('VV',             "WZ",                               "WZ_Tune*pythia8"                                          ),
   ('VV',             "ZZ",                               "ZZ_Tune*pythia8"                                          ),
   ('Tau',            "Tau_$RUN",                         "Tau/$RUN"                                                 ),
   ('Tau',            "Tau_Run2017B",                     "Tau/ytakahas-NanoTest_20180507_B"                         ),
   ('Tau',            "Tau_Run2017C",                     "Tau/ytakahas-NanoTest_20180507_C"                         ),
   ('Tau',            "Tau_Run2017D",                     "Tau/ytakahas-NanoTest_20180507_D"                         ),
   ('Tau',            "Tau_Run2017E",                     "Tau/ytakahas-NanoTest_20180507_E"                         ),
   ('Tau',            "Tau_Run2017F",                     "Tau/ytakahas-NanoTest_20180507_F"                         ),
   ('Tau',            "Tau_$RUN",                         "Tau/manzoni-$RUN"                                         ),
   ('SingleMuon',     "SingleMuon_$RUN",                  "SingleMuon/$RUN"                                          ),
   ('SingleMuon',     "SingleMuon_$RUN",                  "SingleMuon/manzoni-$RUN"                                  ),
   ('SingleElectron', "SingleElectron_$RUN",              "SingleElectron/$RUN"                                      ),
   ('SingleElectron', "SingleElectron_Run2017B",          "SingleElectron/ytakahas-Nano_SingleElectron_20180507_B"   ),
   ('SingleElectron', "SingleElectron_Run2017C",          "SingleElectron/ytakahas-Nano_SingleElectron_20180507_C"   ),
   ('SingleElectron', "SingleElectron_Run2017D",          "SingleElectron/ytakahas-Nano_SingleElectron_20180507_D"   ),
   ('SingleElectron', "SingleElectron_Run2017E",          "SingleElectron/ytakahas-Nano_SingleElectron_20180507_E"   ),
   ('SingleElectron', "SingleElectron_Run2017F",          "SingleElectron/ytakahas-Nano_SingleElectron_20180507_F"   ),
   ('MuTauEmb',       "Embedding_MuTau_$RUN",             "Embedding$RUN"                                            ),
   ('EGamma',         "EGamma_$RUN",                      "EGamma/$RUN"                                              ),
   ('LQ',             "SLQ_pair_M$MASS",                  "LegacyRun2_*_LQ_Pair_5f_Madgraph_LO_M$MASS"               ),
   ('LQ',             "SLQ_single_M$MASS",                "LegacyRun2_*_LQ_Single_5f_Madgraph_LO_M$MASS"             ),
   ('LQ',             "SLQ_nonres_M$MASS",                "LegacyRun2_*_LQ_NonRes_5f_Madgraph_LO_M$MASS"             ),
   ('LQ',             "VLQ_nonres_M$MASS",                "LegacyRun2_*_LQ_VecNonRes_5f_Madgraph_LO_M$MASS"          ),
   ('LQ',             "VLQ_pair_M$MASS",                  "PairVectorLQ_InclusiveDecay_M-$MASS"                      ),
   ('LQ',             "VLQ_single_M$MASS",                "SingleVectorLQ_InclusiveDecay_M-$MASS"                    ),
   ('LQ',             "LQ3ToTauB_t-channel_M$MASS",       "LQ3ToTauB_Fall2017_5f_Madgraph_LO_t-channel-M$MASS"       ),
   ('LQ',             "LQ3ToTauB_s-channel_M$MASS",       "LQ3ToTauB_Fall2017_5f_Madgraph_LO_s-channel-M$MASS"       ),
   ('LQ',             "LQ3ToTauB_pair_M$MASS",            "LQ3ToTauB_Fall2017_5f_Madgraph_LO_pair-M$MASS"            ),
   ('LQ',             "VectorLQ3ToTauB_s-channel_M$MASS", "VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_s_channel_M$MASS" ),
   ('LQ',             "VectorLQ3ToTauB_pair_M$MASS",      "VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M$MASS"      ),
   ('VBF',            "VBFHToTauTau_M$MASS",              "VBFHToTauTau_M$MASS"                                      ),
]
sample_dict = [(d,s,p.replace('*','.*').replace('$MASS','(\d+)').replace('$RUN','(Run201\d[A-H])')) for d,s,p in sample_dict] # convert to regex pattern
#sample_dict = { k: v.lstrip('/').replace('/','__') for k, v in sample_dict.iteritems() }
haddsets = [
  ('DY',             "DYJetsToLL_M-50",      [ 'DYJetsToLL_M-50_*'    ], [2016,2017]),
  ('DY',             "DY1JetsToLL_M-50",     [ 'DY1JetsToLL_M-50_*'   ], [2017]),
  ('DY',             "DY2JetsToLL_M-50",     [ 'DY2JetsToLL_M-50_*'   ], [2017]),
  ('DY',             "DY3JetsToLL_M-50",     [ 'DY3JetsToLL_M-50_*'   ], [2017]),
  ('WJ',             "WJetsToLNu",           [ 'WJetsToLNu_*'         ], ),
  ('WJ',             "W2JetsToLNu",          [ 'W2JetsToLNu_*'        ], [2016]),
  ('WJ',             "W3JetsToLNu",          [ 'W3JetsToLNu_*'        ], [2016]),
  ('WJ',             "W4JetsToLNu",          [ 'W4JetsToLNu_*'        ], [2016]),
  ('Tau',            "Tau_$RUN",             [ 'Tau_$RUN?'            ], ),
  ('SingleMuon',     "SingleMuon_$RUN",      [ 'SingleMuon_$RUN?'     ], ),
  ('SingleElectron', "SingleElectron_$RUN",  [ 'SingleElectron_$RUN?' ], [2016,2017]),
  ('EGamma',         "EGamma_$RUN",          [ 'EGamma_$RUN?'         ], [2018]),
]



def main(args):
  #from checkJobs import getSubmittedJobs
  
  years      = args.years
  channels   = args.channels
  intag      = args.intag
  outtag     = args.outtag
  tes        = args.tes
  ltf        = args.ltf
  jtf        = args.jtf
  Zmass      = args.Zmass
  #submitted  = getSubmittedJobs()
  
  if outtag and '_' not in outtag[0]: outtag = '_'+outtag
  if tes!=1.: intag += "_TES%.3f"%(tes)
  if ltf!=1.: intag += "_LTF%.3f"%(ltf)
  if jtf!=1.: intag += "_JTF%.3f"%(jtf)
  if Zmass:   intag += "_Zmass"
  intag  = intag.replace('.','p')
  outtag = intag+outtag
  
  for year in years:
    indir      = "output_%s/"%(year)
    samplesdir = args.outdir if args.outdir else "/scratch/ineuteli/analysis/LQ_%s"%(year)
    os.chdir(indir)
    
    # CHECK EXISTING
    if args.checkExisting:
      for channel in channels:
        infiles  = "%s/*/*_%s.root"%(channel)
        filelist = glob.glob(infiles)
        pattern  = infiles.split('/')[-1]
        for file in filelist:
          if not isValidSample(pattern): continue
          checkFiles(file,pattern,tag=intag)
      continue
    
    # GET LIST
    samplelist = [ ]
    for directory in sorted(os.listdir('./')):
      if not os.path.isdir(directory): continue
      if not isValidSample(directory): continue
      samplelist.append(directory)
    if not samplelist:
      print "No samples found in %s!"%(indir)
    if args.verbose:
      print 'samplelist = %s\n'%(samplelist)
    
    # CHECK samples
    for channel in channels:
      print header(year,channel,intag)
      
      # HADD samples
      if not args.haddother or args.make:
        for directory in samplelist:
            if args.verbose:
              print directory
            
            subdir, samplename = getSampleShortName(directory)
            outdir  = "%s/%s"%(samplesdir,subdir)
            outfile = "%s/%s_%s%s.root"%(outdir,samplename,channel,outtag)
            infiles = '%s/*_%s%s.root'%(directory,channel,intag)
            
            if args.verbose:
              print "directory = %s"%(directory)
              print "outdir    = %s"%(outdir)
              print "outfile   = %s"%(outfile)
              print "infiles   = %s"%(infiles)
            
            #if directory.find('W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8__ytakahas-NanoTest_20180507_W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8-a7a5b67d3e3590e4899e147be08660be__USER')==-1: continue
            filelist = sorted(glob.glob(infiles),key=naturalSort)
            if not filelist: continue
            #running = [f for f in filelist if any(j.outfile in f for j in submitted)]
            
            if checkFiles(filelist,directory,clean=args.removeBadFiles,force=args.force,cleanBug=args.removeBuggedFiles,tag=intag):
              print bcolors.BOLD + bcolors.OKGREEN + '[OK] ' + directory + ' ... can be hadded ' + bcolors.ENDC
            
            if not any(s in directory for s in ['LQ3','LQ_']):
              if args.compareToDas:
                compareEventsToDAS(filelist,directory)
              if args.compareToDasExisting and os.path.isfile(outfile):
                print '   check existing file %s:'%(outfile)
                compareEventsToDAS(outfile,directory)
              #else:
              #  print bcolors.BOLD + bcolors.OKBLUE + '   [OK] ' + directory + bcolors.ENDC
              #print
            
            # HADD
            if args.make:
                ensureDirectory(outdir)
                if os.path.isfile(outfile):
                  if args.force:
                    print bcolors.BOLD + bcolors.WARNING + "   [WN] target %s already exists! Overwriting..."%(outfile) + bcolors.ENDC
                  else:
                    print bcolors.BOLD + bcolors.FAIL + "   [NG] target %s already exists! Use --force or -f to overwrite."%(outfile) + bcolors.ENDC
                    continue
                
                haddcmd = 'hadd -f %s %s'%(outfile,infiles)
                print haddcmd
                os.system(haddcmd)
                
                if not any(s in directory for s in ['LQ3','LQ_']):
                  compareEventsToDAS(outfile,directory)
                #    skimcmd = 'python extractTrees.py -c %s -f %s'%(channel,outfile)
                #    rmcmd = 'rm %s'%(infiles)
                #    #os.system(skimcmd)
                #    #os.system(rmcmd)
                #    continue
                
                #skimcmd = 'python extractTrees.py -c %s -f %s'%(channel,outfile)
                #os.system(skimcmd)
                
                # CLEAN UP
                if args.cleanup:
                  rmcmd = 'rm %s; rm %s/logs/*_%s_%s%s*'%(infiles,directory,channel,year,intag)
                  print bcolors.BOLD + bcolors.OKBLUE + "   removing %d output files..."%(len(infiles)) + bcolors.ENDC
                  if args.verbose:
                    print rmcmd
                  os.system(rmcmd)
                print
      
      # HADD other
      if args.haddother:
        for haddset in haddsets:
            subdir, samplename, sampleset = haddset[:3]
            haddyear = haddset[4] if len(haddset)>=4 else [ ]
            if args.verbose:
              print subdir, samplename, sampleset
            if args.samples and not matchSampleToPattern(samplename,args.samples): continue
            if args.vetos and matchSampleToPattern(directory,args.vetos): continue
            if 'SingleMuon' in subdir and channel not in ['mutau','mumu','elemu']: continue
            if ('SingleElectron' in subdir or 'EGamma' in subdir) and channel!='eletau': continue
            if 'Tau' in subdir and channel!='tautau': continue
            if 'LQ3' in subdir and channel not in ['mutau','tautau','eletau']: continue
            if '2017' in samplename and year!=2017: continue
            if '2018' in samplename and year!=2018: continue
            if haddyear and year not in haddyear: continue
            if '$RUN' in samplename:
              samplename = samplename.replace('$RUN','Run%d'%year)
              sampleset  = [s.replace('$RUN','Run%d'%year) for s in sampleset]
            
            outdir  = "%s/%s"%(samplesdir,subdir)
            outfile = "%s/%s_%s%s.root"%(outdir,samplename,channel,outtag)
            infiles = ['%s/%s_%s%s.root'%(outdir,s,channel,outtag) for s in sampleset] #.replace('ele','e')
            ensureDirectory(outdir)
            
            # OVERWRITE ?
            if os.path.isfile(outfile):
              if args.force:
                pass
                #if args.verbose:
                #  print bcolors.BOLD + bcolors.WARNING + "[WN] target %s already exists! Overwriting..."%(outfile) + bcolors.ENDC
              else:
                print bcolors.BOLD + bcolors.FAIL + "[NG] target %s already exists! Use --force or -f to overwrite."%(outfile) + bcolors.ENDC
                continue
            
            # CHECK FILES
            allinfiles = [ ]
            for infile in infiles[:]:
              if '*' in infile or '?' in infile:
                files = glob.glob(infile)
                allinfiles += files
                if not files:
                  print bcolors.BOLD + bcolors.FAIL + '[NG] no match for the glob pattern %s! Removing pattern from hadd list for "%s"...'%(infile,samplename) + bcolors.ENDC
                  infiles.remove(infile)
              elif not os.path.isfile(infile):
                print bcolors.BOLD + bcolors.FAIL + '[NG] infile %s does not exists! Removing from hadd list for "%s"...'%(infile,samplename) + bcolors.ENDC
                infiles.remove(infile)
              else:
                allinfiles.append(infile)
            
            # HADD
            if args.verbose:
              print "infiles =", infiles
              print "allfiles =", allinfiles
            if len(allinfiles)==1:
              print bcolors.BOLD + bcolors.WARNING + "[WN] found only one file (%s) to hadd to %s!"%(allinfiles[0],outfile) + bcolors.ENDC 
            elif len(allinfiles)>1:
              print bcolors.BOLD + bcolors.OKGREEN + '[OK] hadding %s' %(outfile) + bcolors.ENDC
              haddcmd = 'hadd -f %s %s'%(outfile,' '.join(infiles))
              print haddcmd
              os.system(haddcmd)
            else:
              print bcolors.BOLD + bcolors.WARNING + "[WN] no files to hadd!" + bcolors.ENDC
            print
    
    os.chdir('..')
     


def isValidSample(pattern):
  if args.samples and not matchSampleToPattern(pattern,args.samples): return False
  if args.vetos and matchSampleToPattern(pattern,args.vetos): return False
  if args.type=='mc' and any(s in pattern[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): return False
  if args.type=='data' and not any(s in pattern[:len(s)+2] for s in ['SingleMuon','SingleElectron','Tau','EGamma']): return False
  return True


def checkFiles(filelist,directory,clean=False,force=False,cleanBug=False,treename='tree',tag=""):
    """Check if the file is valid."""
    if args.verbose:
      print "checkFiles: %s, %s"%(filelist,directory)
    if isinstance(filelist,str):
      filelist = [filelist]
    badfiles = [ ]
    bugfiles = [ ]
    ifound   = [ ]
    nfiles   = len(filelist)
    #total_processed = 0
    indexpattern = re.compile(r".*_(\d+)_[a-z]+%s\.root"%tag) #(?:_[A-Z]+\dp\d+)?(?:_Zmass)?
    for filename in filelist:
      match = indexpattern.search(filename)
      if match: ifound.append(int(match.group(1)))
      file  = TFile.Open(filename, 'READ')
      isbad = False
      if file==None:
        print bcolors.FAIL + '[NG] file %s is None'%(filename) + bcolors.ENDC
        badfiles.append(filename)
        continue
      elif file.IsZombie():
        print bcolors.FAIL + '[NG] file %s is a zombie'%(filename) + bcolors.ENDC
        badfiles.append(filename)
      else:
        tree = file.Get(treename)
        if not isinstance(tree,TTree):
          print bcolors.FAIL + '[NG] no tree found in ' + filename + bcolors.ENDC
          badfiles.append(filename)
        elif not isinstance(file.Get('cutflow'),TH1):
          print bcolors.FAIL + '[NG] no cutflow found in ' + filename + bcolors.ENDC
          badfiles.append(filename)
        elif any(s in filename for s in ['DYJets','WJets']) and tree.GetMaximum('LHE_Njets')>10:
          print bcolors.BOLD + bcolors.WARNING + '[WN] %d/%d events have LHE_Njets = %d > 10 in %s'%(tree.GetEntries(),tree.GetEntries("LHE_Njets>10"),tree.GetMaximum('LHE_Njets'),filename) + bcolors.ENDC
          bugfiles.append(filename)
        #if isinstance(tree,TTree):
        #  total_processed += tree.GetEntries()
      file.Close()
    
    if len(badfiles)>0:
      print bcolors.BOLD + bcolors.FAIL + "[NG] %s:   %d out of %d files %s no tree or cutflow!"%(directory,len(badfiles),len(filelist),"have" if len(badfiles)>1 else "has") + bcolors.ENDC
    
    for cleanlist, cleanflag in [(badfiles,clean),(bugfiles,cleanBug)]:
      if len(cleanlist)>0 and cleanflag:
        if force:
          print bcolors.WARNING + '  [WN] removing bad files:'
          for filename in cleanlist:
            print "    %s"%filename
          print bcolors.ENDC
          for filename in cleanlist:
            os.system("rm %s"%filename)
            filelist.remove(filename)
        else:
          print "\n  Bad files:"
          for filename in cleanlist:
            print "    %s"%filename
          remove = raw_input("  Do you really want to remove these? [y/n] ")
          if remove.lower()=='force':
            remove = 'y'
            force = True
          if remove.lower()=='quit':
            exit(0)
          if remove.lower()=='y':
            for filename in cleanlist:
              print "removing %s..."%filename
              os.system("rm %s"%filename)
              filelist.remove(filename)
          print
    
    # TODO: check all chunks (those>imax)
    if ifound:
      imax = max(ifound)+1
      if nfiles<imax:
        imiss = [ i for i in range(0,max(ifound)) if i not in ifound ]
        chunktext = ('chunks ' if len(imiss)>1 else 'chunk ') + ', '.join(str(i) for i in imiss)
        print bcolors.BOLD + bcolors.WARNING + "[WN] %s missing %d/%d files (%s) ?"%(directory,len(imiss),nfiles,chunktext) + bcolors.ENDC
        return False
    else:
      print bcolors.BOLD + bcolors.WARNING + "[WN] %s did not find any valid chunk pattern in file list ?"%(directory) + bcolors.ENDC
    
    return len(badfiles)==0
    
def compareEventsToDAS(inputarg,dasname,histname='cutflow',treename=""):
    """Compare a number of processed events in an output file to the available number of events in DAS."""
    dasname = dasname.replace('__', '/')
    if dasname[0]!='/': dasname = '/'+dasname
    if args.verbose:
      print "compareEventsToDAS: %s, %s"%(inputarg,dasname)
      #start = time.time()
    
    # COUNT EVENTS
    nfiles = ""
    total_processed = 0
    if isinstance(inputarg,list) or isinstance(inputarg,str):
      filenames = inputarg
      if isinstance(filenames,str):
        filenames = [filenames]
      nfiles = len(filenames)
      for filename in filenames:
          file = TFile.Open(filename, 'READ')
          events_processed = 0
          if file==None:
            continue
          elif file.IsZombie():
            file.Close()
            continue
          elif treename:
            tree = file.Get(treename)
            if tree: events_processed = tree.GetEntries()
          else:
            hist = file.Get(histname)
            if hist: events_processed = hist.GetBinContent(1)
          if args.verbose:
            print "%12d events processed in %s "%(events_processed,filename)
          total_processed += events_processed
          file.Close()
      nfiles = ", %d files"%(nfiles) if nfiles>1 else ""
    elif isinstance(inputarg,long) or isinstance(inputarg,int) or isinstance(inputarg,float):
      total_processed = inputarg
    else:
      print bcolors.BOLD + bcolors.FAIL + '   [NG] Did recognize input for "%s": %s'%(dasname,inputarg) + bcolors.ENDC
    
    instance = 'prod/phys03' if 'USER' in dasname else 'prod/global'
    dascmd   = 'das_client --limit=0 --query=\"summary dataset=%s instance=%s\"'%(dasname,instance)
    if args.verbose:
      print dascmd
    dasargs  = shlex.split(dascmd)
    output, error = subprocess.Popen(dasargs, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
    
    if not "nevents" in output:
        print bcolors.BOLD + bcolors.FAIL + '   [NG] Did not find nevents for "%s" in DAS. Return message:'%(dasname) + bcolors.ENDC 
        print bcolors.FAIL + '     ' + output + bcolors.ENDC
        return False
    total_das = Double(output.split('"nevents":')[1].split(',')[0])
    fraction = total_processed/total_das
    
    if fraction > 1.001:
        print bcolors.BOLD + bcolors.FAIL + '   [NG] DAS entries = %d, Processed in tree = %d (frac = %.2f > 1%s)'%(total_das,total_processed,fraction,nfiles) + bcolors.ENDC
    elif fraction > 0.8:
        print bcolors.BOLD + bcolors.OKBLUE + '   [OK] DAS entries = %d, Processed in tree = %d (frac = %.2f%s)'%(total_das,total_processed,fraction,nfiles) + bcolors.ENDC
    else:
        print bcolors.BOLD + bcolors.FAIL + '   [NG] DAS entries = %d, Processed in tree = %d (frac = %.2f < 0.8%s)'%(total_das,total_processed,fraction,nfiles) + bcolors.ENDC
    return True
    
def getSampleShortName(dasname):
  """Get short subdir and sample name from sample_dict."""
  #if '__nanoaod' in dasname.lower():
  #  dasname = dasname[:dasname.lower().index('__nanoaod')]
  #if '__user' in dasname.lower():
  #  dasname = dasname[:dasname.lower().index('__user')]
  if args.verbose:
    print "getSampleShortName: %s"%(dasname)
  dasname = dasname.replace('__','/').lstrip('/')
  for subdir, samplename, pattern in sample_dict:
    matches = re.findall(pattern,dasname)
    if matches:
      samplename = samplename.replace('$MASS',matches[0]).replace('$RUN',matches[0])
      if args.verbose:
         print "getSampleShortName: MATCH! subdir=%s, samplename=%s, pattern=%s"%(subdir, samplename, pattern)
      return subdir, samplename
  print bcolors.BOLD + bcolors.WARNING + '[WN] getSampleShortName: did not find subdir and short sample name for "%s"! Will save in subdir \'unknown\''%(dasname) + bcolors.ENDC 
  return "unknown", dasname.replace('/','__')
  
def getSubdir(dir):
  for subdir in subdirs:
    if '*' in subdir or '?' in subdir:
      if fnmatch(dir,subdir):
        return subdir
    else:
      if subdir==dir[:len(subdir)]:
        return subdir
  return "unknown"
  
def matchSampleToPattern(sample,patterns):
  """Match sample name to some pattern."""
  sample = sample.lstrip('/')
  if not isinstance(patterns,list):
    patterns = [patterns]
  for pattern in patterns:
    if '*' in pattern or '?' in pattern:
      if fnmatch(sample,pattern+'*'):
        return True
    else:
      if pattern in sample[:len(pattern)+1]:
        return True
  return False
  
def ensureDirectory(dirname):
  """Make directory if it does not exist."""
  if not os.path.exists(dirname):
    os.makedirs(dirname)
    print '>>> made directory "%s"'%(dirname)
    if not os.path.exists(dirname):
      print '>>> failed to make directory "%s"'%(dirname)
  return dirname
  
headeri = 0
def header(*strings):
  global headeri
  title  = ', '.join([str(s).lstrip('_') for s in strings if s])
  string = ("\n\n" if headeri>0 else "") +\
           "   ###%s\n"    % ('#'*(len(title)+3)) +\
           "   #  %s  #\n" % (title) +\
           "   ###%s\n"    % ('#'*(len(title)+3))
  headeri += 1
  return string
    
def naturalSort(string):
  """Key for sorting strings according to numerical order.""" 
  return [ int(s) if s.isdigit() else s for s in re.split(r'(\d+)',string) ]
  


if __name__ == '__main__':
    
    print
    main(args)
    print
    


