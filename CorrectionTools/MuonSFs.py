from ScaleFactorTool import ScaleFactor, ScaleFactorHTT

# /shome/ytakahas/work/Leptoquark/CMSSW_9_4_4/src/PhysicsTools/NanoAODTools/NanoTreeProducer/leptonSF
# HTT: https://github.com/CMS-HTT/LeptonEfficiencies
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
# https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Efficiency_Scale_Factors
path    = 'CorrectionTools/leptonEfficiencies/'
pathHTT = 'CorrectionTools/leptonEfficiencies/HTT/Muon/'

class MuonSFs:
    
    def __init__(self, year=2017):
        """Load histograms from files."""
        
        assert(year in [2016,2017,2018]), "You must choose a year from: 2016, 2017, or 2018."
        
        if year==2016:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2016BtoH/Muon_IdIso_IsoLt0p15_2016BtoH_eff.root",'ZMass','mu_trig')
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2016BtoH/Muon_Mu22OR_eta2p1_eff.root",'ZMass','mu_idiso')
        else:
          self.sftool_trig  = ScaleFactor(path+"EfficienciesAndSF_RunBtoF_Nov17Nov2017.root","IsoMu27_PtEtaBins/abseta_pt_ratio",'mu_trig')
          #self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2017/Muon_IsoMu24orIsoMu27.root",'ZMass','mu_idiso')
          #self.sftool_id    = ScaleFactor(path+"RunBCDEF_SF_ID.root","NUM_MediumID_DEN_genTracks",'mu_id')
          #self.sftool_iso   = ScaleFactor(path+"RunBCDEF_SF_ISO.root","NUM_TightRelIso_DEN_MediumID",'mu_iso')
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2017/Muon_IdIso_IsoLt0p15_eff_RerecoFall17.root",'ZMass','mu_idiso')
          
    def getTriggerSF(self, pt, eta):
        """Get SF for single muon trigger."""
        return self.sftool_trig.getSF(pt,abs(eta))
        
    def getIdIsoSF(self, pt, eta):
        """Get SF for muon identification + isolation."""
        return self.sftool_idiso.getSF(pt,eta)
    
