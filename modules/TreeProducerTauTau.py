from TreeProducerCommon import *

class TreeProducerTauTau(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""

    def __init__(self, name, dataType, **kwargs):
        print 'TreeProducerTauTau is called for', name
        super(TreeProducerTauTau,self).__init__(name,dataType,**kwargs)
        
        self.doTight = kwargs.get('doTight', False)
        
        
        #############
        #   TAU 1   #
        #############
        
        self.addBranch('pt_1',                       'F')
        self.addBranch('eta_1',                      'F')
        self.addBranch('phi_1',                      'F')
        self.addBranch('m_1',                        'F')
        self.addBranch('dxy_1',                      'F')
        self.addBranch('dz_1',                       'F')
        self.addBranch('leadTkPtOverTauPt_1',        'F')
        self.addBranch('chargedIso_1',               'F')
        self.addBranch('neutralIso_1',               'F')
        self.addBranch('photonsOutsideSignalCone_1', 'F')
        self.addBranch('puCorr_1',                   'F')
        self.addBranch('rawAntiEle_1',               'F')
        self.addBranch('rawIso_1',                   'F')
        self.addBranch('rawMVAnewDM2017v2_1',        'F')
        self.addBranch('rawMVAoldDM_1',              'F')
        self.addBranch('rawMVAoldDM2017v1_1',        'F')
        self.addBranch('rawMVAoldDM2017v2_1',        'F')
        self.addBranch('q_1',                        'I')
        self.addBranch('decayMode_1',                'I')
        ###self.addBranch('rawAntiEleCat_1',            'F')
        self.addBranch('idAntiEle_1',                'I')
        self.addBranch('idAntiMu_1',                 'I')
        self.addBranch('idDecayMode_1',              '?')
        self.addBranch('idDecayModeNewDMs_1',        '?')
        self.addBranch('idMVAnewDM2017v2_1',         'I')
        self.addBranch('idMVAoldDM_1',               'I')
        self.addBranch('idMVAoldDM2017v1_1',         'I')
        self.addBranch('idMVAoldDM2017v2_1',         'I')
        
        if not self._isData:
          self.addBranch('genPartFlav_1',            'I', -1)
          self.addBranch('gendecayMode_1',           'I', -1)
          self.addBranch('genvistaupt_1',            'F', -1)
          self.addBranch('genvistaueta_1',           'F', -9)
          self.addBranch('genvistauphi_1',           'F', -9)
        
        
        #############
        #   TAU 2   #
        #############
        
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
        
        if not self._isData:
          self.addBranch('genPartFlav_2',            'I', -1)
          self.addBranch('gendecayMode_2',           'I', -1)
          self.addBranch('genvistaupt_2',            'F', -1)
          self.addBranch('genvistaueta_2',           'F', -9)
          self.addBranch('genvistauphi_2',           'F', -9)
          self.addBranch('trigweightVT',             'F', 1.)
          if not self.doTight:
            self.addBranch('trigweightUp',           'F', 1.)
            self.addBranch('trigweightDown',         'F', 1.)
        
