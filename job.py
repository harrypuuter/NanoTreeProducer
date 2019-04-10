#! /usr/bin/env python
import os, sys
import PhysicsTools
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from argparse import ArgumentParser
from checkFiles import ensureDirectory

infiles = "root://cms-xrd-global.cern.ch//store/user/arizzi/Nano01Fall17/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAOD-94X-Nano01Fall17/180205_160029/0000/test94X_NANO_70.root"

parser = ArgumentParser()
parser.add_argument('-i', '--infiles', dest='infiles', action='store', type=str, default=infiles)
parser.add_argument('-o', '--outdir',  dest='outdir', action='store', type=str, default="outdir")
parser.add_argument('-N', '--outfile', dest='outfile', action='store', type=str, default="noname")
parser.add_argument('-n', '--nchunck', dest='nchunck', action='store', type=int, default='test')
parser.add_argument('-c', '--channel', dest='channel', action='store', choices=['tautau','mutau','eletau','mumu','elemu'], type=str, default='tautau')
parser.add_argument('-t', '--type',    dest='type', action='store', choices=['data','mc'], default='mc')
parser.add_argument('-y', '--year',    dest='year', action='store', choices=[2016,2017,2018], type=int, default=2017)
parser.add_argument('-M', '--Zmass',   dest='Zmass', action='store_true', default=False)
parser.add_argument('-T', '--tes',     dest='tes', action='store', type=float, default=1.0)
parser.add_argument('-L', '--ltf',     dest='ltf', action='store', type=float, default=1.0)
parser.add_argument('-J', '--jtf',     dest='jtf', action='store', type=float, default=1.0)
args = parser.parse_args()

channel  = args.channel
dataType = args.type
infiles  = args.infiles
outdir   = args.outdir
outfile  = args.outfile
nchunck  = args.nchunck
year     = args.year
tes      = args.tes
kwargs   = {
  'year':  year,
  'tes':   args.tes,
  'ltf':   args.ltf,
  'jtf':   args.jtf,
  'ZmassWindow': args.Zmass,
}

if isinstance(infiles,str):
  infiles = infiles.split(',')

ensureDirectory(outdir)

dataType = 'mc'
if 'SingleMuon' in infiles[0] or "/Tau/" in infiles[0] or 'SingleElectron' in infiles[0] or 'EGamma' in infiles[0]:
  dataType = 'data'

JSON = '/shome/ineuteli/analysis/LQ_legacy/NanoTreeProducer/json/'
if year==2016:
  json = JSON+'Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
  #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
elif year==2017:
  json = JSON+'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
  #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
else:
  json = JSON+'Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
  #json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'

tag = ""
if args.tes!=1: tag +="_TES%.3f"%(args.tes)
if args.ltf!=1: tag +="_LTF%.3f"%(args.ltf)
if args.jtf!=1: tag +="_JTF%.3f"%(args.jtf)
if args.Zmass:  tag +="_Zmass"
outfile = "%s_%s_%s%s.root"%(outfile,nchunck,channel,tag.replace('.','p'))
postfix = "%s/%s"%(outdir,outfile)

print '-'*80
print "%-12s = %s"%('input files',infiles)
print "%-12s = %s"%('output directory',outdir)
print "%-12s = %s"%('output file',outfile)
print "%-12s = %s"%('chunck',nchunck)
print "%-12s = %s"%('channel',channel)
print "%-12s = %s"%('dataType',dataType)
print "%-12s = %s"%('year',kwargs['year'])
print "%-12s = %s"%('tes',args.tes)
print "%-12s = %s"%('ltf',args.ltf)
print "%-12s = %s"%('jtf',args.jtf)
print "%-12s = %s"%('Zmass',args.Zmass)
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
if dataType=='data':
    p = PostProcessor(outdir, infiles, None, "keep_and_drop.txt", noOut=True, 
                      modules=[module2run()], provenance=False, fwkJobReport=False,
                      jsonInput=json, postfix=postfix)
else:
    p = PostProcessor(outdir, infiles, None, "keep_and_drop.txt", noOut=True,
                      modules=[module2run()], provenance=False, fwkJobReport=False, postfix=postfix)

print "job.py: going to run PostProcessor..."
p.run()
print "DONE"
