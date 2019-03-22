# Author: Izaak Neutelings (November 2018)
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Electron_efficiencies_and_scale
# https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Efficiency_Scale_Factors
# https://github.com/CMS-HTT/LeptonEfficiencies/tree/master/Electron/
# 2018: https://hypernews.cern.ch/HyperNews/CMS/get/higgstautau/1132.html
from CorrectionTools import modulepath
from ROOT import TFile
from ScaleFactorTool import ScaleFactor, ScaleFactorHTT
pathPOG = modulepath+"/leptonEfficiencies/EGammaPOG/"
pathHTT = modulepath+"/leptonEfficiencies/HTT/Electron/"


class ElectronSFs:
    
    def __init__(self, year=2017):
        """Load histograms from files."""
        
        assert year in [2016,2017,2018], "ElectronSFs: You must choose a year from: 2016, 2017, or 2018."
        
        if year==2016:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2016BtoH/Electron_Ele27Loose_OR_Ele25Tight_eff.root",'ZMass','ele_trig')
          self.sftool_reco  = ScaleFactor(pathPOG+"2016/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root",'EGamma_SF2D','ele_reco')
          self.sftool_idiso = ScaleFactorHTT(pathHTT+"2016/Run2016BtoH/Electron_IdIso_IsoLt0p1_eff.root",'ZMass','ele_idiso')
        elif year==2017:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2017/Electron_Ele32orEle35.root",'ZMass','ele_trig')
          self.sftool_reco  = ScaleFactor(pathPOG+"2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root",'EGamma_SF2D','ele_reco')
          self.sftool_idiso = ScaleFactor(pathPOG+"2017/2017_ElectronMVA80noiso.root",'EGamma_SF2D','ele_id')
          #self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2017/Electron_IdIso_IsoLt0.15_IsoID_eff.root","ZMass",'ele_idiso')
        else:
          self.sftool_trig  = ScaleFactorHTT(pathHTT+"Run2018/Electron_Run2018_Ele32orEle35.root",'ZMass','ele_trig')
          #self.sftool_idiso = ScaleFactorHTT(pathHTT+"Run2018/Electron_Run2018_IdIso.root",'ZMass','ele_idiso') # MVA nonIso Fall17 WP90, rho-corrected Iso(dR<0.3)<0.1
          self.sftool_reco  = ScaleFactor(pathPOG+"2018/egammaEffi.txt_EGM2D_updatedAll.root",'EGamma_SF2D','ele_reco')
          self.sftool_idiso = ScaleFactor(pathPOG+"2018/2018_ElectronMVA80noiso.root",'EGamma_SF2D','ele_id')
        
        if self.sftool_reco:
          self.sftool_idiso = self.sftool_reco * self.sftool_idiso
        
    def getTriggerSF(self, pt, eta):
        """Get SF for single electron trigger."""
        return self.sftool_trig.getSF(pt,eta)
        
    def getIdIsoSF(self, pt, eta):
        """Get SF for electron identification + isolation."""
        return self.sftool_idiso.getSF(pt,eta)
    
