import sys
from ModuleCommon import *
from TreeProducerMuMu import *
from corrections.MuonSFs import *


class MuMuProducer(CommonProducer):
    
    def __init__(self, name, dataType, **kwargs):
        
        super(MuMuProducer,self).__init__(name,dataType,'mumu',**kwargs)
        self.out = TreeProducerMuMu(name,dataType,doJECSys=self.doJECSys)
        self.inZmassWindow = kwargs.get('ZmassWindow', True )
        
        # TRIGGERS
        if self.year==2016:
          self.trigger     = lambda e: e.HLT_IsoMu22 or e.HLT_IsoMu22_eta2p1 or e.HLT_IsoTkMu22 or e.HLT_IsoTkMu22_eta2p1 #or e.HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1
          self.muon1CutPt  = lambda e: 23
        elif self.year==2017:
          self.trigger     = lambda e: e.HLT_IsoMu24 or e.HLT_IsoMu27 #or e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
          self.muon1CutPt  = lambda e: 25 if e.HLT_IsoMu24 else 28
        else:
          self.trigger     = lambda e: e.HLT_IsoMu24 or e.HLT_IsoMu27 #or e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
          self.muon1CutPt  = lambda e: 25
        self.muon2CutPt    = 15
        self.jetCutPt      = 20 # override for tau -> j fake measurement
        
        # CORRECTIONS
        if not self.isData:
          self.muSFs      = MuonSFs(year=self.year)
        
        # CUTFLOW
        self.Nocut = 0
        self.Trigger = 1
        self.GoodMuons = 2
        self.GoodSecondMuon = 3
        self.GoodDiLepton = 4
        self.TotalWeighted = 15
        self.TotalWeighted_no0PU = 16
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Nocut,               "no cut"                 )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Trigger,             "trigger"                )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodMuons,           "muon object"            )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodSecondMuon,      "second muon object"     )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodDiLepton,        "mumu pair"              )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted,       "no cut, weighted"       )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted_no0PU, "no cut, weighted, PU>0" )
        self.out.cutflow.GetXaxis().SetLabelSize(0.041)
        #self.out.zpt = TH1D('Zpt', 'Zpt', 100, 0, 100)
        #self.out.zpt.SetDirectory(self.out.outputfile)
        
    
    def beginJob(self):
        super(MuMuProducer,self).beginJob()
        print ">>> %-12s = %s"%('muon1CutPt', self.muon1CutPt)
        print ">>> %-12s = %s"%('muon2CutPt', self.muon2CutPt)
        print ">>> %-12s = %s"%('inZmassWindow', self.inZmassWindow)
        pass
        
    
    def analyze(self, event):
        """Process and select events; fill branches and return True if the events passes,
        return False otherwise."""
        sys.stdout.flush()
        
        #zboson = getZBoson(event)
        #self.out.zpt.Fill(zboson.Pt())
        #return False
        
        
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
        #####################################
        
        
        idx_goodmuons = [ ]
        for imuon in range(event.nMuon):
            if event.Muon_pt[imuon] < self.muon2CutPt: continue # lower pT cut
            if abs(event.Muon_eta[imuon]) > 2.4: continue
            if abs(event.Muon_dz[imuon]) > 0.2: continue
            if abs(event.Muon_dxy[imuon]) > 0.045: continue
            if event.Muon_pfRelIso04_all[imuon] > 0.15: continue
            if not event.Muon_mediumId[imuon]: continue
            idx_goodmuons.append(imuon)
        
        if len(idx_goodmuons) < 1:
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodMuons)
        #####################################
        
        
        if not any(event.Muon_pt[i]>self.muon1CutPt(event) for i in idx_goodmuons) or len(idx_goodmuons)<2: # higher pT cut
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodSecondMuon)
        #####################################
        
        
        muons = Collection(event, 'Muon')
        dileptons = [ ]
        for idx1 in idx_goodmuons:
          for idx2 in idx_goodmuons:
              if idx1 >= idx2: continue
              muon1 = muons[idx1].p4()
              muon2 = muons[idx2].p4()
              if muon1.DeltaR(muon2) < 0.5: continue
              if self.inZmassWindow and not (70<(muon1+muon2).M()<110): continue # Z mass
              dilepton = DiLeptonBasicClass(idx1, event.Muon_pt[idx1], event.Muon_pfRelIso04_all[idx1], 
                                            idx2, event.Muon_pt[idx2], event.Muon_pfRelIso04_all[idx2])
              dileptons.append(dilepton)
        
        if len(dileptons)==0:
            return False
        
        dilepton = bestDiLepton(dileptons)
        muon1    = muons[dilepton.id1].p4()
        muon2    = muons[dilepton.id2].p4()
        
        #####################################
        self.out.cutflow.Fill(self.GoodDiLepton)
        #####################################
        
        
        # VETOS
        self.out.extramuon_veto[0], self.out.extraelec_veto[0], self.out.dilepton_veto[0] = extraLeptonVetos(event, [dilepton.id1, dilepton.id2], [-1], self.channel)
        self.out.lepton_vetos[0] = self.out.extramuon_veto[0] or self.out.extraelec_veto[0] or self.out.dilepton_veto[0]
        
        
        # EVENT
        self.out.isData[0]               = self.isData
        self.out.run[0]                  = event.run
        self.out.lumi[0]                 = event.luminosityBlock
        self.out.event[0]                = event.event & 0xffffffffffffffff
        ###self.out.puppimet[0]            = event.PuppiMET_pt
        ###self.out.puppimetphi[0]         = event.PuppiMET_phi
        ###self.out.metsignificance[0]     = event.MET_significance
        ###self.out.metcovXX[0]            = event.MET_covXX
        ###self.out.metcovXY[0]            = event.MET_covXY
        ###self.out.metcovYY[0]            = event.MET_covYY
        self.out.npvs[0]                 = event.PV_npvs
        self.out.npvsGood[0]             = event.PV_npvsGood
        self.out.metfilter[0]            = self.filter(event)
        
        if not self.isData:
          self.out.genPartFlav_1[0]      = ord(event.Muon_genPartFlav[dilepton.id1])
          self.out.genPartFlav_2[0]      = ord(event.Muon_genPartFlav[dilepton.id2])
          self.out.genmet[0]             = event.GenMET_pt
          self.out.genmetphi[0]          = event.GenMET_phi
          self.out.nPU[0]                = event.Pileup_nPU
          self.out.nTrueInt[0]           = event.Pileup_nTrueInt
          try:
            self.out.LHE_Njets[0]        = event.LHE_Njets
          except RuntimeError:
            self.out.LHE_Njets[0]        = -1
          
          if self.isVectorLQ:
            self.out.ntops[0] = countTops(event)
        
        
        # MUON 1
        self.out.pt_1[0]                 = event.Muon_pt[dilepton.id1]
        self.out.eta_1[0]                = event.Muon_eta[dilepton.id1]
        self.out.phi_1[0]                = event.Muon_phi[dilepton.id1]
        self.out.m_1[0]                  = event.Muon_mass[dilepton.id1]
        self.out.dxy_1[0]                = event.Muon_dxy[dilepton.id1]
        self.out.dz_1[0]                 = event.Muon_dz[dilepton.id1]         
        self.out.q_1[0]                  = event.Muon_charge[dilepton.id1]
        self.out.pfRelIso04_all_1[0]     = event.Muon_pfRelIso04_all[dilepton.id1]
        
        
        # MUON 2
        self.out.pt_2[0]                 = event.Muon_pt[dilepton.id2]
        self.out.eta_2[0]                = event.Muon_eta[dilepton.id2]
        self.out.phi_2[0]                = event.Muon_phi[dilepton.id2]
        self.out.m_2[0]                  = event.Muon_mass[dilepton.id2]
        self.out.dxy_2[0]                = event.Muon_dxy[dilepton.id2]
        self.out.dz_2[0]                 = event.Muon_dz[dilepton.id2]         
        self.out.q_2[0]                  = event.Muon_charge[dilepton.id2]
        self.out.pfRelIso04_all_2[0]     = event.Muon_pfRelIso04_all[dilepton.id2]
        
        
        # TAU for jet -> tau fake rate measurement
        maxId = -1
        maxPt = 20
        taus  = Collection(event, 'Tau')
        for itau in range(event.nTau):
          if event.Tau_pt[itau] < maxPt: continue
          if muon1.DeltaR(taus[itau].p4())<0.5: continue
          if muon2.DeltaR(taus[itau].p4())<0.5: continue
          if abs(event.Tau_eta[itau])>2.3: continue
          if abs(event.Tau_dz[itau])>0.2: continue
          if event.Tau_decayMode[itau] not in [0,1,10,11]: continue
          if abs(event.Tau_charge[itau])!=1: continue
          if ord(event.Tau_idAntiEle[itau])<1: continue # VLoose
          if ord(event.Tau_idAntiMu[itau])<1: continue # Loose
          #if not self.vlooseIso(event,itau): continue
          maxId = itau
          maxPt = event.Tau_pt[itau]
        if maxId>-1:
          self.out.pt_3[0]               = event.Tau_pt[maxId]
          self.out.eta_3[0]              = event.Tau_eta[maxId]
          self.out.m_3[0]                = event.Tau_mass[maxId]
          self.out.decayMode_3[0]        = event.Tau_decayMode[maxId]
          self.out.idAntiEle_3[0]        = ord(event.Tau_idAntiEle[maxId])
          self.out.idAntiMu_3[0]         = ord(event.Tau_idAntiMu[maxId])
          self.out.idMVAoldDM_3[0]       = ord(event.Tau_idMVAoldDM[maxId])
          self.out.idMVAoldDM2017v1_3[0] = ord(event.Tau_idMVAoldDM2017v1[maxId])
          self.out.idMVAoldDM2017v2_3[0] = ord(event.Tau_idMVAoldDM2017v2[maxId])
          self.out.idMVAnewDM2017v2_3[0] = ord(event.Tau_idMVAnewDM2017v2[maxId])
          self.out.idIso_3[0]            = Tau_idIso(event,maxId)
          if not self.isData:
            self.out.genPartFlav_3[0]    = genmatch(event,maxId) #ord(event.Tau_genPartFlav[maxId])
        else:
          self.out.pt_3[0]               = -1
          self.out.eta_3[0]              = -9
          self.out.m_3[0]                = -1
          self.out.decayMode_3[0]        = -1
          self.out.idAntiEle_3[0]        = -1
          self.out.idAntiMu_3[0]         = -1
          self.out.idMVAoldDM_3[0]       = -1
          self.out.idMVAoldDM2017v1_3[0] = -1
          self.out.idMVAoldDM2017v2_3[0] = -1
          self.out.idMVAnewDM2017v2_3[0] = -1
          self.out.idIso_3[0]            = -1
          if not self.isData:
            self.out.genPartFlav_3[0]    = -1
        
        
        # JETS
        jetIds, met, njets_var, met_vars = self.fillJetBranches(event,muon1,muon2)
        
        
        # WEIGHTS
        if not self.isData:
          self.applyCommonCorrections(event,jetIds,met,njets_var,met_vars)
          if event.Muon_pfRelIso04_all[dilepton.id1]<0.50 and event.Muon_pfRelIso04_all[dilepton.id2]<0.50:
            self.btagTool.fillEfficiencies(event,jetIds)
            self.btagTool_loose.fillEfficiencies(event,jetIds)
          self.out.trigweight[0]         = self.muSFs.getTriggerSF(self.out.pt_1[0],self.out.eta_1[0])
          self.out.idisoweight_1[0]      = self.muSFs.getIdIsoSF(self.out.pt_1[0],self.out.eta_1[0])
          self.out.idisoweight_2[0]      = self.muSFs.getIdIsoSF(self.out.pt_2[0],self.out.eta_2[0])
          self.out.weight[0]             = self.out.genweight[0]*self.out.puweight[0]*self.out.trigweight[0]*self.out.idisoweight_1[0]*self.out.idisoweight_2[0]
        
        
        # MET & DILEPTON VARIABLES
        self.fillMETAndDiLeptonBranches(event,muon1,muon2,met,met_vars)
        
        
        self.out.tree.Fill() 
        return True
        
