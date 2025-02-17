# Author: Izaak Neutelings (December 2018)
# /shome/ytakahas/work/Leptoquark/CMSSW_9_4_4/src/PhysicsTools/NanoAODTools/NanoTreeProducer/leptonSF
# HTT: https://github.com/CMS-HTT/LeptonEfficiencies
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
from corrections import modulepath
from ScaleFactorTool import ScaleFactor, ScaleFactorHTT
pathPOG = modulepath+"/leptonEfficiencies/MuonPOG/"
pathHTT = modulepath+"/leptonEfficiencies/HTT/Muon/"


class MuonSFs:
    
    def __init__(self, year=2017):
        """Load histograms from files."""
        
        assert year in [2016,2017,2018], "MuonSFs: You must choose a year from: 2016, 2017, or 2018."
        
        if year==2016:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2016_legacy/Muon_Run2016_legacy_IsoMu22.root",'ZMass','mu_trig')
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2016_legacy/Muon_Run2016_legacy_IdIso.root",'ZMass','mu_idiso')
        elif year==2017:
          #self.sftool_trig  = ScaleFactor(pathPOG+"Run2017/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root","IsoMu27_PtEtaBins/abseta_pt_ratio",'mu_trig')
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2017/Muon_IsoMu24orIsoMu27.root",'ZMass','mu_idiso')
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2017/Muon_IdIso_IsoLt0.15_eff_RerecoFall17.root",'ZMass','mu_idiso')
          #sftool_id         = ScaleFactor(pathPOG+"Run2017/RunBCDEF_SF_ID.root","NUM_MediumID_DEN_genTracks_pt_abseta",'mu_id',ptvseta=False)
          #sftool_iso        = ScaleFactor(pathPOG+"Run2017/RunBCDEF_SF_ISO.root","NUM_TightRelIso_DEN_MediumID_pt_abseta",'mu_iso',ptvseta=False)
          #self.sftool_idiso = sftool_id*sftool_iso
        else:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2018/Muon_Run2018_IsoMu24orIsoMu27.root",'ZMass','mu_trig')
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2018/Muon_Run2018_IdIso.root") # MediumID, DB corrected iso (dR<0.4) < 0.15
          #sftool_id         = ScaleFactor(pathPOG+"Run2018/RunABCD_SF_ID.root","NUM_MediumID_DEN_genTracks_pt_abseta",'mu_id',ptvseta=False)
          #sftool_iso        = ScaleFactor(pathPOG+"Run2018/RunABCD_SF_ISO.root","NUM_TightRelIso_DEN_MediumID_pt_abseta",'mu_iso',ptvseta=False)
          #self.sftool_idiso = sftool_id*sftool_iso
        
    def getTriggerSF(self, pt, eta):
        """Get SF for single muon trigger."""
        return self.sftool_trig.getSF(pt,abs(eta))
        
    def getIdIsoSF(self, pt, eta):
        """Get SF for muon identification + isolation."""
        return self.sftool_idiso.getSF(pt,abs(eta))
    
