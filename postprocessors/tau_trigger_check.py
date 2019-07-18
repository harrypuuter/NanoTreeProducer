#! /usr/bin/env python
# Author: Izaak Neutelings (July 2019)
# Description: Check tau triggers in nanoAOD
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
import os, sys
import numpy as np
from math import sqrt, pi
from postprocessors import modulepath
from postprocessors.tauCorrReduced import TauCorrectionsProducerSimple
from postprocessors.tauCorrProducer import TauCorrectionsProducer
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True


# MODULE
class TauTriggerChecks(Module):
    
    def __init__(self,year=2017,trigger='all',wps=['loose','medium','tight']):
        
        assert year in [2017,2018], "Year should be 2017 or 2018"
        
        # TRIGGERS
        if year==2017:
          self.trigger_etau  = lambda e: e.HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1
          self.trigger_mutau = lambda e: e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
          self.trigger_ditau = lambda e: e.HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg or e.HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
        else:
          self.trigger_etau  = lambda e: e.HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1
          self.trigger_mutau = lambda e: e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1
          self.trigger_ditau = lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
        
        if trigger=='etau':
          self.trigger = self.trigger_etau
        elif trigger=='mutau':
          self.trigger = self.trigger_mutau
        elif trigger=='ditau':
          self.trigger = self.trigger_ditau
        else:
          self.trigger = lambda e: self.trigger_etau(e) or self.trigger_mutau(e) or self.trigger_ditau(e)
        
        # TAU ID WPs and bits
        tauIDWPs      = { wp: 2**i for i, wp in enumerate(['vvloose','vloose','loose','medium','tight','vtight','vvtight']) }
        assert all(w in tauIDWPs for w in wps), "Tau ID WP should be in %s"%tauIDWPs.keys()
        self.tauIDWPs = sorted([(tauIDWPs[w],w) for w in wps])
        ###self.tauID    = lambda tau: tau.idMVAoldDM2017v2>=8
        
        # TRIGGER OBJECT bits
        print ">>> trigger objects:"
        trigObjects = [ "LooseChargedIso", "MediumChargedIso", "TightChargedIso", "TightOOSCPhotons", "Hps", "SelectedPFTau", "DoublePFTau", "OverlapFilterIsoEle", "OverlapFilterIsoMu", "DoublePFTau" ]
        self.trigObjBits = { }
        for i, trigobj in enumerate(trigObjects):
          bit = 2**i
          print ">>> %5d: %s"%(bit,trigobj)
          self.trigObjBits[bit] = trigobj
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        self.out = wrappedOutputTree
        self.out.branch("trigger_etau",  'O')
        self.out.branch("trigger_mutau", 'O')
        self.out.branch("trigger_ditau", 'O')
        for bit, trigobj in sorted(self.trigObjBits.iteritems()):
          self.out.branch("nTau_%s"%trigobj, 'I')
          for wpbit, wp in self.tauIDWPs:
            self.out.branch("nTau_%s_%s"%(trigobj,wp), 'I')
        
    def analyze(self, event):
        """Process event, return True (pass, go to next module) or False (fail, go to next event)."""
        
        # TRIGGER
        if not self.trigger(event):
          return False
        ###print "%s %s passed the trigger %s"%('-'*20,event.event,'-'*40)
        
        # TRIGGER OBJECTS
        nMatches    = { w[0]: { b: 0 for b in self.trigObjBits } for w in self.tauIDWPs+[(0,'all')] }
        trigObjects = [o for o in Collection(event,'TrigObj') if o.id==15] # and o.filterBits in [1,2,3,16]]
        ###for obj in Collection(event,'TrigObj'):
        ###  print obj, obj.id, obj.filterBits, type(obj), type(obj.id), type(obj.filterBits)
        ###for trigobj in trigObjects:
        ###  print trigobj, trigobj.filterBits
        
        # LOOP over TAUS
        taus = Collection(event, 'Tau')
        for tau in taus:
          ###dm = tau.decayMode
          ###if dm not in [0,1,10]: continue
          ###if not self.tauID(tau): continue
          
          # MATCH
          for trigobj in trigObjects:
            if DeltaR(tau,trigobj) < 0.4:
              ###print "Match:",tau,trigobj
              for bit in getBits(trigobj.filterBits):
                assert bit in nMatches[0], "Did not find bit %s (from %s) in nMatches[0] = %s"%(bit,trigobj.filterBits,nMatches['all'])
                nMatches[0][bit] += 1
                for wpbit, wp in self.tauIDWPs:
                  if tau.idMVAoldDM2017v2>=wpbit:
                    nMatches[wpbit][bit] += 1
                  else:
                    break
        
        # FILL BRANCHES
        self.out.fillBranch("trigger_etau",  self.trigger_etau(event))
        self.out.fillBranch("trigger_mutau", self.trigger_mutau(event))
        self.out.fillBranch("trigger_ditau", self.trigger_ditau(event))
        for bit, trigobj in self.trigObjBits.iteritems():
          self.out.fillBranch("nTau_%s"%trigobj,nMatches[0][bit]) #.get(bit,0)
          for wpbit, wp in self.tauIDWPs:
            self.out.fillBranch("nTau_%s_%s"%(trigobj,wp),nMatches[wpbit][bit])
        
        return True
        

def DeltaR(obj1,obj2):
  deta = abs(obj1.eta - obj2.eta)
  dphi = abs(obj1.phi - obj2.phi)
  while dphi > pi:
    dphi = abs(dphi - 2*pi)
  return sqrt(dphi**2+deta**2)
  

def getBits(x):
  """Decompose integer into list of bits (powers of 2)."""
  powers = [ ]
  i = 1
  while i <= x:
    if i & x: powers.append(i)
    i <<= 1
  return powers
  


# POST-PROCESSOR
year      = 2017
trigger   = 'all'
maxEvts   = int(1e4)
nFiles    = 2
postfix   = '_trigger_%s_%s'%(trigger,year)
branchsel = "%s/keep_and_drop_taus.txt"%modulepath
if not os.path.isfile(branchsel): branchsel = None

if year==2017:
  infiles = [
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/67/myNanoProdMc2017_NANO_66.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/68/myNanoProdMc2017_NANO_67.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/69/myNanoProdMc2017_NANO_68.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/70/myNanoProdMc2017_NANO_69.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/71/myNanoProdMc2017_NANO_70.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/72/myNanoProdMc2017_NANO_71.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/73/myNanoProdMc2017_NANO_72.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/74/myNanoProdMc2017_NANO_73.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/75/myNanoProdMc2017_NANO_74.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/76/myNanoProdMc2017_NANO_75.root',
  ]
else:
  infiles = [
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/77/myNanoProdMc2018_NANO_176.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/78/myNanoProdMc2018_NANO_177.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/79/myNanoProdMc2018_NANO_178.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/80/myNanoProdMc2018_NANO_179.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/81/myNanoProdMc2018_NANO_180.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/82/myNanoProdMc2018_NANO_181.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/83/myNanoProdMc2018_NANO_182.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/84/myNanoProdMc2018_NANO_183.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/85/myNanoProdMc2018_NANO_184.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/86/myNanoProdMc2018_NANO_185.root',
  ]
infiles = infiles[:nFiles]

print ">>> %-10s = %s"%('year',year)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('nFiles',nFiles)
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('branchsel',branchsel)

module2run = lambda: TauTriggerChecks(year,trigger)
p = PostProcessor(".", infiles, None, branchsel=branchsel, outputbranchsel=branchsel, noOut=False,
                  modules=[module2run()], provenance=False, postfix=postfix, maxEntries=maxEvts)
p.run()
