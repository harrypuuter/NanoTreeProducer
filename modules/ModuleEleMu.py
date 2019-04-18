import sys
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from ModuleCommon import *
from TreeProducerEleMu import *
from CorrectionTools.MuonSFs import *
from CorrectionTools.ElectronSFs import *
from CorrectionTools.PileupWeightTool import *
from CorrectionTools.RecoilCorrectionTool import *
from CorrectionTools.BTaggingTool import BTagWeightTool, BTagWPs


class EleMuProducer(Module):

    def __init__(self, name, dataType, **kwargs):
        
        self.name             = name
        self.out              = TreeProducerEleMu(name,dataType)
        self.isData           = dataType=='data'
        self.year             = kwargs.get('year',       2017 )
        self.tes              = kwargs.get('tes',        1.0  )
        self.ltf              = kwargs.get('ltf',        1.0  )
        self.doZpt            = kwargs.get('doZpt',      'DY' in name )
        self.doRecoil         = kwargs.get('doRecoil',   ('DY' in name or re.search(r"W\d?Jets",name)) and self.year>2016)
        self.doTTpt           = kwargs.get('doTTpt',     'TT' in name )
        self.doTight          = kwargs.get('doTight',    self.tes!=1 or self.ltf!=1 )
        self.isVectorLQ       = kwargs.get('isVectorLQ', 'VectorLQ' in name )
        self.channel          = 'elemu'
        year, channel         = self.year, self.channel
        
        self.met              = getMET(year)
        self.filter           = getMETFilters(year,self.isData)
        if year==2016:
          self.trigger        = lambda e: e.HLT_IsoMu22 or e.HLT_IsoMu22_eta2p1 or e.HLT_IsoTkMu22 or e.HLT_IsoTkMu22_eta2p1 #or e.HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1
          self.muonCutPt      = lambda e: 23
        elif year==2017:
          self.trigger        = lambda e: e.HLT_IsoMu24 or e.HLT_IsoMu27 #or e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
          self.muonCutPt      = lambda e: 25 if e.HLT_IsoMu24 else 28
        else:
          self.trigger        = lambda e: e.HLT_IsoMu24 or e.HLT_IsoMu27 #or e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
          self.muonCutPt      = lambda e: 25
        self.eleCutPt         = 15
        self.jetCutPt         = 30
        
        if not self.isData:
          self.eleSFs         = ElectronSFs(year=year)
          self.muSFs          = MuonSFs(year=year)
          self.puTool         = PileupWeightTool(year=year)
          self.btagTool       = BTagWeightTool('DeepCSV','medium',channel=channel,year=year)
          self.btagTool_loose = BTagWeightTool('DeepCSV','loose',channel=channel,year=year)
          if self.doZpt:
            self.zptTool      = ZptCorrectionTool(year=year)
          if self.doRecoil:
            self.recoilTool   = RecoilCorrectionTool(year=year)
        self.deepcsv_wp       = BTagWPs('DeepCSV',year=year)
        
        self.Nocut = 0
        self.Trigger = 1
        self.GoodMuons = 2
        self.GoodElectrons = 3
        self.GoodDiLepton = 4
        self.TotalWeighted = 15
        self.TotalWeighted_no0PU = 16
        
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Nocut,               "no cut"                 )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Trigger,             "trigger"                )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodMuons,           "muon object"            )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodElectrons,       "electron object"        )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodDiLepton,        "mumu pair"              )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted,       "no cut, weighted"       )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted_no0PU, "no cut, weighted, PU>0" )
        self.out.cutflow.GetXaxis().SetLabelSize(0.041)
        
    def beginJob(self):
        pass
        
    def endJob(self):
        if not self.isData:
          self.btagTool.setDirectory(self.out.outputfile,'btag')
          self.btagTool_loose.setDirectory(self.out.outputfile,'btag')
        self.out.endJob()
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        sys.stdout.flush()
        checkBranches(inputTree)
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):        
        pass
        
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        sys.stdout.flush()
        
        #####################################
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
            if event.Muon_pt[imuon] < self.muonCutPt(event): continue
            if abs(event.Muon_eta[imuon]) > 2.4: continue
            if abs(event.Muon_dz[imuon]) > 0.2: continue
            if abs(event.Muon_dxy[imuon]) > 0.045: continue
            if not event.Muon_mediumId[imuon]: continue
            idx_goodmuons.append(imuon)
        
        if len(idx_goodmuons)==0:
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodMuons)
        #####################################
        
        
        idx_goodelectrons = [ ]
        for ielectron in range(event.nElectron):
            if event.Electron_pt[ielectron] < self.eleCutPt: continue
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
        
        
        muons     = Collection(event, 'Muon')
        electrons = Collection(event, 'Electron')
        dileptons = [ ]
        for idx1 in idx_goodelectrons:
          for idx2 in idx_goodmuons:
              if electrons[idx1].p4().DeltaR(muons[idx2].p4()) < 0.5: continue
              dilepton = DiLeptonBasicClass(idx1, event.Electron_pt[idx1], event.Electron_pfRelIso03_all[idx1], 
                                            idx2, event.Muon_pt[idx2],     event.Muon_pfRelIso04_all[idx2])
              dileptons.append(dilepton)
        
        if len(dileptons)==0:
            return False
        
        dilepton = bestDiLepton(dileptons)
        electron = electrons[dilepton.id1].p4()
        muon     = muons[dilepton.id2].p4()
        
        #####################################
        self.out.cutflow.Fill(self.GoodDiLepton)
        #####################################
        
        
        # VETOS
        self.out.extramuon_veto[0], self.out.extraelec_veto[0], self.out.dilepton_veto[0] = extraLeptonVetos(event, [dilepton.id2], [dilepton.id1], self.channel)
        self.out.lepton_vetos[0] = self.out.extramuon_veto[0] or self.out.extraelec_veto[0] or self.out.dilepton_veto[0]
        ###if self.doTight and (self.out.lepton_vetos[0] or event.Electron_pfRelIso03_all[dilepton.id1]>0.10 or\
        ###                     ord(event.Tau_idAntiMu[dilepton.id2]<1 or ord(event.Tau_idAntiEle[dilepton.id2]<8):
        ###  return False
        
        
        # EVENT
        self.out.isData[0]                = self.isData
        self.out.run[0]                   = event.run
        self.out.lumi[0]                  = event.luminosityBlock
        self.out.event[0]                 = event.event & 0xffffffffffffffff
        ###self.out.puppimet[0]             = event.PuppiMET_pt
        ###self.out.puppimetphi[0]          = event.PuppiMET_phi
        ###self.out.metsignificance[0]      = event.MET_significance
        ###self.out.metcovXX[0]             = event.MET_covXX
        ###self.out.metcovXY[0]             = event.MET_covXY
        ###self.out.metcovYY[0]             = event.MET_covYY
        self.out.npvs[0]                  = event.PV_npvs
        self.out.npvsGood[0]              = event.PV_npvsGood
        
        if not self.isData:
          self.out.genPartFlav_1[0]       = ord(event.Electron_genPartFlav[dilepton.id1])
          self.out.genPartFlav_2[0]       = ord(event.Muon_genPartFlav[dilepton.id2])
          self.out.genmet[0]              = event.GenMET_pt
          self.out.genmetphi[0]           = event.GenMET_phi
          self.out.nPU[0]                 = event.Pileup_nPU
          self.out.nTrueInt[0]            = event.Pileup_nTrueInt
          try:
            self.out.LHE_Njets[0]         = event.LHE_Njets
          except RuntimeError:
            self.out.LHE_Njets[0]         = -1
          
          if self.isVectorLQ:
            self.out.ntops[0] = countTops(event)
        
        
        # ELECTRON
        self.out.pt_1[0]                  = event.Electron_pt[dilepton.id1]
        self.out.eta_1[0]                 = event.Electron_eta[dilepton.id1]
        self.out.phi_1[0]                 = event.Electron_phi[dilepton.id1]
        self.out.m_1[0]                   = event.Electron_mass[dilepton.id1]
        self.out.dxy_1[0]                 = event.Electron_dxy[dilepton.id1]
        self.out.dz_1[0]                  = event.Electron_dz[dilepton.id1]
        self.out.q_1[0]                   = event.Electron_charge[dilepton.id1]
        self.out.pfRelIso03_all_1[0]      = event.Electron_pfRelIso03_all[dilepton.id1]
        self.out.cutBased_1[0]            = event.Electron_cutBased[dilepton.id1]
        self.out.mvaFall17Iso_WP90_1[0]   = event.Electron_mvaFall17V2Iso_WP90[dilepton.id1]
        self.out.mvaFall17Iso_WP80_1[0]   = event.Electron_mvaFall17V2Iso_WP80[dilepton.id1]
        self.out.mvaFall17noIso_WP90_1[0] = event.Electron_mvaFall17V2noIso_WP90[dilepton.id1]
        self.out.mvaFall17noIso_WP80_1[0] = event.Electron_mvaFall17V2noIso_WP80[dilepton.id1]
        
        
        # MUON
        self.out.pt_2[0]                  = event.Muon_pt[dilepton.id2]
        self.out.eta_2[0]                 = event.Muon_eta[dilepton.id2]
        self.out.phi_2[0]                 = event.Muon_phi[dilepton.id2]
        self.out.m_2[0]                   = event.Muon_mass[dilepton.id2]
        self.out.dxy_2[0]                 = event.Muon_dxy[dilepton.id2]
        self.out.dz_2[0]                  = event.Muon_dz[dilepton.id2]         
        self.out.q_2[0]                   = event.Muon_charge[dilepton.id2]
        self.out.pfRelIso04_all_2[0]      = event.Muon_pfRelIso04_all[dilepton.id2]
        
        
        # TAU for jet -> tau fake control region
        maxId = -1
        maxPt = 20
        taus  = Collection(event, 'Tau')
        for itau in range(event.nTau):
          if event.Tau_pt[itau] < maxPt: continue
          if electron.DeltaR(taus[itau].p4())<0.5: continue
          if muon.DeltaR(taus[itau].p4())<0.5: continue
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
          self.out.pt_3[0]                = event.Tau_pt[maxId]
          self.out.eta_3[0]               = event.Tau_eta[maxId]
          self.out.m_3[0]                 = event.Tau_mass[maxId]
          self.out.decayMode_3[0]         = event.Tau_decayMode[maxId]
          self.out.idAntiEle_3[0]         = ord(event.Tau_idAntiEle[maxId])
          self.out.idAntiMu_3[0]          = ord(event.Tau_idAntiMu[maxId])
          self.out.idMVAoldDM_3[0]        = ord(event.Tau_idMVAoldDM[maxId])
          self.out.idMVAoldDM2017v1_3[0]  = ord(event.Tau_idMVAoldDM2017v1[maxId])
          self.out.idMVAoldDM2017v2_3[0]  = ord(event.Tau_idMVAoldDM2017v2[maxId])
          self.out.idMVAnewDM2017v2_3[0]  = ord(event.Tau_idMVAnewDM2017v2[maxId])
          self.out.idIso_3[0]             = Tau_idIso(event,maxId)
          if not self.isData:
            self.out.genPartFlav_3[0]     = ord(event.Tau_genPartFlav[maxId])
        else:
          self.out.pt_3[0]                = -1
          self.out.eta_3[0]               = -9
          self.out.m_3[0]                 = -1
          self.out.decayMode_3[0]         = -1
          self.out.idAntiEle_3[0]         = -1
          self.out.idAntiMu_3[0]          = -1
          self.out.idMVAoldDM_3[0]        = -1
          self.out.idMVAoldDM2017v1_3[0]  = -1
          self.out.idMVAoldDM2017v2_3[0]  = -1
          self.out.idMVAnewDM2017v2_3[0]  = -1
          self.out.idIso_3[0]             = -1
          if not self.isData:
            self.out.genPartFlav_3[0]     = -1
        
        
        # JETS
        jetIds = fillJetsBranches(self,event,electron,muon)
        
        
        # WEIGHTS
        met = self.met(event)
        if not self.isData:
          if self.doRecoil:
            boson, boson_vis           = getBoson(event)
            self.recoilTool.CorrectPFMETByMeanResolution(met,boson,boson_vis,len(jetIds))
            self.out.m_genboson[0]     = boson.M()
            self.out.pt_genboson[0]    = boson.Pt()
            if self.doZpt:
              self.out.zptweight[0]    = self.zptTool.getZptWeight(boson.Pt(),boson.M())
          elif self.doZpt:
            zboson = getZBoson(event)
            self.out.m_genboson[0]     = zboson.M()
            self.out.pt_genboson[0]    = zboson.Pt()
            self.out.zptweight[0]      = self.zptTool.getZptWeight(zboson.Pt(),zboson.M())
          elif self.doTTpt:
            toppt1, toppt2             = getTTPt(event)
            self.out.ttptweight[0]     = getTTptWeight(toppt1,toppt2)
          if event.Electron_pfRelIso03_all[dilepton.id1]<0.50 and event.Muon_pfRelIso04_all[dilepton.id2]<0.50:
            self.btagTool.fillEfficiencies(event,jetIds)
            self.btagTool_loose.fillEfficiencies(event,jetIds)
          self.out.genweight[0]        = event.genWeight
          self.out.puweight[0]         = self.puTool.getWeight(event.Pileup_nTrueInt)
          self.out.trigweight[0]       = self.muSFs.getTriggerSF(self.out.pt_2[0],self.out.eta_2[0])
          self.out.idisoweight_1[0]    = self.eleSFs.getIdIsoSF(self.out.pt_1[0],self.out.eta_1[0])
          self.out.idisoweight_2[0]    = self.muSFs.getIdIsoSF(self.out.pt_2[0],self.out.eta_2[0])
          self.out.btagweight[0]       = self.btagTool.getWeight(event,jetIds)
          self.out.btagweight_loose[0] = self.btagTool_loose.getWeight(event,jetIds)
          self.out.weight[0]           = self.out.genweight[0]*self.out.puweight[0]*self.out.trigweight[0]*self.out.idisoweight_1[0]*self.out.idisoweight_2[0]
        
        
        # MET
        self.out.met[0]                = met.Pt()
        self.out.metphi[0]             = met.Phi()
        self.out.pfmt_1[0]             = sqrt( 2 * self.out.pt_1[0] * met.Pt() * ( 1 - cos(deltaPhi(self.out.phi_1[0], met.Phi())) ));
        self.out.pfmt_2[0]             = sqrt( 2 * self.out.pt_2[0] * met.Pt() * ( 1 - cos(deltaPhi(self.out.phi_2[0], met.Phi())) ));
        
        self.out.m_vis[0]              = (electron + muon).M()
        self.out.pt_ll[0]              = (electron + muon).Pt()
        self.out.dR_ll[0]              = electron.DeltaR(muon)
        self.out.dphi_ll[0]            = deltaPhi(self.out.phi_1[0], self.out.phi_2[0])
        self.out.deta_ll[0]            = abs(self.out.eta_1[0] - self.out.eta_2[0])
        
        
        # PZETA   
        leg1                           = TVector3(electron.Px(), electron.Py(), 0.)
        leg2                           = TVector3(muon.Px(), muon.Py(), 0.)
        zetaAxis                       = TVector3(leg1.Unit() + leg2.Unit()).Unit()
        pzeta_vis                      = leg1*zetaAxis + leg2*zetaAxis
        pzeta_miss                     = met.Vect()*zetaAxis
        self.out.pzetamiss[0]          = pzeta_miss
        self.out.pzetavis[0]           = pzeta_vis
        self.out.dzeta[0]              = pzeta_miss - 0.85*pzeta_vis
        
        
        self.out.tree.Fill() 
        return True
        
