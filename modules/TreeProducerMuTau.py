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
        
        self.addBranch('pt_1',                       'f')
        self.addBranch('eta_1',                      'f')
        self.addBranch('phi_1',                      'f')
        self.addBranch('m_1',                        'f')
        self.addBranch('y_1',                        'f')
        self.addBranch('dxy_1',                      'f')
        self.addBranch('dz_1',                       'f')
        self.addBranch('q_1',                        'i')
        self.addBranch('pfRelIso04_all_1',           'f')
        
        
        ###########
        #   TAU   #
        ###########
        
        self.addBranch('pt_2',                       'f')
        self.addBranch('eta_2',                      'f')
        self.addBranch('phi_2',                      'f')
        self.addBranch('m_2',                        'f')
        self.addBranch('y_2',                        'f')
        self.addBranch('dxy_2',                      'f')
        self.addBranch('dz_2',                       'f')
        self.addBranch('leadTkPtOverTauPt_2',        'f')
        self.addBranch('chargedIso_2',               'f')
        self.addBranch('neutralIso_2',               'f')
        self.addBranch('photonsOutsideSignalCone_2', 'f')
        self.addBranch('puCorr_2',                   'f')
        self.addBranch('q_2',                        'i')
        self.addBranch('decayMode_2',                'i')
        self.addBranch('rawAntiEle_2',               'f')
        ###self.addBranch('rawAntiEleCat_2',            'f')
        self.addBranch('rawIso_2',                   'f')
        ###self.addBranch('rawMVAoldDM_2',              'f')
        ###self.addBranch('rawMVAoldDM2017v1_2',        'f')
        self.addBranch('rawMVAoldDM2017v2_2',        'f')
        self.addBranch('rawMVAnewDM2017v2_2',        'f')
        self.addBranch('rawDeepTau2017v2VSe_2',      'f')
        self.addBranch('rawDeepTau2017v2VSmu_2',     'f')
        self.addBranch('rawDeepTau2017v2VSjet_2',    'f')
        self.addBranch('idAntiEle_2',                'i')
        self.addBranch('idAntiMu_2',                 'i')
        self.addBranch('idDecayMode_2',              '?')
        self.addBranch('idDecayModeNewDMs_2',        '?')
        ###self.addBranch('idMVAoldDM_2',               'i')
        ###self.addBranch('idMVAoldDM2017v1_2',         'i')
        self.addBranch('idMVAoldDM2017v2_2',         'i')
        self.addBranch('idMVAnewDM2017v2_2',         'i')
        self.addBranch('idDeepTau2017v2VSe_2',       'i')
        self.addBranch('idDeepTau2017v2VSmu_2',      'i')
        self.addBranch('idDeepTau2017v2VSjet_2',     'i')
        self.addBranch('idIso_2',                    'i')
        self.addBranch('jpt_match_2',                'f')
        
        if not self._isData:
          self.addBranch('genPartFlav_1',            'i', -1)
          self.addBranch('genPartFlav_2',            'i', -1)
          self.addBranch('gendecayMode_2',           'i', -1)
          self.addBranch('genvistaupt_2',            'f', -1)
          self.addBranch('genvistaueta_2',           'f', -9)
          self.addBranch('genvistauphi_2',           'f', -9)
        if self._isEmb:
          self.addBranch('generatorWeight',          'f', -9)
        
