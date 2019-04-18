from TreeProducerCommon import *

class TreeProducerTauTau(TreeProducerCommon):

    def __init__(self, name, dataType, **kwargs):
        
        super(TreeProducerTauTau, self).__init__(name,dataType,**kwargs)
        print 'TreeProducerTauTau is called', name
        
        
        #############
        #   TAU 1   #
        #############
        
        self.addBranch('pt_1',                       float)
        self.addBranch('eta_1',                      float)
        self.addBranch('phi_1',                      float)
        self.addBranch('m_1',                        float)
        self.addBranch('dxy_1',                      float)
        self.addBranch('dz_1',                       float)
        self.addBranch('leadTkPtOverTauPt_1',        float)
        self.addBranch('chargedIso_1',               float)
        self.addBranch('neutralIso_1',               float)
        self.addBranch('photonsOutsideSignalCone_1', float)
        self.addBranch('puCorr_1',                   float)
        self.addBranch('rawAntiEle_1',               float)
        self.addBranch('rawIso_1',                   float)
        self.addBranch('rawMVAnewDM2017v2_1',        float)
        self.addBranch('rawMVAoldDM_1',              float)
        self.addBranch('rawMVAoldDM2017v1_1',        float)
        self.addBranch('rawMVAoldDM2017v2_1',        float)
        self.addBranch('q_1',                        int)
        self.addBranch('decayMode_1',                int)
        ###self.addBranch('rawAntiEleCat_1',            float)
        self.addBranch('idAntiEle_1',                int)
        self.addBranch('idAntiMu_1',                 int)
        self.addBranch('idDecayMode_1',              bool)
        self.addBranch('idDecayModeNewDMs_1',        bool)
        self.addBranch('idMVAnewDM2017v2_1',         int)
        self.addBranch('idMVAoldDM_1',               int)
        self.addBranch('idMVAoldDM2017v1_1',         int)
        self.addBranch('idMVAoldDM2017v2_1',         int)
        
        if not self._isData:
          self.addBranch('genPartFlav_1',            int,   -1)
          self.addBranch('gendecayMode_1',           int,   -1)
          self.addBranch('genvistaupt_1',            float, -1)
          self.addBranch('genvistaueta_1',           float, -9)
          self.addBranch('genvistauphi_1',           float, -9)
        
        
        #############
        #   TAU 2   #
        #############
        
        self.addBranch('pt_2',                       float)
        self.addBranch('eta_2',                      float)
        self.addBranch('phi_2',                      float)
        self.addBranch('m_2',                        float)
        self.addBranch('dxy_2',                      float)
        self.addBranch('dz_2',                       float)
        self.addBranch('leadTkPtOverTauPt_2',        float)
        self.addBranch('chargedIso_2',               float)
        self.addBranch('neutralIso_2',               float)
        self.addBranch('photonsOutsideSignalCone_2', float)
        self.addBranch('puCorr_2',                   float)
        self.addBranch('rawAntiEle_2',               float)
        self.addBranch('rawIso_2',                   float)
        self.addBranch('rawMVAnewDM2017v2_2',        float)
        self.addBranch('rawMVAoldDM_2',              float)
        self.addBranch('rawMVAoldDM2017v1_2',        float)
        self.addBranch('rawMVAoldDM2017v2_2',        float)
        self.addBranch('q_2',                        int)
        self.addBranch('decayMode_2',                int)
        ###self.addBranch('rawAntiEleCat_2',            float)
        self.addBranch('idAntiEle_2',                int)
        self.addBranch('idAntiMu_2',                 int)
        self.addBranch('idDecayMode_2',              bool)
        self.addBranch('idDecayModeNewDMs_2',        bool)
        self.addBranch('idMVAnewDM2017v2_2',         int)
        self.addBranch('idMVAoldDM_2',               int)
        self.addBranch('idMVAoldDM2017v1_2',         int)
        self.addBranch('idMVAoldDM2017v2_2',         int)
        
        if not self._isData:
          self.addBranch('genPartFlav_2',            int,   -1)
          self.addBranch('gendecayMode_2',           int,   -1)
          self.addBranch('genvistaupt_2',            float, -1)
          self.addBranch('genvistaueta_2',           float, -9)
          self.addBranch('genvistauphi_2',           float, -9)
          self.addBranch('trigweightVT',             float, 1.)
        
