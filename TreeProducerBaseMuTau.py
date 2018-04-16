import ROOT
import math 
import numpy as num 

class TreeProducerBaseMuTau(object):

    def __init__(self, name):

        print 'TreeProducerBaseMuTau is called', name

        self.outputfile = ROOT.TFile(name, 'recreate')
        self.tree = ROOT.TTree('tree','tree')

        # histogram for cutflow

        self.h_cutflow = ROOT.TH1F("h_cutflow", "h_cutflow", 10, 0, 10) 


        # trees

        ##################
        # muon
        ##################

        self.pt_1                       = num.zeros(1, dtype=float)
        self.eta_1                      = num.zeros(1, dtype=float)
        self.phi_1                      = num.zeros(1, dtype=float)
        self.mass_1                     = num.zeros(1, dtype=float)
        self.dxy_1                      = num.zeros(1, dtype=float)
        self.dz_1                       = num.zeros(1, dtype=float)        
        self.pfRelIso04_all_1           = num.zeros(1, dtype=float)
        self.q_1                   = num.zeros(1, dtype=int)
        
        self.tree.Branch('pt_1'                      , self.pt_1, 'pt_1/D')
        self.tree.Branch('eta_1'                     , self.eta_1, 'eta_1/D')
        self.tree.Branch('phi_1'                     , self.phi_1, 'phi_1/D')
        self.tree.Branch('mass_1'                    , self.mass_1, 'mass_1/D')
        self.tree.Branch('dxy_1'                     , self.dxy_1, 'dxy_1/D')
        self.tree.Branch('dz_1'                      , self.dz_1, 'dz_1/D')
        self.tree.Branch('q_1'                       , self.q_1, 'q_1/I')
        self.tree.Branch('pfRelIso04_all_1'          , self.pfRelIso04_all_1, 'pfRelIso04_all_1/D')


        ##################
        # tau 2
        ##################

        self.pt_2                       = num.zeros(1, dtype=float)
        self.eta_2                      = num.zeros(1, dtype=float)
        self.phi_2                      = num.zeros(1, dtype=float)
        self.mass_2                     = num.zeros(1, dtype=float)
        self.dxy_2                      = num.zeros(1, dtype=float)
        self.dz_2                       = num.zeros(1, dtype=float)        
        self.leadTkPtOverTauPt_2        = num.zeros(1, dtype=float)
        self.chargedIso_2               = num.zeros(1, dtype=float)
        self.neutralIso_2               = num.zeros(1, dtype=float)
        self.photonsOutsideSignalCone_2 = num.zeros(1, dtype=float)
        self.puCorr_2                   = num.zeros(1, dtype=float)
        self.rawAntiEle_2               = num.zeros(1, dtype=float)
        self.rawIso_2                   = num.zeros(1, dtype=float)
        self.rawMVAnewDM_2              = num.zeros(1, dtype=float)
        self.rawMVAoldDM_2              = num.zeros(1, dtype=float)
        self.q_2                        = num.zeros(1, dtype=int)
        self.decayMode_2                = num.zeros(1, dtype=int)
        self.rawAntiEleCat_2            = num.zeros(1, dtype=float)
        self.idAntiEle_2                = num.zeros(1, dtype=int)
        self.idAntiMu_2                 = num.zeros(1, dtype=int)
        self.idDecayMode_2              = num.zeros(1, dtype=int)
        self.idDecayModeNewDMs_2        = num.zeros(1, dtype=int)
        self.idMVAnewDM_2               = num.zeros(1, dtype=int)
        self.idMVAoldDM_2               = num.zeros(1, dtype=int)
        self.genPartFlav_2              = num.zeros(1, dtype=int)
        self.gendecayMode_2             = num.zeros(1, dtype=int)
        self.genvistaupt_2              = num.zeros(1, dtype=float)
        self.genvistaueta_2             = num.zeros(1, dtype=float)
        self.genvistauphi_2             = num.zeros(1, dtype=float)


        self.tree.Branch('pt_2'                      , self.pt_2, 'pt_2/D')
        self.tree.Branch('eta_2'                     , self.eta_2, 'eta_2/D')
        self.tree.Branch('phi_2'                     , self.phi_2, 'phi_2/D')
        self.tree.Branch('mass_2'                    , self.mass_2, 'mass_2/D')
        self.tree.Branch('dxy_2'                     , self.dxy_2, 'dxy_2/D')
        self.tree.Branch('dz_2'                      , self.dz_2, 'dz_2/D')
        self.tree.Branch('leadTkPtOverTauPt_2'       , self.leadTkPtOverTauPt_2, 'leadTkPtOverTauPt_2/D')
        self.tree.Branch('chargedIso_2'              , self.chargedIso_2, 'chargedIso_2/D')
        self.tree.Branch('neutralIso_2'              , self.neutralIso_2, 'neutralIso_2/D')
        self.tree.Branch('photonsOutsideSignalCone_2', self.photonsOutsideSignalCone_2, 'photonsOutsideSignalCone_2/D')
        self.tree.Branch('puCorr_2'                  , self.puCorr_2, 'puCorr_2/D')
        self.tree.Branch('rawAntiEle_2'              , self.rawAntiEle_2, 'rawAntiEle_2/D')
        self.tree.Branch('rawIso_2'                  , self.rawIso_2, 'rawIso_2/D')
        self.tree.Branch('rawMVAnewDM_2'             , self.rawMVAnewDM_2, 'rawMVAnewDM_2/D')
        self.tree.Branch('rawMVAoldDM_2'             , self.rawMVAoldDM_2, 'rawMVAoldDM_2/D')
        self.tree.Branch('q_2'                       , self.q_2, 'q_2/I')
        self.tree.Branch('decayMode_2'               , self.decayMode_2, 'decayMode_2/I')
        self.tree.Branch('rawAntiEleCat_2'           , self.rawAntiEleCat_2, 'rawAntiEleCat_2/D')
        self.tree.Branch('idAntiEle_2'               , self.idAntiEle_2, 'idAntiEle_2/I')
        self.tree.Branch('idAntiMu_2'                , self.idAntiMu_2, 'idAntiMu_2/I')
        self.tree.Branch('idDecayMode_2'             , self.idDecayMode_2, 'idDecayMode_2/I')
        self.tree.Branch('idDecayModeNewDMs_2'       , self.idDecayModeNewDMs_2, 'idDecayModeNewDMs_2/I')
        self.tree.Branch('idMVAnewDM_2'              , self.idMVAnewDM_2, 'idMVAnewDM_2/I')
        self.tree.Branch('idMVAoldDM_2'              , self.idMVAoldDM_2, 'idMVAoldDM_2/I')
        self.tree.Branch('genPartFlav_2'             , self.genPartFlav_2, 'genPartFlav_2/I')
        self.tree.Branch('gendecayMode_2'             , self.gendecayMode_2, 'gendecayMode_2/I')
        self.tree.Branch('genvistaupt_2'             , self.genvistaupt_2, 'genvistaupt_2/D')
        self.tree.Branch('genvistaueta_2'             , self.genvistaueta_2, 'genvistaueta_2/D')
        self.tree.Branch('genvistauphi_2'             , self.genvistauphi_2, 'genvistauphi_2/D')



        ##################
        # event variables
        ##################

        self.run                        = num.zeros(1, dtype=int)
        self.luminosityBlock            = num.zeros(1, dtype=int)        
        self.event                      = num.zeros(1, dtype=int)
        self.MET_pt                     = num.zeros(1, dtype=float)
        self.MET_phi                    = num.zeros(1, dtype=float)
        self.PuppiMET_pt                = num.zeros(1, dtype=float)
        self.PuppiMET_phi               = num.zeros(1, dtype=float)
        self.MET_significance           = num.zeros(1, dtype=float)
        self.MET_covXX                  = num.zeros(1, dtype=float)
        self.MET_covXY                  = num.zeros(1, dtype=float)
        self.MET_covYY                  = num.zeros(1, dtype=float)
        self.Pileup_nPU                 = num.zeros(1, dtype=int)
        self.Pileup_nTrueInt            = num.zeros(1, dtype=int)
        self.fixedGridRhoFastjetAll     = num.zeros(1, dtype=float)
        self.genWeight                  = num.zeros(1, dtype=float)
        self.LHE_NpLO                   = num.zeros(1, dtype=int)
        self.LHE_NpNLO                  = num.zeros(1, dtype=int)

        self.tree.Branch('run'                       , self.run, 'run/I')
        self.tree.Branch('luminosityBlock'           , self.luminosityBlock, 'luminosityBlock/I')
        self.tree.Branch('event'                     , self.event, 'event/I')
        self.tree.Branch('MET_pt'                    , self.MET_pt, 'MET_pt/D')
        self.tree.Branch('MET_phi'                   , self.MET_phi, 'MET_phi/D')
        self.tree.Branch('PuppiMET_pt'               , self.PuppiMET_pt, 'PuppiMET_pt/D')
        self.tree.Branch('PuppiMET_phi'              , self.PuppiMET_phi, 'PuppiMET_phi/D')
        self.tree.Branch('MET_significance'          , self.MET_significance, 'MET_significance/D')
        self.tree.Branch('Pileup_nPU'                , self.Pileup_nPU, 'Pileup_nPU/I')
        self.tree.Branch('Pileup_nTrueInt'           , self.Pileup_nTrueInt, 'Pileup_nTrueInt/I')
        self.tree.Branch('fixedGridRhoFastjetAll'    , self.fixedGridRhoFastjetAll, 'fixedGridRhoFastjetAll/D')
        self.tree.Branch('genWeight'                 , self.genWeight, 'genWeight/D')
        self.tree.Branch('LHE_NpLO'                  , self.LHE_NpLO, 'LHE_NpLO/I')
        self.tree.Branch('LHE_NpNLO'                 , self.LHE_NpNLO, 'LHE_NpNLO/I')


        # -- additionals from analyzers
        self.njets                      = num.zeros(1, dtype=int)
        self.nfjets                     = num.zeros(1, dtype=int)
        self.ncjets                     = num.zeros(1, dtype=int)
        self.nbtag                      = num.zeros(1, dtype=int)
        self.pfmt_1                     = num.zeros(1, dtype=float)
        self.pfmt_2                     = num.zeros(1, dtype=float)
    
        self.jpt_1                      = num.zeros(1, dtype=float)
        self.jeta_1                     = num.zeros(1, dtype=float)
        self.jphi_1                     = num.zeros(1, dtype=float)
        self.jcsvv2_1                   = num.zeros(1, dtype=float)

        self.jpt_2                      = num.zeros(1, dtype=float)
        self.jeta_2                     = num.zeros(1, dtype=float)
        self.jphi_2                     = num.zeros(1, dtype=float)
        self.jcsvv2_2                   = num.zeros(1, dtype=float)

        self.m_vis                      = num.zeros(1, dtype=float)
        self.pt_tt                      = num.zeros(1, dtype=float)
        self.dR_ll                      = num.zeros(1, dtype=float)

        self.tree.Branch('njets'                       , self.njets, 'njets/I')
        self.tree.Branch('ncjets'                      , self.ncjets, 'ncjets/I')
        self.tree.Branch('nfjets'                      , self.nfjets, 'nfjets/I')
        self.tree.Branch('nbtag'                       , self.nbtag, 'nbtag/I')

        self.tree.Branch('pfmt_1'                      , self.pfmt_1, 'pfmt_1/D')
        self.tree.Branch('pfmt_2'                      , self.pfmt_2, 'pfmt_2/D')

        self.tree.Branch('jpt_1'                       , self.jpt_1, 'jpt_1/D')
        self.tree.Branch('jeta_1'                      , self.jeta_1, 'jeta_1/D')
        self.tree.Branch('jphi_1'                      , self.jphi_1, 'jphi_1/D')

        self.tree.Branch('jpt_2'                       , self.jpt_2, 'jpt_2/D')
        self.tree.Branch('jeta_2'                      , self.jeta_2, 'jeta_2/D')
        self.tree.Branch('jphi_2'                      , self.jphi_2, 'jphi_2/D')

        self.tree.Branch('m_vis'                       , self.m_vis, 'm_vis/D')
        self.tree.Branch('pt_tt'                       , self.pt_tt, 'pt_tt/D')
        self.tree.Branch('dR_ll'                       , self.dR_ll, 'dR_ll/D')

    
#        self.m_vis
#        self.m_taub
#        self.m_taumub
#        self.m_tauj
#        self.m_muj
#        self.m_coll_muj
#        self.m_coll_tauj
#        self.mt_coll_muj
#        self.mt_coll_tauj
#        self.m_max_lj 
#        self.m_max_lb 
#        self.m_mub   
#    
#        self.dR_ll 
#        self.dphi_ll 
#        
#        self.pzetamiss
#        self.pzetavis 
#        self.pzeta_disc
        






