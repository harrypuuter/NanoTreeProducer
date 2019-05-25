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
        
        self.addBranch('pt_1',                'F')
        self.addBranch('eta_1',               'F')
        self.addBranch('phi_1',               'F')
        self.addBranch('m_1',                 'F')
        self.addBranch('dxy_1',               'F')
        self.addBranch('dz_1',                'F')
        self.addBranch('pfRelIso04_all_1',    'F')
        self.addBranch('q_1',                 'I')
        
        
        ##############
        #   MUON 2   #
        ##############
        
        self.addBranch('pt_2',                'F')
        self.addBranch('eta_2',               'F')
        self.addBranch('phi_2',               'F')
        self.addBranch('m_2',                 'F')
        self.addBranch('dxy_2',               'F')
        self.addBranch('dz_2',                'F')
        self.addBranch('pfRelIso04_all_2',    'F')
        self.addBranch('q_2',                 'I')
        
        
        ###########
        #   TAU   #
        ###########
        
        self.addBranch('pt_3',                'F')
        self.addBranch('eta_3',               'F')
        self.addBranch('m_3',                 'F')
        self.addBranch('decayMode_3',         'I')
        self.addBranch('idAntiEle_3',         'I')
        self.addBranch('idAntiMu_3',          'I')
        ###self.addBranch('idDecayMode_3',       '?')
        ###self.addBranch('idDecayModeNewDMs_3', '?')
        self.addBranch('idMVAoldDM_3',        'I')
        self.addBranch('idMVAoldDM2017v1_3',  'I')
        self.addBranch('idMVAoldDM2017v2_3',  'I')
        self.addBranch('idMVAnewDM2017v2_3',  'I')
        self.addBranch('idIso_3',             'I')
        
        if not self._isData:
          self.addBranch('genPartFlav_1',     'I', -1)
          self.addBranch('genPartFlav_2',     'I', -1)
          self.addBranch('genPartFlav_3',     'I', -1)
        
