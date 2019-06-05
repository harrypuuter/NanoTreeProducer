import sys
from ModuleCommon import *
from TreeProducerEleTau import *
from corrections.ElectronSFs import *
from corrections.LeptonTauFakeSFs import *


class EleTauProducer(CommonProducer):
    
    def __init__(self, name, dataType, **kwargs):
        
        super(EleTauProducer,self).__init__(name,dataType,'eletau',**kwargs)
        self.out = TreeProducerEleTau(name,dataType,doJECSys=self.doJECSys)
        
        # TRIGGERS
        if self.year==2016:
          self.trigger  = lambda e: e.HLT_Ele25_eta2p1_WPTight_Gsf or e.HLT_Ele27_WPTight_Gsf #or e.HLT_Ele45_WPLoose_Gsf_L1JetTauSeeded #or e.HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1 or e.HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20 or e.HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30
          self.eleCutPt = lambda e: 26 if e.HLT_Ele25_eta2p1_WPTight_Gsf else 28
        elif self.year==2017:
          self.trigger  = lambda e: e.HLT_Ele35_WPTight_Gsf or e.HLT_Ele32_WPTight_Gsf_L1DoubleEG or e.HLT_Ele32_WPTight_Gsf
          self.eleCutPt = lambda e: 33 if (e.HLT_Ele32_WPTight_Gsf_L1DoubleEG or e.HLT_Ele32_WPTight_Gsf) else 35
        else:
          self.trigger  = lambda e: e.HLT_Ele32_WPTight_Gsf or e.HLT_Ele35_WPTight_Gsf
          self.eleCutPt = lambda e: 33 if e.HLT_Ele32_WPTight_Gsf else 36
        self.tauCutPt   = 20
        
        # CORRECTIONS
        if not self.isData:
          self.eleSFs   = ElectronSFs(year=self.year)
          self.ltfSFs   = LeptonTauFakeSFs('loose','tight',year=self.year)
        
        # CUTFLOW
        self.Nocut = 0
        self.Trigger = 1
        self.GoodElectrons = 2
        self.GoodTaus = 3
        self.GoodDiLepton = 4
        self.TotalWeighted = 15
        self.TotalWeighted_no0PU = 16
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Nocut,               "no cut"                 )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Trigger,             "trigger"                )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodElectrons,       "electron object"        )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodTaus,            "tau object"             )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodDiLepton,        "eletau pair"            )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted,       "no cut, weighted"       )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted_no0PU, "no cut, weighted, PU>0" )
        self.out.cutflow.GetXaxis().SetLabelSize(0.041)
        
    
    def beginJob(self):
        super(EleTauProducer,self).beginJob()
        print ">>> %-12s = %s"%('eleCutPt', self.eleCutPt)
        print ">>> %-12s = %s"%('tauCutPt', self.tauCutPt)
        pass
        
    
    def analyze(self, event):
        """Process and select events; fill branches and return True if the events passes,
        return False otherwise."""
        sys.stdout.flush()
        
        #####################################
        if self.isVectorLQ and hasTop(event):
          return False
        self.out.cutflow.Fill(self.Nocut)
        if self.isData:
          self.out.cutflow.Fill(self.TotalWeighted, 1.)
          if event.PV_npvs>0:
            self.out.cutflow.Fill(self.TotalWeighted_no0PU, 1.)
          else:
            return False
        else:
          self.out.cutflow.Fill(self.TotalWeighted, event.genWeight)
          if event.Pileup_nTrueInt>0:
            self.out.cutflow.Fill(self.TotalWeighted_no0PU, event.genWeight)
          else:
            return False
        #####################################
        
        
        if not self.trigger(event):
            return False
        
        #####################################
        self.out.cutflow.Fill(self.Trigger)
        #####################################
        
        
        idx_goodelectrons = [ ]
        for ielectron in range(event.nElectron):
            if event.Electron_pt[ielectron] < self.eleCutPt(event): continue
            if abs(event.Electron_eta[ielectron]) > 2.4: continue
            if abs(event.Electron_dz[ielectron]) > 0.2: continue
            if abs(event.Electron_dxy[ielectron]) > 0.045: continue
            if not event.Electron_convVeto[ielectron]: continue
            if ord(event.Electron_lostHits[ielectron]) > 1: continue
            if not (event.Electron_mvaFall17V2Iso_WP90[ielectron] or event.Electron_mvaFall17V2noIso_WP90[ielectron]): continue
            idx_goodelectrons.append(ielectron)
        
        if len(idx_goodelectrons)==0:
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodElectrons)
        #####################################
        
        
        Tau_genmatch = { } # bug in Tau_genPartFlav
        idx_goodtaus = [ ]
        for itau in range(event.nTau):
            if not self.vlooseIso(event,itau): continue
            if abs(event.Tau_eta[itau]) > 2.3: continue
            if abs(event.Tau_dz[itau]) > 0.2: continue
            if event.Tau_decayMode[itau] not in [0,1,10]: continue
            if abs(event.Tau_charge[itau])!=1: continue
            if not self.isData:
              Tau_genmatch[itau] = genmatch(event,itau)
              #if self.tes!=1.0 and Tau_genmatch[itau]==5:
              #  event.Tau_pt[itau]   *= self.tes
              #  event.Tau_mass[itau] *= self.tes
              #elif self.ltf!=1.0 and 0<Tau_genmatch[itau]<5:
              #  event.Tau_pt[itau]   *= self.ltf
              #  event.Tau_mass[itau] *= self.ltf
              #elif self.jtf!=1.0 and Tau_genmatch[itau]==0:
              #  event.Tau_pt[itau]   *= self.jtf
              #  event.Tau_mass[itau] *= self.jtf
            if event.Tau_pt[itau] < self.tauCutPt: continue
            ###if ord(event.Tau_idAntiEle[itau])<1: continue
            ###if ord(event.Tau_idAntiMu[itau])<1: continue
            idx_goodtaus.append(itau)
        
        if len(idx_goodtaus)==0:
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodTaus)
        #####################################
        
        
        electrons = Collection(event, 'Electron')
        taus  = Collection(event, 'Tau')
        ltaus = [ ]
        for idx1 in idx_goodelectrons:
            for idx2 in idx_goodtaus:
                dR = taus[idx2].p4().DeltaR(electrons[idx1].p4())
                if dR < 0.5: continue
                ltau = LeptonTauPair(idx1, event.Electron_pt[idx1], event.Electron_pfRelIso03_all[idx1],
                                     idx2, event.Tau_pt[idx2],      event.Tau_rawMVAoldDM2017v2[idx2])
                ltaus.append(ltau)
        
        if len(ltaus)==0:
            return False
        
        ltau     = bestDiLepton(ltaus)
        electron = electrons[ltau.id1].p4()
        tau      = taus[ltau.id2].p4()
        #print 'chosen tau1 (idx, pt) = ', ltau.id1, ltau.tau1_pt, 'check', electron.p4().Pt()
        #print 'chosen tau2 (idx, pt) = ', ltau.id2, ltau.tau2_pt, 'check', tau.p4().Pt()
        
        #####################################
        self.out.cutflow.Fill(self.GoodDiLepton)
        #####################################
        
        
        # VETOS
        extramuon, extraelec_veto, dilepton_veto = extraLeptonVetos(event,[ltau.id1],[ ],[ltau.id2],self.channel)
        self.out.extramuon_veto[0], self.out.extraelec_veto[0], self.out.dilepton_veto[0] = extraLeptonVetos(event,[ltau.id1],[ ],[ ],self.channel)
        self.out.lepton_vetos_noTau[0] = extramuon or extraelec_veto or dilepton_veto
        self.out.lepton_vetos[0]       = self.out.extramuon_veto[0] or self.out.extraelec_veto[0] or self.out.dilepton_veto[0]
        ###if self.doTight and (self.out.lepton_vetos[0] or event.Electron_pfRelIso03_all[ltau.id1]>0.10 or\
        ###                     ord(event.Tau_idAntiMu[ltau.id2]<1 or ord(event.Tau_idAntiEle[ltau.id2]<8):
        ###  return False
        
        
        # EVENT
        self.fillEventBranches(event)
        
        
        # ELECTRON
        self.out.pt_1[0]                       = event.Electron_pt[ltau.id1]
        self.out.eta_1[0]                      = event.Electron_eta[ltau.id1]
        self.out.phi_1[0]                      = event.Electron_phi[ltau.id1]
        self.out.m_1[0]                        = event.Electron_mass[ltau.id1]
        self.out.dxy_1[0]                      = event.Electron_dxy[ltau.id1]
        self.out.dz_1[0]                       = event.Electron_dz[ltau.id1]         
        self.out.q_1[0]                        = event.Electron_charge[ltau.id1]
        self.out.pfRelIso03_all_1[0]           = event.Electron_pfRelIso03_all[ltau.id1]
        self.out.cutBased_1[0]                 = event.Electron_cutBased[ltau.id1]
        self.out.mvaFall17Iso_WP90_1[0]        = event.Electron_mvaFall17V2Iso_WP90[ltau.id1]
        self.out.mvaFall17Iso_WP80_1[0]        = event.Electron_mvaFall17V2Iso_WP80[ltau.id1]
        self.out.mvaFall17noIso_WP90_1[0]      = event.Electron_mvaFall17V2noIso_WP90[ltau.id1]
        self.out.mvaFall17noIso_WP80_1[0]      = event.Electron_mvaFall17V2noIso_WP80[ltau.id1]
        
        
        # TAU
        self.out.pt_2[0]                       = event.Tau_pt[ltau.id2]
        self.out.eta_2[0]                      = event.Tau_eta[ltau.id2]
        self.out.phi_2[0]                      = event.Tau_phi[ltau.id2]
        self.out.m_2[0]                        = event.Tau_mass[ltau.id2]
        self.out.dxy_2[0]                      = event.Tau_dxy[ltau.id2]
        self.out.dz_2[0]                       = event.Tau_dz[ltau.id2]         
        self.out.leadTkPtOverTauPt_2[0]        = event.Tau_leadTkPtOverTauPt[ltau.id2]
        self.out.chargedIso_2[0]               = event.Tau_chargedIso[ltau.id2]
        self.out.neutralIso_2[0]               = event.Tau_neutralIso[ltau.id2]
        self.out.photonsOutsideSignalCone_2[0] = event.Tau_photonsOutsideSignalCone[ltau.id2]
        self.out.puCorr_2[0]                   = event.Tau_puCorr[ltau.id2]
        self.out.rawAntiEle_2[0]               = event.Tau_rawAntiEle[ltau.id2]
        self.out.rawIso_2[0]                   = event.Tau_rawIso[ltau.id2]
        self.out.q_2[0]                        = event.Tau_charge[ltau.id2]
        self.out.decayMode_2[0]                = event.Tau_decayMode[ltau.id2]
        ###self.out.rawAntiEleCat_2[0]            = event.Tau_rawAntiEleCat[ltau.id2]
        self.out.idAntiEle_2[0]                = ord(event.Tau_idAntiEle[ltau.id2])
        self.out.idAntiMu_2[0]                 = ord(event.Tau_idAntiMu[ltau.id2])
        self.out.idDecayMode_2[0]              = event.Tau_idDecayMode[ltau.id2]
        self.out.idDecayModeNewDMs_2[0]        = event.Tau_idDecayModeNewDMs[ltau.id2]
        self.out.rawMVAoldDM_2[0]              = event.Tau_rawMVAoldDM[ltau.id2]
        self.out.rawMVAnewDM2017v2_2[0]        = event.Tau_rawMVAnewDM2017v2[ltau.id2]
        self.out.rawMVAoldDM2017v1_2[0]        = event.Tau_rawMVAoldDM2017v1[ltau.id2]
        self.out.rawMVAoldDM2017v2_2[0]        = event.Tau_rawMVAoldDM2017v2[ltau.id2]
        self.out.idMVAoldDM_2[0]               = ord(event.Tau_idMVAoldDM[ltau.id2])
        self.out.idMVAoldDM2017v1_2[0]         = ord(event.Tau_idMVAoldDM2017v1[ltau.id2])
        self.out.idMVAoldDM2017v2_2[0]         = ord(event.Tau_idMVAoldDM2017v2[ltau.id2])
        self.out.idMVAnewDM2017v2_2[0]         = ord(event.Tau_idMVAnewDM2017v2[ltau.id2])
        
        
        # GENERATOR
        if not self.isData:
          self.out.genPartFlav_1[0]  = ord(event.Electron_genPartFlav[ltau.id1])
          self.out.genPartFlav_2[0]  = Tau_genmatch[ltau.id2] # ord(event.Tau_genPartFlav[ltau.id2])
          
          genvistau = Collection(event, 'GenVisTau')
          dRmax  = 1000
          gendm  = -1
          genpt  = -1
          geneta = -1
          genphi = -1
          for igvt in range(event.nGenVisTau):
            dR = genvistau[igvt].p4().DeltaR(tau)
            if dR < 0.5 and dR < dRmax:
              dRmax  = dR
              gendm  = event.GenVisTau_status[igvt]
              genpt  = event.GenVisTau_pt[igvt]
              geneta = event.GenVisTau_eta[igvt]
              genphi = event.GenVisTau_phi[igvt]
          
          self.out.gendecayMode_2[0] = gendm
          self.out.genvistaupt_2[0]  = genpt
          self.out.genvistaueta_2[0] = geneta
          self.out.genvistauphi_2[0] = genphi
        
        
        # JETS
        jetIds, jetIds50, met, njets_var, met_vars = self.fillJetBranches(event,electron,tau)
        if event.Tau_jetIdx[ltau.id2]>=0:
          self.out.jpt_match_2[0] = event.Jet_pt[event.Tau_jetIdx[ltau.id2]]
        else:
          self.out.jpt_match_2[0] = -1
        
        
        # WEIGHTS
        if not self.isData:
          self.applyCommonCorrections(event,jetIds,jetIds50,met,njets_var,met_vars)
          if self.vlooseIso(event,ltau.id2) and event.Electron_pfRelIso03_all[ltau.id1]<0.50:
            self.btagTool.fillEfficiencies(event,jetIds)
            self.btagTool_loose.fillEfficiencies(event,jetIds)
          self.out.trigweight[0]    = self.eleSFs.getTriggerSF(self.out.pt_1[0], self.out.eta_1[0])
          self.out.idisoweight_1[0] = self.eleSFs.getIdIsoSF(self.out.pt_1[0],self.out.eta_1[0])
          self.out.idisoweight_2[0] = self.ltfSFs.getSF(self.out.genPartFlav_2[0],self.out.eta_2[0])
          self.out.weight[0]        = self.out.genweight[0]*self.out.puweight[0]*self.out.trigweight[0]*self.out.idisoweight_1[0]*self.out.idisoweight_2[0]
        
        
        # MET & DILEPTON VARIABLES
        self.fillMETAndDiLeptonBranches(event,electron,tau,met,met_vars)
        
        
        self.out.tree.Fill()
        return True
        
