#! /usr/bin/env python
# Author: Izaak Neutelings (May 2019)
# Description: Skim branch list of samples
# Inspiration:
#   https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples
import sys
from postprocessors import modulepath, ensureDirectory
from postprocessors.config_jme import getEra, getJetCalibrationData, getJetCalibrationMC
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puAutoWeight
#from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertainties2016, jetmetUncertainties2017, jetmetUncertainties2018
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from argparse import ArgumentParser

infiles = "root://cms-xrd-global.cern.ch//store/user/arizzi/Nano01Fall17/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAOD-94X-Nano01Fall17/180205_160029/0000/test94X_NANO_70.root"
parser = ArgumentParser()
parser.add_argument('-i', '--infiles',  dest='infiles',   action='store', type=str, default=infiles)
parser.add_argument('-o', '--outdir',   dest='outdir',    action='store', type=str, default="output")
parser.add_argument('-t', '--type',     dest='type',      action='store', choices=['data','mc'], default=None)
parser.add_argument('-y', '--year',     dest='year',      action='store', choices=[2016,2017,2018], type=int, default=2017)
parser.add_argument('-e', '--era',      dest='era',       action='store', type=str, default="")
parser.add_argument('-l', '--tag',      dest='tag',       action='store', type=str, default="")
parser.add_argument('-p', '--prefetch', dest='prefetch',  action='store_true', default=False)
parser.add_argument('-J', '--jec',      dest='doJEC',     action='store_true', default=False)
parser.add_argument(      '--jec-sys',  dest='doJECSys',  action='store_true', default=None)
args = parser.parse_args()

outdir        = ensureDirectory(args.outdir)
postfix       = '_skimmed'+args.tag
presel        = None #"Muon_pt[0] > 50"
branchsel     = "%s/keep_and_drop_skim_diboson.txt"%modulepath
modules       = [ ]
maxEvts       = None #int(1e3)
prefetch      = args.prefetch #and False # copy file to a local temporary directory
year          = args.year
era           = args.era
dataType      = args.type
infiles       = args.infiles

if isinstance(infiles,str):
  infiles = infiles.split(',')

if any(s in infiles[0] for s in ["/Tau/","JetsToL"]):
  branchsel = "%s/keep_and_drop_skim.txt"%modulepath

if dataType==None:
  dataType = 'mc'
if 'SingleMuon' in infiles[0] or "/Tau/" in infiles[0] or 'SingleElectron' in infiles[0] or 'EGamma' in infiles[0]:
  dataType = 'data'

json     = None
doJEC    = args.doJEC #and dataType=='data'
doJECSys = args.doJECSys
if dataType=='data':
  if doJEC:
    if era=="" and infiles:
      era = getEra(infiles[0],year)
    modules.append(getJetCalibrationData(year,era))
  jsonpath = '/work/ineuteli/analysis/LQ_legacy/NanoTreeProducer/json/'
  if year==2016:
    json = jsonpath+'Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
  elif year==2017:
    json = jsonpath+'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
  else:
    json = jsonpath+'Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'

print '-'*80
print ">>> %-12s = %s"  %('input files',infiles)
print ">>> %-12s = '%s'"%('output directory',outdir)
print ">>> %-12s = %s"  %('maxEvts',maxEvts)
print ">>> %-12s = '%s'"%('postfix',postfix)
print ">>> %-12s = %s"  %('year',year)
print ">>> %-12s = '%s'"%('era',era)
print ">>> %-12s = '%s'"%('dataType',dataType)
print ">>> %-12s = '%s'"%('branchsel',branchsel)
print ">>> %-12s = '%s'"%('json',json)
print ">>> %-12s = %s"  %('modules',modules)
print ">>> %-12s = %s"  %('prefetch',prefetch)
print ">>> %-12s = %s"  %('doJEC',doJEC)
print ">>> %-12s = %s"  %('doJECSys',doJECSys)
print '-'*80

print "skim.py: creating PostProcessor..."
sys.stdout.flush()
p = PostProcessor(outdir, infiles, presel, branchsel, outputbranchsel=branchsel, noOut=False,
                  modules=modules, jsonInput=json, postfix=postfix, maxEntries=maxEvts, prefetch=prefetch)
print "skim.py: running PostProcessor..."
p.run()
print "skim.py: Postprocessor is done"
