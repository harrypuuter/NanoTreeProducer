#! /usr/bin/env python
# Author: Izaak Neutelings (May 2019)
# Inspiration:
#   https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples
from postprocessors import modulepath
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from modules.ModuleExample import ExampleAnalysis

outdir    = "."
maxEvts   = int(1e3)
postfix   = '_skimmed'
presel    = None #"Muon_pt[0] > 50 && Jet_pt[0] > 50"
branchsel = "%s/keep_and_drop_jets.txt"%modulepath
infiles   = [
  ###'%s/samples/DY1JetsToLL_M-50_2017.root'%modulepath,
  ###'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/8C0C1B20-DFC2-2B49-AD49-3BDD07650DD6.root',  #   10908
  ###'root://xrootd-cms.infn.it//store/data/Run2017F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/5C980020-7798-7B4D-B7B5-54EAA473D79A.root', #   89470
  ###'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/90000/946BE003-BA74-554C-81C4-98F9B4D41772.root',  #   83977
  'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/1C5D9C07-B3BA-254E-832D-89AD21C9F258.root', #  109916
  'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/01CBA228-11A8-7848-8710-DF8CFEA1454E.root', #  169467
]

print ">>> %-10s = %s"%('outdir',outdir)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('postfix',postfix)
print ">>> %-10s = %s"%('branchsel',branchsel)
print ">>> %-10s = %s"%('infiles',infiles)

p = PostProcessor(outdir, infiles, presel, branchsel, noOut=False, modules=[ ], provenance=False, postfix=postfix, maxEntries=maxEvts)
p.run()
