import ROOT
import math 
import numpy as num 
from TreeProducerCommon import *

class TreeProducerMuTau(TreeProducerCommon):

    def __init__(self, name):
        
        super(TreeProducerMuTau, self).__init__(name)
        print 'TreeProducerMuTau is called', name
        
        
        ############
        #   MUON   #
        ############
        
        self.addBranch('pt_1',                       float)
        self.addBranch('eta_1',                      float)
        self.addBranch('phi_1',                      float)
        self.addBranch('m_1',                        float)
        self.addBranch('dxy_1',                      float)
        self.addBranch('dz_1',                       float)
        self.addBranch('q_1',                        int)
        self.addBranch('pfRelIso04_all_1',           float)
        self.addBranch('genPartFlav_1',              int)
        
        
        ###########
        #   TAU   #
        ###########
        
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
        self.addBranch('idIso_2',                    int)
        self.addBranch('genPartFlav_2',              float)
        self.addBranch('gendecayMode_2',             float)
        self.addBranch('genvistaupt_2',              float)
        self.addBranch('genvistaueta_2',             float)
        self.addBranch('genvistauphi_2',             float)
        
        self.genPartFlav_1[0]  = -1
        self.genPartFlav_2[0]  = -1
        self.gendecayMode_2[0] = -1
        self.genvistaupt_2[0]  = -9
        self.genvistaueta_2[0] = -1
        self.genvistauphi_2[0] = -9
        
