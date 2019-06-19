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
        
        self.addBranch('pt_1',                       'f')
        self.addBranch('eta_1',                      'f')
        self.addBranch('phi_1',                      'f')
        self.addBranch('m_1',                        'f')
        self.addBranch('y_1',                        'f')
        self.addBranch('dxy_1',                      'f')
        self.addBranch('dz_1',                       'f')
        self.addBranch('leadTkPtOverTauPt_1',        'f')
        self.addBranch('chargedIso_1',               'f')
        self.addBranch('neutralIso_1',               'f')
        self.addBranch('photonsOutsideSignalCone_1', 'f')
        self.addBranch('puCorr_1',                   'f')
        self.addBranch('rawAntiEle_1',               'f')
        self.addBranch('rawIso_1',                   'f')
        self.addBranch('rawMVAnewDM2017v2_1',        'f')
        self.addBranch('rawMVAoldDM_1',              'f')
        self.addBranch('rawMVAoldDM2017v1_1',        'f')
        self.addBranch('rawMVAoldDM2017v2_1',        'f')
        self.addBranch('q_1',                        'i')
        self.addBranch('decayMode_1',                'i')
        ###self.addBranch('rawAntiEleCat_1',            'f')
        self.addBranch('idAntiEle_1',                'i')
        self.addBranch('idAntiMu_1',                 'i')
        self.addBranch('idDecayMode_1',              '?')
        self.addBranch('idDecayModeNewDMs_1',        '?')
        self.addBranch('idMVAnewDM2017v2_1',         'i')
        self.addBranch('idMVAoldDM_1',               'i')
        self.addBranch('idMVAoldDM2017v1_1',         'i')
        self.addBranch('idMVAoldDM2017v2_1',         'i')
        
        if not self._isData:
          self.addBranch('genPartFlav_1',            'i', -1)
          self.addBranch('gendecayMode_1',           'i', -1)
          self.addBranch('genvistaupt_1',            'f', -1)
          self.addBranch('genvistaueta_1',           'f', -9)
          self.addBranch('genvistauphi_1',           'f', -9)
        
        
        #############
        #   TAU 2   #
        #############
        
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
        self.addBranch('rawAntiEle_2',               'f')
        self.addBranch('rawIso_2',                   'f')
        self.addBranch('rawMVAnewDM2017v2_2',        'f')
        self.addBranch('rawMVAoldDM_2',              'f')
        self.addBranch('rawMVAoldDM2017v1_2',        'f')
        self.addBranch('rawMVAoldDM2017v2_2',        'f')
        self.addBranch('q_2',                        'i')
        self.addBranch('decayMode_2',                'i')
        ###self.addBranch('rawAntiEleCat_2',            'f')
        self.addBranch('idAntiEle_2',                'i')
        self.addBranch('idAntiMu_2',                 'i')
        self.addBranch('idDecayMode_2',              '?')
        self.addBranch('idDecayModeNewDMs_2',        '?')
        self.addBranch('idMVAnewDM2017v2_2',         'i')
        self.addBranch('idMVAoldDM_2',               'i')
        self.addBranch('idMVAoldDM2017v1_2',         'i')
        self.addBranch('idMVAoldDM2017v2_2',         'i')
        
        if not self._isData:
          self.addBranch('genPartFlav_2',            'i', -1)
          self.addBranch('gendecayMode_2',           'i', -1)
          self.addBranch('genvistaupt_2',            'f', -1)
          self.addBranch('genvistaueta_2',           'f', -9)
          self.addBranch('genvistauphi_2',           'f', -9)
          self.addBranch('trigweightVT',             'f', 1.)
          if not self.doTight:
            self.addBranch('trigweightUp',           'f', 1.)
            self.addBranch('trigweightDown',         'f', 1.)
        
