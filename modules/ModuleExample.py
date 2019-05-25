# Official example:
#  https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/examples/exampleAnalysis.py
import sys
from ROOT import TH1F, TLorentzVector
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon

class ExampleAnalysis(Module):
    
    def __init__(self):
      self.writeHistFile = True
      
    def beginJob(self,histFile=None,histDirName=None):
      #Module.beginJob(self,histFile,histDirName)
      #self.h_vpt = TH1F('sumpt', 'sumpt', 100, 0, 1000)
      #self.addObject(self.h_vpt)
      pass
      
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
      self.out = wrappedOutputTree
      self.out.branch("sumpt", 'F')
      
    def analyze(self, event):
      #print ">>> ExampleAnalysis.analyze"
      electrons = Collection(event, "Electron")
      muons     = Collection(event, "Muon")
      jets      = Collection(event, "Jet")
      eventSum  = TLorentzVector()
      
      
      # select events with at least 2 muons
      if len(muons)>=2:
        for lep in muons:     #loop on muons
          eventSum += lep.p4()
        for lep in electrons : #loop on electrons
          eventSum += lep.p4()
        for j in jets:       #loop on jets
          eventSum += j.p4()
        #self.h_vpt.Fill(eventSum.Pt())     #fill histogram
        self.out.fillBranch("sumpt",eventSum.Pt()) # fill branch
      
      return True
      