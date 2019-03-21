# Author: Izaak Neutelings (November 2018)
# https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Efficiency_Scale_Factors
# https://github.com/CMS-HTT/LeptonEfficiencies/tree/master/Electron/Run2017
from CorrectionTools import modulepath
from ROOT import TFile
from ScaleFactorTool import ScaleFactor, ScaleFactorHTT
path    = modulepath+"/leptonEfficiencies/"
pathHTT = modulepath+"/leptonEfficiencies/HTT/Electron/"


class ElectronSFs:
    
    def __init__(self, year=2017):
        """Load histograms from files."""
        
        assert year in [2016,2017,2018], "ElectronSFs: You must choose a year from: 2016, 2017, or 2018."
        
        if year==2016:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2016BtoH/Spring15_Id/Electron_Ele25_eta2p1_WPTight_2016BtoH_eff.root",'ZMass','mu_trig')
          self.sftool_reco  = None
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2016BtoH/Spring15_Id/Electron_IdIso_IsoLt0p1_2016BtoH_eff.root",'ZMass','mu_idiso')
        else:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2017/Electron_Ele32orEle35.root",'ZMass','ele_trig')
          self.sftool_reco  = ScaleFactor(path+"egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root","EGamma_SF2D",'ele_reco')
          self.sftool_idiso = ScaleFactor(path+"gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp80iso.root","EGamma_SF2D",'ele_idiso')
          #self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2017/Electron_IdIso_IsoLt0.15_IsoID_eff.root","ZMass",'ele_idiso')
          
    def getTriggerSF(self, pt, eta):
        """Get SF for single electron trigger."""
        return self.sftool_trig.getSF(pt,eta)
        
    def getIdIsoSF(self, pt, eta):
        """Get SF for electron identification + isolation."""
        sf_reco  = self.sftool_reco.getSF(pt,eta) if self.sftool_reco else 1.
        sf_idiso = self.sftool_idiso.getSF(pt,eta)
        return sf_reco*sf_idiso
    
