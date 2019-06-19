#! /usr/bin/env python
# Author: Izaak Neutelings (May 2019)
# Description: example of a postprocessor with Jet/MET corrections and to test the behavior
#              of own JME tools
# Inspiration:
#   https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples
#   https://gitlab.cern.ch/Zurich_ttH/tthbb13/blob/FHv2/MEAnalysis/python/nano_postproc.py#L34
#   https://gitlab.cern.ch/Zurich_ttH/tthbb13/blob/FHv2/MEAnalysis/python/nano_config.py
import os, sys
from postprocessors import modulepath
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puAutoWeight
#from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertainties2017All
from modules.ModuleSimpleJME import SimpleJMEProducer

year     = 2017
dataType = 'mc'
maxEvts  = int(1e1)
postfix  = 'jme_%s.root'%(year)
if dataType=='data':
  if year==2016:
    infiles = [
      'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/9DC46213-FB51-5347-89A4-4FF02435B663.root', #    3457
      ###'root://xrootd-cms.infn.it//store/data/Run2016F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/705EBC01-6F4A-F943-9834-64387A0D5480.root', #   41623
      ###'root://xrootd-cms.infn.it//store/data/Run2016G/SingleMuon/NANOAOD/Nano14Dec2018-v1/00000/57E51EC1-15B2-AC46-9D69-32C4FAC9E94B.root',  #   14731
    ]
  elif year==2017:
    infiles = [
      'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/8C0C1B20-DFC2-2B49-AD49-3BDD07650DD6.root',  #   10908
      ###'root://xrootd-cms.infn.it//store/data/Run2017F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/5C980020-7798-7B4D-B7B5-54EAA473D79A.root', #   89470
      ###'root://xrootd-cms.infn.it//store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/46665B58-B1DF-4641-9CFB-B72822DDD495.root',  #  439959
    ]
  else:
    infiles = [
      'root://xrootd-cms.infn.it//store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/5FA66B97-0267-B244-8761-3D1BE9F3428F.root', #    6107
      ###'root://xrootd-cms.infn.it//store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/4FC2DBE0-183D-6A49-9E59-55B89D34A722.root', #   61529
      ###'root://xrootd-cms.infn.it//store/data/Run2018A/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/17CF17FF-ACE6-A944-9021-0C0FC9F25F9B.root', #   98698
    ]
else:
  if year==2016:
    infiles = [
      'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/47560595-D7E2-DD4D-989A-39EB01F213FA.root', #  522739
      ###'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/BEF8D775-B527-634D-8049-4CE5F091D665.root', #  760101
    ]
  elif year==2017:
    infiles = [
      #'946BE003-BA74-554C-81C4-98F9B4D41772.root'
      'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/90000/946BE003-BA74-554C-81C4-98F9B4D41772.root',  #   83977
      ###'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/1C5D9C07-B3BA-254E-832D-89AD21C9F258.root', #  109916
    ]
  else:
    infiles = [
      'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/110000/70EC8A67-D08F-1240-97DA-768AEADB5C6B.root', # 1254738
      ###'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/110000/621334D2-E98E-3545-B6D8-053726E86ACE.root', # 1367732
    ]

print ">>> %-10s = %s"%('year',year)
print ">>> %-10s = '%s'"%('dataType',dataType)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = %s"%('infiles',infiles)

module2run = lambda: SimpleJMEProducer(postfix,year=year,dataType=dataType)
p = PostProcessor(".", infiles, None, noOut=True, modules=[module2run()], provenance=False,
                  postfix=postfix, maxEntries=maxEvts)
p.run()
