# Author: Izaak Neutelings (May 2019)
from ROOT import TFile, TTree
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
from corrections.JetMETCorrectionTool import JetMETCorrectionTool



class TreeProducerSimpleJME(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, isData=False):
        
        print 'TreeProducerSimple is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        
        self.addBranch('event',  int  )
        self.addBranch('njets',  float)
        self.addBranch('jpt_1',  float)
        self.addBranch('jeta_1', float)
        self.addBranch('jphi_1', float)
        self.addBranch('jpt_2',  float)
        self.addBranch('jeta_2', float)
        self.addBranch('jphi_2', float)
        self.addBranch('met',    float)
        self.addBranch('metphi', float)
        
        if not isData:
          jetuncs = [ 'jer', 'jes']
          metuncs = [ 'jer', 'jes', 'unclEn']
          for unc in jetuncs:
            for var in ['Up','Down']:
              self.addBranch('jpt_1_%s'%(unc+var),  float)
              self.addBranch('jpt_2_%s'%(unc+var),  float)
          for unc in metuncs:
            for var in ['Up','Down']:
              self.addBranch('met_%s'%(unc+var),    float)
    


class SimpleJMEProducer(Module):
    """Simple module to test postprocessing with JME modules added."""
    
    def __init__(self, name, **kwargs):
        
        self.name    = name
        self.year    = kwargs.get('year',     2017 )
        self.isData  = kwargs.get('dataType', 'mc' )=='data'
        self.out     = TreeProducerSimpleJME(name,isData=self.isData)
        self.jmeTool = JetMETCorrectionTool(self.year,jet='AK4PFchs',met='MET',updateEvent=True,data=self.isData,era='C')
        
        if self.isData:
          self.jetuncs = [ ]
          self.metuncs = [ ]
        else:
          self.jetuncs = ['jer', 'jes']
          self.metuncs = ['jer', 'jes', 'unclEn']
        
    def beginJob(self):
        pass
        
    def endJob(self):
        self.jmeTool.endJob()
        self.out.endJob()
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def analyze(self, event):
        """Process event, return True (go to next module) or False (fail, go to next event)."""
        
        self.out.event = event.event & 0xffffffffffffffff
        
        if self.isData:
          jetpt_corr, met_corr = self.jmeTool.correctJetMET(event)
          jetpt_vars, met_vars = { 'nom': jetpt_corr }, { 'nom': met_corr }
        else:
          jetpt_vars, met_vars = self.jmeTool.correctJetMET(event)
          jetpt_corr, met_corr = jetpt_vars['nom'], met_vars['nom']
        #print jetpt_vars
        
        #### LOOP over JETS
        ###jetIds = [ ]
        ###jets = Collection(event,'Jet')
        ###for ijet in range(event.nJet):
        ###    if event.Jet_pt[ijet] < 30: continue
        ###    if abs(event.Jet_eta[ijet]) > 4.7: continue
        ###    jetIds.append(ijet)
        
        # FILL BRANCHES JETS
        self.out.njets[0]    = event.nJet
        
        if event.nJet>0:
          self.out.jpt_1[0]  = jetpt_corr[0]
          self.out.jeta_1[0] = event.Jet_eta[0]
          self.out.jphi_1[0] = event.Jet_phi[0]
          for unc in self.jetuncs:
            for var in ['Up','Down']:
              getattr(self.out,"jpt_1_%s"%(unc+var))[0] = jetpt_vars[unc+var][0]
        else:
          self.out.jpt_1[0]  = -1.
          self.out.jeta_1[0] = -9.
          self.out.jphi_1[0] = -9.
        
        if event.nJet>1:
          self.out.jpt_2[0]  = jetpt_corr[1]
          self.out.jeta_2[0] = event.Jet_eta[1]
          self.out.jphi_2[0] = event.Jet_phi[1]
          for unc in self.jetuncs:
            for var in ['Up','Down']:
              getattr(self.out,"jpt_2_%s"%(unc+var))[0] = jetpt_vars[unc+var][1]
        else:
          self.out.jpt_2[0]  = -1.
          self.out.jeta_2[0] = -9.
          self.out.jphi_2[0] = -9.
        
        self.out.met[0]    = met_corr.Pt()
        self.out.metphi[0] = met_corr.Phi()
        for unc in self.metuncs:
          for var in ['Up','Down']:
            getattr(self.out,"met_%s"%(unc+var))[0]    = met_vars[unc+var].Pt()
        
        self.out.tree.Fill()
        return True
        
