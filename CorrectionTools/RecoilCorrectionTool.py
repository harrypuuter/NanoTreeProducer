#! /bin/usr/env python
# Author: Izaak Neutelings (November 2018)
# https://twiki.cern.ch/twiki/bin/view/CMS/MSSMAHTauTauEarlyRun2#Top_quark_pT_reweighting
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting#MC_SFs_Reweighting
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from ScaleFactorTool import ensureTFile
from ROOT import TLorentzVector
from math import sqrt, exp

path = 'CorrectionTools/Zpt/'

class RecoilCorrectionTool:
    
    def __init__( self, year=2017 ):
        """Load Z pT weights."""
        
        assert(year in [2016,2017,2018]), "You must choose a year from: 2016, 2017, or 2018."        
        
        #if year==2016:
        #  self.file = ensureTFile( path+'Zpt_weights_2017_Izaak.root', 'READ')
        #elif year==2017:
        #  self.file = ensureTFile( path+'Zpt_weights_2017_Izaak.root', 'READ')
        #else:
        #  self.file = ensureTFile( path+'Zpt_weights_2017_Izaak.root', 'READ')
        #self.file = self.file.Get('zptmass_weights')
        #self.hist.SetDirectory(0)
        #self.file.Close()
    
    def getZptWeight(self,Zpt,Zmass):
        """Get Z pT weight for a given Z boson pT and mass."""
        #weight = self.hist.GetBinContent(self.hist.GetXaxis().FindBin(Zpt),self.hist.GetXaxis().FindBin(Zmass))
        #print ">>> Warning! RecoilCorrectionTool::getZptWeight: Could not make pileup weight for npu=%s data=%s, mc=%s"%(npu,data,mc)
        #return weight
        return 1.
    
    def getTTptWeight(self,toppt1,toppt2):
        """Get top pT weight."""
        #sqrt(exp(0.156-0.00137*min(toppt1,400.0))*exp(0.156-0.00137*min(toppt2,400.0)))
        return sqrt(exp(0.0615-0.0005*min(toppt1,400.0))*exp(0.0615-0.0005*min(toppt2,400.0)))
        

def getZPTMass(event):
    """Calculate Z boson pT and mass."""
    #print '-'*80
    genparticles = Collection(event,'GenPart')
    zboson = TLorentzVector()
    for id in range(event.nGenPart):
      particle = genparticles[id]
      PID      = abs(particle.pdgId)
      #if PID==23 and particle.status==62:
      #  print "%3d: PID=%3d, mass=%3.1f, pt=%3.1f, status=%2d"%(id,particle.pdgId,particle.mass,particle.pt,particle.status)
      if ((PID==11 or PID==13) and particle.status==1 and hasBit(particle.statusFlags,9)) or\
                     (PID==15  and particle.status==2 and hasBit(particle.statusFlags,9)):
        zboson += particle.p4()
        #print "%3d: PID=%3d, mass=%3.1f, pt=%3.1f, status=%2d, statusFlags=%2d (%16s), fromHardProcess=%2d"%(id,particle.pdgId,particle.mass,particle.pt,particle.status,particle.statusFlags,bin(particle.statusFlags),hasBit(particle.statusFlags,9))
    #print "tlv: mass=%3.1f, pt=%3.1f"%(zboson.M(),zboson.Pt())
    return zboson
    

def getTTPTMass(event):
    """Calculate top pT."""
    #print '-'*80
    genparticles = Collection(event,'GenPart')
    toppt1 = -1
    toppt2 = -1
    for id in range(event.nGenPart):
      particle = genparticles[id]
      PID      = abs(particle.pdgId)
      if PID==6 and particle.status==62:
        #print "%3d: PID=%3d, mass=%3.1f, pt=%3.1f, status=%2d"%(id,particle.pdgId,particle.mass,particle.pt,particle.status)
        if particle.pt>toppt1:
          if toppt1==-1:
            toppt1 = particle.pt
          else:
            toppt2 = toppt1
            toppt1 = particle.pt
        else:
          toppt2 = particle.pt
    return toppt1, toppt2
    

def hasBit(value,bit):
  #return bin(value)[-bit]=='1'
  #return format(value,'b').zfill(bit)[-bit]=='1'
  return (value & (1 << (bit-1)))>0
  
