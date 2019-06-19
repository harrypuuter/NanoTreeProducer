import sys
from ModuleCommon import *
from TreeProducerTauTau import *
from corrections.TauTriggerSFs import *
from corrections.LeptonTauFakeSFs import *


class TauTauProducer(CommonProducer):
    
    def __init__(self, name, dataType, **kwargs):
        
        super(TauTauProducer,self).__init__(name,dataType,'tautau',**kwargs)
        self.out = TreeProducerTauTau(name,dataType,JECSys=self.doJECSys,doTight=self.doTight)
        
        # TRIGGERS
        if self.year==2016:
          if self.isData:
            self.trigger = lambda e: e.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg \
                                     if e.run<280919 else e.HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg
          else:
            self.trigger = lambda e: e.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg or e.HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg
        elif self.year==2017:
            self.trigger = lambda e: e.HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg or e.HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
        else:
          if self.isData:
            self.trigger = lambda e: e.HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg or e.HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg \
                                     if e.run<317509 else e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
          else:
            self.trigger = lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
        self.tauCutPt    = 40
        
        # CORRECTIONS
        if not self.isData:
          self.tauSFs    = TauTriggerSFs('tautau','tight',year=self.year)
          self.tauSFsVT  = TauTriggerSFs('tautau','vtight',year=self.year)
          self.ltfSFs    = LeptonTauFakeSFs('loose','vloose',year=self.year)
        
        # CUTFLOW
        self.Nocut = 0
        self.Trigger = 1
        self.GoodTaus = 2
        self.GoodDiTau = 3
        self.Nocut_GT = 20
        self.Trigger_GT = 21
        self.GoodTaus_GT = 22
        self.GoodDiTau_GT = 23
        self.TotalWeighted = 15
        self.TotalWeighted_no0PU = 16
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Nocut,               "no cut"                 )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Trigger,             "trigger"                )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodTaus,            "tau objects"            )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodDiTau,           "ditau pair"             )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Nocut_GT,            "no cut, GM"             )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Trigger_GT,          "trigger, GM"            )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodTaus_GT,         "tau objects, GM"        )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodDiTau_GT,        "ditau pair, GM"         )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted,       "no cut, weighted"       )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted_no0PU, "no cut, weighted, PU>0" )
        self.out.cutflow.GetXaxis().SetLabelSize(0.041)
        
    
    def beginJob(self):
        super(TauTauProducer,self).beginJob()
        print ">>> %-12s = %s"%('tauCutPt',  self.tauCutPt)
        pass
        
    
    def analyze(self, event):
        """Process and select events; fill branches and return True if the events passes,
        return False otherwise."""
        sys.stdout.flush()
        
        ##print '-'*80
        #ngentauhads = 0
        #ngentaus = 0
        #if not self.isData:            
        #    for igp in range(event.nGenPart):
        #        if abs(event.GenPart_pdgId[igp])==15 and event.GenPart_status[igp]==2:
        #            genflag = event.GenPart_statusFlags[igp]
        #            binary = format(genflag,'b').zfill(15)
        #            # 0 : isPrompt
        #            # 1 : isDecayedLeptonHadron
        #            # 2 : isTauDecayProduct
        #            # 3 : isPromptTauDecayProduct
        #            # 4 : isDirectTauDecayProduct
        #            # 5 : isDirectPromptTauDecayProduct
        #            # 6 : isDirectHadronDecayProduct
        #            # 7 : isHardProcess
        #            # 8 : fromHardProcess
        #            # 9 : isHardProcessTauDecayProduct
        #            # 10 : isDirectHardProcessTauDecayProduct
        #            # 11 : fromHardProcessBeforeFSR
        #            # 12 : isFirstCopy
        #            # 13 : isLastCopy
        #            # 14 : isLastCopyBeforeFSR
        #            
        #            if int(binary[14])==0: continue
        #            if int(binary[6])==0: continue
        #            #print 'Tau found with status = 2 (pt, eta) = ', event.GenPart_pt[igp], event.GenPart_eta[igp], event.GenPart_statusFlags[igp]
        #            
        #            ngentaus += 1
        #            _pdg_ = -1
        #            _idx_ = event.GenPart_genPartIdxMother[igp]
        #            #_status_ = -1
        #            flag_resonance = False
        #            
        #            while abs(_pdg_) not in [9000002, 9000006]:
        #                if _idx_==-1: break
        #                _pdg_ = event.GenPart_pdgId[_idx_]
        #                # _status_ = event.GenPart_status[_idx_]
        #                _idx_ = event.GenPart_genPartIdxMother[_idx_]
        #                if abs(_pdg_) > 30 and abs(_pdg_) not in [9000002, 9000006]: 
        #                    flag_resonance = True
        #                #print '\t (pdg, mother id) = ', _pdg_, _status_, _idx_
        #            if flag_resonance: continue
        #            _dr_ = 100.
        #            for igvt in range(event.nGenVisTau):
        #                dr = deltaR(event.GenPart_eta[igp], event.GenPart_phi[igp], event.GenVisTau_eta[igvt], event.GenVisTau_phi[igvt])
        #                #print dr, _dr_, event.GenPart_eta[igp], event.GenPart_phi[igp], event.GenVisTau_eta[igvt], event.GenVisTau_phi[igvt]
        #                if _dr_ > dr:
        #                    _dr_ = dr
        #            #print 'match !',_pdg_, event.nGenVisTau,  _dr_
        #            if _dr_ < 0.1:
        #                ngentauhads += 1
        #    
        #    #for igvt in range(event.nGenVisTau):
        #    #    print 'status = ', event.GenVisTau_status[igvt], 'mother ID = ', event.GenVisTau_genPartIdxMother[igvt], 'pt = ', event.GenVisTau_pt[igvt], ', eta = ', event.GenVisTau_eta[igvt]
        #    #    ngentauhads += 1
        #    
        #    if ngentaus != 2:
        #       print 'WOW!!! ngentaus = %d != 2'%(ngentaus)
        
        
        #####################################
        if self.isVectorLQ and hasTop(event):
          return False
        self.out.cutflow.Fill(self.Nocut)
        #if ngentauhads == 2:
        #   self.out.cutflow.Fill(self.Nocut_GT)
        if self.isData:
          self.out.cutflow.Fill(self.TotalWeighted, 1.)
          if event.PV_npvs>0:
            self.out.cutflow.Fill(self.TotalWeighted_no0PU, 1.)
          else:
            return False
        else:
          self.out.cutflow.Fill(self.TotalWeighted, event.genWeight)
          self.out.pileup.Fill(event.Pileup_nTrueInt)
          if event.Pileup_nTrueInt>0:
            self.out.cutflow.Fill(self.TotalWeighted_no0PU, event.genWeight)
          else:
            return False
        #####################################        
        
        
        if not self.trigger(event):
            return False
        
        #####################################
        self.out.cutflow.Fill(self.Trigger)
        #if ngentauhads == 2:
        #    self.out.cutflow.Fill(self.Trigger_GT)
        #####################################
        
        
        Tau_genmatch = { } # bug in Tau_genPartFlav
        idx_goodtaus = [ ]
        for itau in range(event.nTau):
            if abs(event.Tau_eta[itau]) > 2.1: continue
            if abs(event.Tau_dz[itau]) > 0.2: continue
            if event.Tau_decayMode[itau] not in [0,1,10]: continue
            if abs(event.Tau_charge[itau])!=1: continue
            if not self.vlooseIso(event,itau): continue
            if not self.isData:
              Tau_genmatch[itau] = genmatch(event,itau)
              #if self.tes!=1.0:
              #  event.Tau_pt[itau]   *= self.tes
              #  event.Tau_mass[itau] *= self.tes
            if event.Tau_pt[itau] < self.tauCutPt: continue
            idx_goodtaus.append(itau)
        
        if len(idx_goodtaus)<2:
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodTaus)
        #if ngentauhads == 2:
        #    self.out.cutflow.Fill(self.GoodTaus_GT)
        #####################################
        
        
        taus = Collection(event, 'Tau')
        ditaus = [ ]
        for idx1 in idx_goodtaus:
          for idx2 in idx_goodtaus:
              if idx1 >= idx2: continue
              dR = taus[idx1].p4().DeltaR(taus[idx2].p4())
              if dR < 0.5: continue
              ditau = DiTauPair(idx1, event.Tau_pt[idx1], event.Tau_rawMVAoldDM[idx1],
                                idx2, event.Tau_pt[idx2], event.Tau_rawMVAoldDM[idx2])
              ditaus.append(ditau)
        
        if len(ditaus)==0:
            return False
        
        ditau = bestDiLepton(ditaus)
        tau1  = taus[ditau.id1].p4()
        tau2  = taus[ditau.id2].p4()
        #print 'chosen tau1 (idx, pt) = ', ditau.id1, ditau.tau1_pt, 'check', tau1.p4().Pt()
        #print 'chosen tau2 (idx, pt) = ', ditau.id2, ditau.tau2_pt, 'check', tau2.p4().Pt()
        
        #####################################
        self.out.cutflow.Fill(self.GoodDiTau)
        #if ngentauhads == 2:
        #    self.out.cutflow.Fill(self.GoodDiTau_GT)
        #####################################
        
        
        # VETOS
        extramuon_veto, extraelec_veto, dilepton_veto = extraLeptonVetos(event,[ ],[ ],[ditau.id1,ditau.id2],self.channel)
        self.out.extramuon_veto[0], self.out.extraelec_veto[0], self.out.dilepton_veto[0] = extraLeptonVetos(event,[ ],[ ],[ ],self.name)
        self.out.lepton_vetos_noTau[0] = extramuon_veto or extraelec_veto
        self.out.lepton_vetos[0]       = self.out.extramuon_veto[0] or self.out.extraelec_veto[0] #or self.out.dilepton_veto[0]
        
        
        # EVENT
        self.fillEventBranches(event)
        
        
        # TAU 1
        self.out.pt_1[0]                       = event.Tau_pt[ditau.id1]
        self.out.eta_1[0]                      = event.Tau_eta[ditau.id1]
        self.out.phi_1[0]                      = event.Tau_phi[ditau.id1]
        self.out.m_1[0]                        = event.Tau_mass[ditau.id1]
        self.out.y_1[0]                        = tau1.Rapidity()
        self.out.dxy_1[0]                      = event.Tau_dxy[ditau.id1]
        self.out.dz_1[0]                       = event.Tau_dz[ditau.id1]         
        self.out.leadTkPtOverTauPt_1[0]        = event.Tau_leadTkPtOverTauPt[ditau.id1]
        self.out.chargedIso_1[0]               = event.Tau_chargedIso[ditau.id1]
        self.out.neutralIso_1[0]               = event.Tau_neutralIso[ditau.id1]
        self.out.photonsOutsideSignalCone_1[0] = event.Tau_photonsOutsideSignalCone[ditau.id1]
        self.out.puCorr_1[0]                   = event.Tau_puCorr[ditau.id1]
        self.out.rawAntiEle_1[0]               = event.Tau_rawAntiEle[ditau.id1]
        self.out.rawIso_1[0]                   = event.Tau_rawIso[ditau.id1]
        self.out.rawMVAnewDM2017v2_1[0]        = event.Tau_rawMVAnewDM2017v2[ditau.id1]
        self.out.rawMVAoldDM_1[0]              = event.Tau_rawMVAoldDM[ditau.id1]
        self.out.rawMVAoldDM2017v1_1[0]        = event.Tau_rawMVAoldDM2017v1[ditau.id1]
        self.out.rawMVAoldDM2017v2_1[0]        = event.Tau_rawMVAoldDM2017v2[ditau.id1]
        self.out.q_1[0]                        = event.Tau_charge[ditau.id1]
        self.out.decayMode_1[0]                = event.Tau_decayMode[ditau.id1]
        ###self.out.rawAntiEleCat_1[0]            = event.Tau_rawAntiEleCat[ditau.id1]
        self.out.idAntiEle_1[0]                = ord(event.Tau_idAntiEle[ditau.id1])
        self.out.idAntiMu_1[0]                 = ord(event.Tau_idAntiMu[ditau.id1])
        self.out.idDecayMode_1[0]              = event.Tau_idDecayMode[ditau.id1]
        self.out.idDecayModeNewDMs_1[0]        = event.Tau_idDecayModeNewDMs[ditau.id1]
        self.out.idMVAnewDM2017v2_1[0]         = ord(event.Tau_idMVAnewDM2017v2[ditau.id1])
        self.out.idMVAoldDM_1[0]               = ord(event.Tau_idMVAoldDM[ditau.id1])
        self.out.idMVAoldDM2017v1_1[0]         = ord(event.Tau_idMVAoldDM2017v1[ditau.id1])
        self.out.idMVAoldDM2017v2_1[0]         = ord(event.Tau_idMVAoldDM2017v2[ditau.id1])
        
        
        # TAU 2
        self.out.pt_2[0]                       = event.Tau_pt[ditau.id2]
        self.out.eta_2[0]                      = event.Tau_eta[ditau.id2]
        self.out.phi_2[0]                      = event.Tau_phi[ditau.id2]
        self.out.m_2[0]                        = event.Tau_mass[ditau.id2]
        self.out.y_2[0]                        = tau2.Rapidity()
        self.out.dxy_2[0]                      = event.Tau_dxy[ditau.id2]
        self.out.dz_2[0]                       = event.Tau_dz[ditau.id2]         
        self.out.leadTkPtOverTauPt_2[0]        = event.Tau_leadTkPtOverTauPt[ditau.id2]
        self.out.chargedIso_2[0]               = event.Tau_chargedIso[ditau.id2]
        self.out.neutralIso_2[0]               = event.Tau_neutralIso[ditau.id2]
        self.out.photonsOutsideSignalCone_2[0] = event.Tau_photonsOutsideSignalCone[ditau.id2]
        self.out.puCorr_2[0]                   = event.Tau_puCorr[ditau.id2]
        self.out.rawAntiEle_2[0]               = event.Tau_rawAntiEle[ditau.id2]
        self.out.rawIso_2[0]                   = event.Tau_rawIso[ditau.id2]
        self.out.q_2[0]                        = event.Tau_charge[ditau.id2]
        self.out.decayMode_2[0]                = event.Tau_decayMode[ditau.id2]
        ###self.out.rawAntiEleCat_2[0]            = event.Tau_rawAntiEleCat[ditau.id2]
        self.out.idAntiEle_2[0]                = ord(event.Tau_idAntiEle[ditau.id2])
        self.out.idAntiMu_2[0]                 = ord(event.Tau_idAntiMu[ditau.id2])
        self.out.idDecayMode_2[0]              = event.Tau_idDecayMode[ditau.id2]
        self.out.idDecayModeNewDMs_2[0]        = event.Tau_idDecayModeNewDMs[ditau.id2]
        self.out.rawMVAoldDM_2[0]              = event.Tau_rawMVAoldDM[ditau.id2]
        self.out.rawMVAoldDM2017v1_2[0]        = event.Tau_rawMVAoldDM2017v1[ditau.id2]
        self.out.rawMVAoldDM2017v2_2[0]        = event.Tau_rawMVAoldDM2017v2[ditau.id2]
        self.out.rawMVAnewDM2017v2_2[0]        = event.Tau_rawMVAnewDM2017v2[ditau.id2]
        self.out.idMVAoldDM_2[0]               = ord(event.Tau_idMVAoldDM[ditau.id2])
        self.out.idMVAoldDM2017v1_2[0]         = ord(event.Tau_idMVAoldDM2017v1[ditau.id2])
        self.out.idMVAoldDM2017v2_2[0]         = ord(event.Tau_idMVAoldDM2017v2[ditau.id2])
        self.out.idMVAnewDM2017v2_2[0]         = ord(event.Tau_idMVAnewDM2017v2[ditau.id2])
        
        
        # GENERATOR
        if not self.isData:
          self.out.genPartFlav_1[0]  = Tau_genmatch[ditau.id1]
          self.out.genPartFlav_2[0]  = Tau_genmatch[ditau.id2]
          
          genvistau = Collection(event, 'GenVisTau')
          dRmax1,  dRmax2  = .5, .5
          gendm1,  gendm2  = -1, -1
          genpt1,  genpt2  = -1, -1
          geneta1, geneta2 = -9, -9
          genphi1, genphi2 = -9, -9
          for igvt in range(event.nGenVisTau):
            dR = genvistau[igvt].p4().DeltaR(tau1)
            if dR<dRmax1:
              dRmax1  = dR
              gendm1  = event.GenVisTau_status[igvt]
              genpt1  = event.GenVisTau_pt[igvt]
              geneta1 = event.GenVisTau_eta[igvt]
              genphi1 = event.GenVisTau_phi[igvt]
            dR = genvistau[igvt].p4().DeltaR(tau2)
            if dR<dRmax2:
              dRmax2  = dR
              gendm2  = event.GenVisTau_status[igvt]
              genpt2  = event.GenVisTau_pt[igvt]
              geneta2 = event.GenVisTau_eta[igvt]
              genphi2 = event.GenVisTau_phi[igvt]
          
          self.out.gendecayMode_1[0] = gendm1
          self.out.genvistaupt_1[0]  = genpt1
          self.out.genvistaueta_1[0] = geneta1
          self.out.genvistauphi_1[0] = genphi1
          
          self.out.gendecayMode_2[0] = gendm2
          self.out.genvistaupt_2[0]  = genpt2
          self.out.genvistaueta_2[0] = geneta2
          self.out.genvistauphi_2[0] = genphi2
        
        
        # JETS
        jetIds, jetIds50, met, njets_var, met_vars = self.fillJetBranches(event,tau1,tau2)
        
        
        # WEIGHTS
        if not self.isData:
          self.applyCommonCorrections(event,jetIds,jetIds50,met,njets_var,met_vars)
          if self.vlooseIso(event,ditau.id1) and self.vlooseIso(event,ditau.id2):
            self.btagTool.fillEfficiencies(event,jetIds)
            self.btagTool_loose.fillEfficiencies(event,jetIds)
          diTauLeg1SF                  = self.tauSFs.getTriggerSF(   self.out.pt_1[0],self.out.eta_1[0],self.out.phi_1[0],self.out.decayMode_1[0],self.out.genPartFlav_1[0] )
          diTauLeg2SF                  = self.tauSFs.getTriggerSF(   self.out.pt_2[0],self.out.eta_2[0],self.out.phi_2[0],self.out.decayMode_2[0],self.out.genPartFlav_2[0] )
          diTauLeg1SFVT                = self.tauSFsVT.getTriggerSF( self.out.pt_1[0],self.out.eta_1[0],self.out.phi_1[0],self.out.decayMode_1[0],self.out.genPartFlav_1[0] )
          diTauLeg2SFVT                = self.tauSFsVT.getTriggerSF( self.out.pt_2[0],self.out.eta_2[0],self.out.phi_2[0],self.out.decayMode_2[0],self.out.genPartFlav_2[0] )
          self.out.trigweight[0]       = diTauLeg1SF*diTauLeg2SF
          self.out.trigweightVT[0]     = diTauLeg1SFVT*diTauLeg2SFVT
          if not self.doTight:
            diTauLeg1SFUp              = self.tauSFs.getTriggerSFUnc(self.out.pt_1[0],self.out.eta_1[0],self.out.phi_1[0],self.out.decayMode_1[0],self.out.genPartFlav_1[0], 'Up' )
            diTauLeg2SFUp              = self.tauSFs.getTriggerSFUnc(self.out.pt_2[0],self.out.eta_2[0],self.out.phi_2[0],self.out.decayMode_2[0],self.out.genPartFlav_2[0], 'Up' )
            diTauLeg1SFDown            = self.tauSFs.getTriggerSFUnc(self.out.pt_1[0],self.out.eta_1[0],self.out.phi_1[0],self.out.decayMode_1[0],self.out.genPartFlav_1[0], 'Down' )
            diTauLeg2SFDown            = self.tauSFs.getTriggerSFUnc(self.out.pt_2[0],self.out.eta_2[0],self.out.phi_2[0],self.out.decayMode_2[0],self.out.genPartFlav_2[0], 'Down' )
            self.out.trigweightUp[0]   = diTauLeg1SFUp*diTauLeg2SFUp
            self.out.trigweightDown[0] = diTauLeg1SFDown*diTauLeg2SFDown
          self.out.idisoweight_1[0]    = self.ltfSFs.getSF(self.out.genPartFlav_1[0],self.out.eta_1[0])
          self.out.idisoweight_2[0]    = self.ltfSFs.getSF(self.out.genPartFlav_2[0],self.out.eta_2[0])
          self.out.weight[0]           = self.out.genweight[0]*self.out.puweight[0]*self.out.trigweight[0]*self.out.idisoweight_1[0]*self.out.idisoweight_2[0]
        
        
        # MET & DILEPTON VARIABLES
        self.fillMETAndDiLeptonBranches(event,tau1,tau2,met,met_vars)
        
        
        self.out.tree.Fill() 
        return True
        
