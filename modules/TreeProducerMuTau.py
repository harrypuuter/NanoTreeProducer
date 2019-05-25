import ROOT
import math 
import numpy as num 
from TreeProducerCommon import *

class TreeProducerMuTau(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""

    def __init__(self, name, dataType, **kwargs):
        print 'TreeProducerMuTau is called for', name
        super(TreeProducerMuTau, self).__init__(name,dataType,**kwargs)
        
        
        ############
        #   MUON   #
        ############
        
        self.addBranch('pt_1',                       'F')
        self.addBranch('eta_1',                      'F')
        self.addBranch('phi_1',                      'F')
        self.addBranch('m_1',                        'F')
        self.addBranch('dxy_1',                      'F')
        self.addBranch('dz_1',                       'F')
        self.addBranch('q_1',                        'I')
        self.addBranch('pfRelIso04_all_1',           'F')
        
        
        ###########
        #   TAU   #
        ###########
        
        self.addBranch('pt_2',                       'F')
        self.addBranch('eta_2',                      'F')
        self.addBranch('phi_2',                      'F')
        self.addBranch('m_2',                        'F')
        self.addBranch('dxy_2',                      'F')
        self.addBranch('dz_2',                       'F')
        self.addBranch('leadTkPtOverTauPt_2',        'F')
        self.addBranch('chargedIso_2',               'F')
        self.addBranch('neutralIso_2',               'F')
        self.addBranch('photonsOutsideSignalCone_2', 'F')
        self.addBranch('puCorr_2',                   'F')
        self.addBranch('rawAntiEle_2',               'F')
        self.addBranch('rawIso_2',                   'F')
        self.addBranch('rawMVAnewDM2017v2_2',        'F')
        self.addBranch('rawMVAoldDM_2',              'F')
        self.addBranch('rawMVAoldDM2017v1_2',        'F')
        self.addBranch('rawMVAoldDM2017v2_2',        'F')
        self.addBranch('q_2',                        'I')
        self.addBranch('decayMode_2',                'I')
        ###self.addBranch('rawAntiEleCat_2',            'F')
        self.addBranch('idAntiEle_2',                'I')
        self.addBranch('idAntiMu_2',                 'I')
        self.addBranch('idDecayMode_2',              '?')
        self.addBranch('idDecayModeNewDMs_2',        '?')
        self.addBranch('idMVAnewDM2017v2_2',         'I')
        self.addBranch('idMVAoldDM_2',               'I')
        self.addBranch('idMVAoldDM2017v1_2',         'I')
        self.addBranch('idMVAoldDM2017v2_2',         'I')
        self.addBranch('idIso_2',                    'I')
        self.addBranch('jpt_match_2',                'F')
        
        if not self._isData:
          self.addBranch('genPartFlav_1',            'I', -1)
          self.addBranch('genPartFlav_2',            'I', -1)
          self.addBranch('gendecayMode_2',           'I', -1)
          self.addBranch('genvistaupt_2',            'F', -1)
          self.addBranch('genvistaueta_2',           'F', -9)
          self.addBranch('genvistauphi_2',           'F', -9)
        
