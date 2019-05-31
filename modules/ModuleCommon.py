# Author: Izaak Neutelings (May 2019)
import sys, re
from math import sqrt, sin, cos, pi
from ROOT import TH1D, TH2D, TLorentzVector, TVector3
from ModuleTools import *
from corrections.PileupWeightTool import *
from corrections.RecoilCorrectionTool import *
from corrections.BTaggingTool import BTagWeightTool, BTagWPs
from corrections.JetMETCorrectionTool import JetMETCorrectionTool
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Event
__metaclass__ = type # to use super() with subclasses from CommonProducer


class CommonProducer(Module):
    
    def __init__(self, name, dataType, channel, **kwargs):
        
        # HEADER
        classname = self.__class__.__name__
        print '\n'
        print ' '*9+'#'*(len(classname)+8)
        print ' '*9+"#   %s   #"%(classname)
        print ' '*9+'#'*(len(classname)+8)+'\n'
        
        # SETTINGS
        self.name             = name
        self.isData           = dataType=='data'
        self.channel          = channel
        self.year             = kwargs.get('year',       2017 )
        self.era              = kwargs.get('era',        ""   )
        self.tes              = kwargs.get('tes',        1.0  )
        self.ltf              = kwargs.get('ltf',        1.0  )
        self.jtf              = kwargs.get('jtf',        1.0  )
        self.doTTpt           = kwargs.get('doTTpt',     'TT' in name       )
        self.doZpt            = kwargs.get('doZpt',      'DY' in name       )
        self.doRecoil         = kwargs.get('doRecoil',   ('DY' in name or re.search(r"W\d?Jets",name)) and self.year>2016)
        self.doTight          = kwargs.get('doTight',    self.tes!=1 or self.ltf!=1 or self.jtf!=1)
        self.doJEC            = kwargs.get('doJEC',      not self.doTight   ) #and False
        self.doJECSys         = kwargs.get('doJECSys',   self.doJEC         ) and not self.isData and self.doJEC #and False
        self.isVectorLQ       = kwargs.get('isVectorLQ', 'VectorLQ' in name )
        self.jetCutPt         = 30
        
        # YEAR-DEPENDENT IDs
        self.vlooseIso        = getVLooseTauIso(self.year)
        self.met, metbranch   = getMET(self.year)
        self.filter           = getMETFilters(self.year,self.isData)
        
        # CORRECTIONS
        self.jeclabels    = [ ]
        self.jecMETlabels = [ ]
        if not self.isData:
          self.puTool         = PileupWeightTool(year=self.year)
          self.btagTool       = BTagWeightTool('DeepCSV','medium',channel=channel,year=self.year)
          self.btagTool_loose = BTagWeightTool('DeepCSV','loose',channel=channel,year=self.year)
          if self.doZpt:
            self.zptTool      = ZptCorrectionTool(year=self.year)
          if self.doRecoil:
            self.recoilTool   = RecoilCorrectionTool(year=self.year)
          if self.doJEC:
            self.jmeTool      = JetMETCorrectionTool(self.year,jet='AK4PFchs',met=metbranch,systematics=self.doJECSys,updateEvent=False)
            if self.doJECSys:
              self.jeclabels    = [ u+v for u in ['jer','jes'] for v in ['Down','Up']]
              self.jecMETlabels = [ u+v for u in ['jer','jes','unclEn'] for v in ['Down','Up']]
        elif self.year in [2016,2017,2018]:
          self.jmeTool = JetMETCorrectionTool(self.year,jet='AK4PFchs',met=metbranch,systematics=self.doJECSys,updateEvent=False,data=True,era=self.era)
        else:
          self.doJEC = False
        self.deepcsv_wp       = BTagWPs('DeepCSV',year=self.year)
        
    
    def beginJob(self):
        print '-'*80
        print ">>> %-12s = '%s'"%('outputfile',self.name)
        print ">>> %-12s = '%s'"%('channel',   self.channel)
        print ">>> %-12s = %s"  %(  'isData',  self.isData)
        print ">>> %-12s = %s"  %('year',      self.year)
        print ">>> %-12s = '%s'"%('era',       self.era)
        print ">>> %-12s = %s"  %('tes',       self.tes)
        print ">>> %-12s = %s"  %('ltf',       self.ltf)
        print ">>> %-12s = %s"  %('jtf',       self.jtf)
        print ">>> %-12s = %s"  %('doTTpt',    self.doTTpt)
        print ">>> %-12s = %s"  %('doZpt',     self.doZpt)
        print ">>> %-12s = %s"  %('doRecoil',  self.doRecoil)
        print ">>> %-12s = %s"  %('doJEC',     self.doJEC)
        print ">>> %-12s = %s"  %('doJECSys',  self.doJECSys)
        print ">>> %-12s = %s"  %('isVectorLQ',self.isVectorLQ)
        print ">>> %-12s = %s"  %('doTight',   self.doTight)
        print ">>> %-12s = %s"  %('jetCutPt',  self.jetCutPt)
        pass
        
    
    def endJob(self):
        if not self.isData:
          self.btagTool.setDirectory(self.out.outputfile,'btag')
          self.btagTool_loose.setDirectory(self.out.outputfile,'btag')
          if self.doJEC:
            self.jmeTool.endJob()
        self.out.endJob()
        
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        sys.stdout.flush()
        checkBranches(inputTree,self.year)
        
    
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    
    def analyze(self, event):
        """Process event, return True (go to next module) or False (fail, go to next event)."""
        pass
        
    
    def fillEventBranches(self,event):
        """Help function to fill branches of common event variables."""
        
        # EVENT
        self.out.isData[0]          = self.isData
        self.out.run[0]             = event.run
        self.out.lumi[0]            = event.luminosityBlock
        self.out.event[0]           = event.event & 0xffffffffffffffff
        self.out.npvs[0]            = event.PV_npvs
        self.out.npvsGood[0]        = event.PV_npvsGood
        self.out.metfilter[0]       = self.filter(event)
        
        if not self.isData:
          ###self.out.ngentauhads[0]   = ngentauhads
          ###self.out.ngentaus[0]      = ngentaus
          self.out.genmet[0]        = event.GenMET_pt
          self.out.genmetphi[0]     = event.GenMET_phi
          self.out.nPU[0]           = event.Pileup_nPU
          self.out.nTrueInt[0]      = event.Pileup_nTrueInt
          try:
            self.out.LHE_Njets[0]   = event.LHE_Njets
          except RuntimeError:
            self.out.LHE_Njets[0]   = -1
          ###self.out.LHE_NpLO[0]      = event.LHE_NpLO
          ###self.out.LHE_NpNLO[0]     = event.LHE_NpNLO
          
          ###if self.isVectorLQ:
          ###  self.out.ntops[0]       = countTops(event)
          
    
    def fillJetBranches(self,event,tau1,tau2):
        """Help function to select jets and b tags, after removing overlap with tau decay candidates,
        and fill the jet variable branches."""
        #print '-'*80
        
        # GET JEC correction and uncertainty variations
        if self.doJEC:
          jetIds_vars = { }
          if self.isData:
            jetpt_nom, met_nom = self.jmeTool.correctJetMET_Data(event) # returns a list of jet pT and a MET TLorenzVector
            met_vars = { }
          else:
            jetpt_vars, met_vars = self.jmeTool.correctJetMET_MC(event) # returns a dict of jet pT lists and a dict of MET TLorenzVectors
            jetpt_nom,  met_nom  = jetpt_vars['nom'], met_vars['nom']
            for label in self.jeclabels:
              jetIds_vars[label] = [ ]
        else:
          jetpt_nom = [event.Jet_pt[i] for i in xrange(event.nJet)]
          met_nom   = self.met(event)
          met_vars  = { }
        
        # COUNTER
        jetIds, bjetIds = [ ], [ ]
        nfjets, ncjets  = 0, 0
        nbtag, nbtag50  = 0, 0
        nbtag_loose, nbtag50_loose = 0, 0
        
        # SELECT JET, remove overlap with selected objects
        jets = Collection(event,'Jet')
        #jets = filter(self.jetSel,jets)
        for ijet in xrange(event.nJet):
            #print event.Jet_pt[ijet], jetpt_vars['nom'][ijet]
            if abs(event.Jet_eta[ijet]) > 4.7: continue
            if tau1.DeltaR(jets[ijet].p4()) < 0.5: continue
            if tau2.DeltaR(jets[ijet].p4()) < 0.5: continue
            if event.Jet_jetId[ijet] < 2: continue
            
            if self.doJEC:
              for label in self.jeclabels:
                if jetpt_vars[label][ijet] < self.jetCutPt: continue
                jetIds_vars[label].append(ijet)
            if jetpt_nom[ijet] < self.jetCutPt: continue
            jetIds.append(ijet)
            
            if abs(event.Jet_eta[ijet]) > 2.4:
              nfjets += 1
            else:
              ncjets += 1
            
            if event.Jet_btagDeepB[ijet] > self.deepcsv_wp.loose:
              nbtag_loose += 1
              if jetpt_nom[ijet]>50:
                nbtag50_loose += 1
              if event.Jet_btagDeepB[ijet] > self.deepcsv_wp.medium:
                nbtag += 1
                if jetpt_nom[ijet]>50:
                  nbtag50 += 1
                bjetIds.append(ijet)
        
        ## TOTAL MOMENTUM
        #eventSum = TLorentzVector()
        #for lep in muons :
        #    eventSum += lep.p4()
        #for lep in electrons :
        #    eventSum += lep.p4()
        #for j in filter(self.jetSel,jets):
        #    eventSum += j.p4()
        
        # FILL JET BRANCHES
        self.out.njets[0]         = len(jetIds)
        self.out.njets50[0]       = len([i for i in jetIds if jetpt_nom>50])
        self.out.nfjets[0]        = nfjets
        self.out.ncjets[0]        = ncjets
        self.out.nbtag[0]         = nbtag
        self.out.nbtag50[0]       = nbtag50
        self.out.nbtag_loose[0]   = nbtag_loose
        self.out.nbtag50_loose[0] = nbtag50_loose
        
        # LEADING JET
        jetIds.sort(key=lambda i: jetpt_nom[i],reverse=True) # sort needed if JECs were applied
        if len(jetIds)>0:
          self.out.jpt_1[0]       = jetpt_nom[jetIds[0]]
          self.out.jeta_1[0]      = event.Jet_eta[jetIds[0]]
          self.out.jphi_1[0]      = event.Jet_phi[jetIds[0]]
          self.out.jdeepb_1[0]    = event.Jet_btagDeepB[jetIds[0]]
        else:
          self.out.jpt_1[0]       = -1.
          self.out.jeta_1[0]      = -9.
          self.out.jphi_1[0]      = -9.
          self.out.jdeepb_1[0]    = -9.
        
        # SUBLEADING JET
        if len(jetIds)>1:
          self.out.jpt_2[0]       = jetpt_nom[jetIds[1]]
          self.out.jeta_2[0]      = event.Jet_eta[jetIds[1]]
          self.out.jphi_2[0]      = event.Jet_phi[jetIds[1]]
          self.out.jdeepb_2[0]    = event.Jet_btagDeepB[jetIds[1]]
        else:
          self.out.jpt_2[0]       = -1.
          self.out.jeta_2[0]      = -9.
          self.out.jphi_2[0]      = -9.
          self.out.jdeepb_2[0]    = -9.
        
        # LEADING B JETS
        if len(bjetIds)>0:
          self.out.bpt_1[0]       = jetpt_nom[bjetIds[0]]
          self.out.beta_1[0]      = event.Jet_eta[bjetIds[0]]
        else:
          self.out.bpt_1[0]       = -1.
          self.out.beta_1[0]      = -9.
        
        # SUBLEADING B JETS
        if len(bjetIds)>1:
          self.out.bpt_2[0]       = jetpt_nom[bjetIds[1]]
          self.out.beta_2[0]      = event.Jet_eta[bjetIds[1]]
        else:
          self.out.bpt_2[0]       = -1.
          self.out.beta_2[0]      = -9.
        
        # FILL JET VARIATION BRANCHES
        njets_vars = { }
        if self.doJECSys:
          for label in self.jeclabels:
            jetIds_vars[label].sort(key=lambda i: jetpt_vars[label][i],reverse=True)
            njets_vars[label]    = len(jetIds_vars[label])
            jetIds_vars50        = [i for i in jetIds_vars[label]   if jetpt_vars[label][i]>50]
            bjetIds_vars50_loose = [i for i in jetIds_vars50        if event.Jet_btagDeepB[i] > self.deepcsv_wp.loose]
            bjetIds_vars50       = [i for i in bjetIds_vars50_loose if event.Jet_btagDeepB[i] > self.deepcsv_wp.medium]
            getattr(self.out,"njets_"+label)[0]   = njets_vars[label]
            getattr(self.out,"njets50_"+label)[0] = len(jetIds_vars50)
            getattr(self.out,"nbtag50_"+label)[0] = len(bjetIds_vars50)
            getattr(self.out,"nbtag50_loose_"+label)[0] = len(bjetIds_vars50_loose)
            getattr(self.out,"jpt_1_"+label)[0]   = jetpt_vars[label][jetIds_vars[label][0]] if len(jetIds_vars[label])>0 else -1
            getattr(self.out,"jpt_2_"+label)[0]   = jetpt_vars[label][jetIds_vars[label][1]] if len(jetIds_vars[label])>1 else -1
        
        return jetIds, met_nom, njets_vars, met_vars
        
    
    def applyCommonCorrections(self, event, jetIds, met, njets_var, met_vars):
        """Help function to apply common corrections, and fill weight branches."""
        
        if self.doRecoil:
          boson, boson_vis           = getBoson(event)
          self.recoilTool.CorrectPFMETByMeanResolution(met,boson,boson_vis,len(jetIds))
          self.out.m_genboson[0]     = boson.M()
          self.out.pt_genboson[0]    = boson.Pt()
          
          for label in self.jecMETlabels:
            self.recoilTool.CorrectPFMETByMeanResolution(met_vars[label],boson,boson_vis,njets_var.get(label,len(jetIds)))
          
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
        
        self.out.genweight[0]        = event.genWeight
        self.out.puweight[0]         = self.puTool.getWeight(event.Pileup_nTrueInt)
        self.out.btagweight[0]       = self.btagTool.getWeight(event,jetIds)
        self.out.btagweight_loose[0] = self.btagTool_loose.getWeight(event,jetIds)
        
    
    def fillMETAndDiLeptonBranches(self, event, tau1, tau2, met, met_vars):
        """Help function to compute variable related to the MET and visible tau candidates,
        and fill the corresponding branches."""
        
        # MET
        self.out.met[0]       = met.Pt()
        self.out.metphi[0]    = met.Phi()
        self.out.pfmt_1[0]    = sqrt( 2 * self.out.pt_1[0] * met.Pt() * ( 1 - cos(deltaPhi(self.out.phi_1[0], met.Phi())) ))
        self.out.pfmt_2[0]    = sqrt( 2 * self.out.pt_2[0] * met.Pt() * ( 1 - cos(deltaPhi(self.out.phi_2[0], met.Phi())) ))
        ###self.out.puppimetpt[0]             = event.PuppiMET_pt
        ###self.out.puppimetphi[0]            = event.PuppiMET_phi
        ###self.out.metsignificance[0]        = event.MET_significance
        ###self.out.metcovXX[0]               = event.MET_covXX
        ###self.out.metcovXY[0]               = event.MET_covXY
        ###self.out.metcovYY[0]               = event.MET_covYY
        ###self.out.fixedGridRhoFastjetAll[0] = event.fixedGridRhoFastjetAll
        
        # PZETA
        leg1                  = TVector3(tau1.Px(), tau1.Py(), 0.)
        leg2                  = TVector3(tau2.Px(), tau2.Py(), 0.)
        zetaAxis              = TVector3(leg1.Unit() + leg2.Unit()).Unit()
        pzeta_vis             = leg1*zetaAxis + leg2*zetaAxis
        pzeta_miss            = met.Vect()*zetaAxis
        self.out.pzetamiss[0] = pzeta_miss
        self.out.pzetavis[0]  = pzeta_vis
        self.out.dzeta[0]     = pzeta_miss - 0.85*pzeta_vis
        
        # MET SYSTEMATICS
        for label in self.jecMETlabels:
          met_var = met_vars[label]
          getattr(self.out,"met_"+label)[0]    = met_var.Pt()
          getattr(self.out,"pfmt_1_"+label)[0] = sqrt( 2 * self.out.pt_1[0] * met_var.Pt() * ( 1 - cos(deltaPhi(self.out.phi_1[0], met_var.Phi())) ))
          getattr(self.out,"dzeta_"+label)[0]  = met_var.Vect()*zetaAxis - 0.85*pzeta_vis
        
        # DILEPTON
        self.out.m_vis[0]     = (tau1 + tau2).M()
        self.out.pt_ll[0]     = (tau1 + tau2).Pt()
        self.out.dR_ll[0]     = tau1.DeltaR(tau2)
        self.out.dphi_ll[0]   = deltaPhi(self.out.phi_1[0], self.out.phi_2[0])
        self.out.deta_ll[0]   = abs(self.out.eta_1[0] - self.out.eta_2[0])
        


