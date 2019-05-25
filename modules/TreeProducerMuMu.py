import ROOT
import math 
import numpy as num 

from TreeProducerCommon import *

class TreeProducerMuMu(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""

    def __init__(self, name, dataType, **kwargs):
        print 'TreeProducerMuMu is called for', name
        super(TreeProducerMuMu, self).__init__(name,dataType,**kwargs)
        
        
        ##############
        #   MUON 1   #
        ##############
        
        self.addBranch('pt_1',                'f')
        self.addBranch('eta_1',               'f')
        self.addBranch('phi_1',               'f')
        self.addBranch('m_1',                 'f')
        self.addBranch('dxy_1',               'f')
        self.addBranch('dz_1',                'f')
        self.addBranch('pfRelIso04_all_1',    'f')
        self.addBranch('q_1',                 'i')
        
        
        ##############
        #   MUON 2   #
        ##############
        
        self.addBranch('pt_2',                'f')
        self.addBranch('eta_2',               'f')
        self.addBranch('phi_2',               'f')
        self.addBranch('m_2',                 'f')
        self.addBranch('dxy_2',               'f')
        self.addBranch('dz_2',                'f')
        self.addBranch('pfRelIso04_all_2',    'f')
        self.addBranch('q_2',                 'i')
        
        
        ###########
        #   TAU   #
        ###########
        
        self.addBranch('pt_3',                'f')
        self.addBranch('eta_3',               'f')
        self.addBranch('m_3',                 'f')
        self.addBranch('decayMode_3',         'i')
        self.addBranch('idAntiEle_3',         'i')
        self.addBranch('idAntiMu_3',          'i')
        ###self.addBranch('idDecayMode_3',       '?')
        ###self.addBranch('idDecayModeNewDMs_3', '?')
        self.addBranch('idMVAoldDM_3',        'i')
        self.addBranch('idMVAoldDM2017v1_3',  'i')
        self.addBranch('idMVAoldDM2017v2_3',  'i')
        self.addBranch('idMVAnewDM2017v2_3',  'i')
        self.addBranch('idIso_3',             'i')
        
        if not self._isData:
          self.addBranch('genPartFlav_1',     'i', -1)
          self.addBranch('genPartFlav_2',     'i', -1)
          self.addBranch('genPartFlav_3',     'i', -1)
        
