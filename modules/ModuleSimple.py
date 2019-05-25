# Author: Izaak Neutelings (May 2019)
from ROOT import TFile, TTree
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon



class TreeProducerSimple(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name):
        
        print 'TreeProducerSimple is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        
        self.addBranch('njets',  float)
        self.addBranch('jpt_1',  float)
        self.addBranch('jeta_1', float)
        self.addBranch('jphi_1', float)
        self.addBranch('jpt_2',  float)
        self.addBranch('jeta_2', float)
        self.addBranch('jphi_2', float)
        
    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()
    


class SimpleProducer(Module):
    """Simple module to test postprocessing."""
    
    def __init__(self, name, **kwargs):
        self.name = name
        self.out  = TreeProducerSimple(name)
    
    def beginJob(self):
        pass
        
    def endJob(self):
        self.out.endJob()
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def analyze(self, event):
        """Process event, return True (go to next module) or False (fail, go to next event)."""
        
        ###idx_goodmuons = [ ]
        ###for imuon in range(event.nMuon):
        ###    if event.Muon_pt[imuon] < self.muonCutPt(event): continue
        ###    if abs(event.Muon_eta[imuon]) > 2.4: continue
        ###    if abs(event.Muon_dz[imuon]) > 0.2: continue
        ###    if abs(event.Muon_dxy[imuon]) > 0.045: continue
        ###    if not event.Muon_mediumId[imuon]: continue
        ###    #if event.Muon_pfRelIso04_all[imuon]>0.50: continue
        ###    idx_goodmuons.append(imuon)
        ###
        ###if len(idx_goodmuons)==0:
        ###    return False
        
        # LOOP over JETS
        jetIds = [ ]
        jets = Collection(event,'Jet')
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 4.7: continue
            jetIds.append(ijet)
        
        # FILL BRANCHES JETS
        self.out.njets[0]         = len(jetIds)
        
        if len(jetIds)>0:
          self.out.jpt_1[0]       = event.Jet_pt[jetIds[0]]
          self.out.jeta_1[0]      = event.Jet_eta[jetIds[0]]
          self.out.jphi_1[0]      = event.Jet_phi[jetIds[0]]
        else:
          self.out.jpt_1[0]       = -1.
          self.out.jeta_1[0]      = -9.
          self.out.jphi_1[0]      = -9.
    
        if len(jetIds)>1:
          self.out.jpt_2[0]       = event.Jet_pt[jetIds[1]]
          self.out.jeta_2[0]      = event.Jet_eta[jetIds[1]]
          self.out.jphi_2[0]      = event.Jet_phi[jetIds[1]]
        else:
          self.out.jpt_2[0]       = -1.
          self.out.jeta_2[0]      = -9.
          self.out.jphi_2[0]      = -9.
        
        self.out.tree.Fill()
        return True
        
