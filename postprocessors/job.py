#! /usr/bin/env python
# Authors: Yuta Takahashi & Izaak Neutelings (2018)
# Description: This postprocessor is meant for actual processing of samples for analysis
import sys
from postprocessors import modulepath, ensureDirectory
from postprocessors.config_jme import getEra
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from argparse import ArgumentParser
from postprocessors import ensureDirectory

infiles = "root://cms-xrd-global.cern.ch//store/user/arizzi/Nano01Fall17/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAOD-94X-Nano01Fall17/180205_160029/0000/test94X_NANO_70.root"

parser = ArgumentParser()
parser.add_argument('-i', '--infiles',  dest='infiles',   action='store', type=str, default=infiles)
parser.add_argument('-o', '--outdir',   dest='outdir',    action='store', type=str, default="output")
parser.add_argument('-N', '--outfile',  dest='outfile',   action='store', type=str, default="noname")
parser.add_argument('-l', '--tag',      dest='tag',       action='store', type=str, default="")
parser.add_argument('-n', '--nchunck',  dest='nchunck',   action='store', type=int, default='test')
parser.add_argument('-p', '--prefetch', dest='prefetch',  action='store_true', default=False)
parser.add_argument('-c', '--channel',  dest='channel',   action='store', choices=['tautau','mutau','eletau','mumu','elemu'], type=str, default='tautau')
parser.add_argument('-t', '--type',     dest='type',      action='store', choices=['data','mc'], default=None)
parser.add_argument('-y', '--year',     dest='year',      action='store', choices=[2016,2017,2018], type=int, default=2017)
parser.add_argument('-e', '--era',      dest='era',       action='store', type=str, default="")
parser.add_argument('-T', '--tes',      dest='tes',       action='store', type=float, default=1.0)
parser.add_argument('-L', '--ltf',      dest='ltf',       action='store', type=float, default=1.0)
parser.add_argument('-J', '--jtf',      dest='jtf',       action='store', type=float, default=1.0)
parser.add_argument('-M', '--Zmass',    dest='Zmass',     action='store_true',  default=False)
parser.add_argument(      '--no-jec',   dest='doJEC',     action='store_false', default=True)
parser.add_argument(      '--jec-sys',  dest='doJECSys',  action='store_true',  default=None)
args = parser.parse_args()

outdir        = ensureDirectory(args.outdir)
outfile       = args.outfile
nchunck       = args.nchunck
prefetch      = args.prefetch #and False # copy file to a local temporary directory
channel       = args.channel
year          = args.year
era           = args.era
dataType      = args.type
infiles       = args.infiles
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

if dataType==None:
  dataType = 'mc'
if 'SingleMuon' in infiles[0] or "/Tau/" in infiles[0] or 'SingleElectron' in infiles[0] or 'EGamma' in infiles[0]:
  dataType = 'data'

json = None
if dataType=='data':
  if era=="" and infiles:
    kwargs['era'] = getEra(infiles[0],year)
  jsonpath = '/work/ineuteli/analysis/LQ_legacy/NanoTreeProducer/json/'
  if year==2016:
    json = jsonpath+'Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
  elif year==2017:
    json = jsonpath+'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
  else:
    json = jsonpath+'Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
    #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'

tag = args.tag
#if args.tes!=1: tag +="_TES%.3f"%(args.tes)
#if args.ltf!=1: tag +="_LTF%.3f"%(args.ltf)
#if args.jtf!=1: tag +="_JTF%.3f"%(args.jtf)
#if args.Zmass:  tag +="_Zmass"
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
    exit(0)

print "job.py: creating PostProcessor..."
sys.stdout.flush()
p = PostProcessor(outdir, infiles, None, noOut=True, modules=[module2run()], jsonInput=json, postfix=postfix, prefetch=prefetch)
print "job.py: running PostProcessor..."
p.run()
print "job.py: Postprocessor is done"
