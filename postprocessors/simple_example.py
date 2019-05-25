#! /usr/bin/env python
# Author: Izaak Neutelings (May 2019)
# Inspiration:
#   https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples
from postprocessors import modulepath
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

outdir    = '.'
maxEvts   = int(1e4)
postfix   = 'simple.root'
branchsel = "%s/keep_and_drop_simple.txt"%modulepath
infiles   = [
  '%s/samples/DY1JetsToLL_M-50_2017.root'%modulepath,
  ###'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/8C0C1B20-DFC2-2B49-AD49-3BDD07650DD6.root',  #   10908
  ###'root://xrootd-cms.infn.it//store/data/Run2017F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/5C980020-7798-7B4D-B7B5-54EAA473D79A.root', #   89470
  ###'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/90000/946BE003-BA74-554C-81C4-98F9B4D41772.root',  #   83977
  ###'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/1C5D9C07-B3BA-254E-832D-89AD21C9F258.root', #  109916
  ###'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/01CBA228-11A8-7848-8710-DF8CFEA1454E.root', #  169467
]

print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('postfix',postfix)
print ">>> %-10s = %s"%('infiles',infiles)

from modules.ModuleSimple import SimpleProducer
module2run = lambda: SimpleProducer(postfix)

#p = PostProcessor(outdir,infiles,"Jet_pt>150","keep_and_drop.txt",[exampleModule()],provenance=True)
p = PostProcessor(outdir, infiles, None, branchsel, noOut=True, modules=[module2run()], provenance=False, postfix=postfix, compression=0)
p.run()
