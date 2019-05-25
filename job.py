#! /usr/bin/env python
# Authors: Yuta Takahashi & Izaak Neutelings (2018)
# Description: This postprocessor is meant for actual processing of samples for analysis
import os, sys, re
import PhysicsTools
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from argparse import ArgumentParser
from checkFiles import ensureDirectory

infiles = "root://cms-xrd-global.cern.ch//store/user/arizzi/Nano01Fall17/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAOD-94X-Nano01Fall17/180205_160029/0000/test94X_NANO_70.root"

parser = ArgumentParser()
parser.add_argument('-i', '--infiles', dest='infiles',   action='store', type=str, default=infiles)
parser.add_argument('-o', '--outdir',  dest='outdir',    action='store', type=str, default="outdir")
parser.add_argument('-N', '--outfile', dest='outfile',   action='store', type=str, default="noname")
parser.add_argument('-n', '--nchunck', dest='nchunck',   action='store', type=int, default='test')
parser.add_argument('-c', '--channel', dest='channel',   action='store', choices=['tautau','mutau','eletau','mumu','elemu'], type=str, default='tautau')
parser.add_argument('-t', '--type',    dest='type',      action='store', choices=['data','mc'], default=None)
parser.add_argument('-y', '--year',    dest='year',      action='store', choices=[2016,2017,2018], type=int, default=2017)
parser.add_argument('-e', '--era',     dest='era',       action='store', type=str, default="")
parser.add_argument('-T', '--tes',     dest='tes',       action='store', type=float, default=1.0)
parser.add_argument('-L', '--ltf',     dest='ltf',       action='store', type=float, default=1.0)
parser.add_argument('-J', '--jtf',     dest='jtf',       action='store', type=float, default=1.0)
parser.add_argument('-M', '--Zmass',   dest='Zmass',     action='store_true',  default=False)
parser.add_argument(      '--no-jec',  dest='doJEC',     action='store_false', default=True)
parser.add_argument(      '--jec-sys', dest='doJECSys',  action='store_true',  default=None)
args = parser.parse_args()

channel       = args.channel
year          = args.year
era           = args.era
dataType      = args.type
infiles       = args.infiles
outdir        = args.outdir
outfile       = args.outfile
nchunck       = args.nchunck
args.doJECSys = (args.tes==1 and args.ltf==1 and args.jtf==1) if args.doJECSys==None else args.doJECSys
kwargs        = {
  'year':        args.year,
  'era':         args.era,
  'tes':         args.tes,
  'ltf':         args.ltf,
  'jtf':         args.jtf,
  'doJEC':       args.doJEC,
  'doJECSys':    args.doJECSys,
  'ZmassWindow': args.Zmass,
}

if isinstance(infiles,str):
  infiles = infiles.split(',')

ensureDirectory(outdir)

if dataType==None:
  dataType = 'mc'
if 'SingleMuon' in infiles[0] or "/Tau/" in infiles[0] or 'SingleElectron' in infiles[0] or 'EGamma' in infiles[0]:
  dataType = 'data'

json = None
if dataType=='data':
  JSON = '/shome/ineuteli/analysis/LQ_legacy/NanoTreeProducer/json/'
  if year==2016:
    json = JSON+'Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
  elif year==2017:
    json = JSON+'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
  else:
    json = JSON+'Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'

if dataType=='data' and era=="" and infiles:
  matches = re.findall(r"Run(201[678])([A-Z]+)",infiles[0])
  if not matches:
    print "Warning! Could not find an era in %s"%infiles[0]
  elif year!=int(matches[0][0])
    print "Warning! Given year does not match the data file %s"%infiles[0]
  else:
    era = matches[0][1]
    kwargs['era'] = era

tag = ""
if args.tes!=1: tag +="_TES%.3f"%(args.tes)
if args.ltf!=1: tag +="_LTF%.3f"%(args.ltf)
if args.jtf!=1: tag +="_JTF%.3f"%(args.jtf)
if args.Zmass:  tag +="_Zmass"
outfile = "%s_%s_%s%s.root"%(outfile,nchunck,channel,tag.replace('.','p'))
postfix = "%s/%s"%(outdir,outfile)

print '-'*80
print ">>> %-12s = %s"  %('input files',infiles)
print ">>> %-12s = %s"  %('output directory',outdir)
print ">>> %-12s = %s"  %('output file',outfile)
print ">>> %-12s = %s"  %('chunck',nchunck)
print ">>> %-12s = '%s'"%('channel',channel)
print ">>> %-12s = %s"  %('year',kwargs['year'])
print ">>> %-12s = '%s'"%('era',kwargs['era'])
print ">>> %-12s = '%s'"%('dataType',dataType)
print ">>> %-12s = %s"  %('Zmass',kwargs['Zmass'])
print '-'*80

module2run = None
if channel=='tautau':
    from modules.ModuleTauTau import *
    module2run = lambda: TauTauProducer(postfix, dataType, **kwargs)

elif channel=='mutau':
    from modules.ModuleMuTau import *
    module2run = lambda: MuTauProducer(postfix, dataType, **kwargs)

elif channel=='eletau':
    from modules.ModuleEleTau import *
    module2run = lambda: EleTauProducer(postfix, dataType, **kwargs)

elif channel=='mumu':
    from modules.ModuleMuMu import *
    module2run = lambda: MuMuProducer(postfix, dataType, **kwargs)

elif channel=='elemu':
    from modules.ModuleEleMu import *
    module2run = lambda: EleMuProducer(postfix, dataType)
else:
    print 'Unkown channel !!!'
    sys.exit(0)

print "job.py: creating PostProcessor..."
p = PostProcessor(outdir, infiles, None, noOut=True, modules=[module2run()], provenance=False, fwkJobReport=False,
                  jsonInput=json, postfix=postfix)

print "job.py: going to run PostProcessor..."
p.run()
print "DONE"
