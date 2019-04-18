import numpy as num
from ROOT import TTree, TFile, TH1D, TH2D


root_dtype = {
  float: 'D',  int: 'I',  bool: 'O',
  'f':   'D',  'i': 'I',  '?':  'O',  'b': 'b'
}
num_dtype = {
  'D':   'f',  'I': 'i',  'O':  '?',  'b': 'b'
}

class TreeProducerCommon(object):
    
    def __init__(self, name, dataType, **kwargs):
        
        print 'TreeProducerCommon is called', name
        self.name       = name
        self._isData    = dataType=='data'
        self.isVectorLQ = kwargs.get('isVectorLQ', 'VectorLQ' in self.name)
        
        # TREE
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        
        # HISTOGRAM
        self.cutflow = TH1D('cutflow', 'cutflow',  25, 0,  25)
        self.pileup  = TH1D('pileup',  'pileup',  100, 0, 100)
        
        ## CHECK genPartFlav
        #self.flags_LTF_DM1 = TH1D('flags_LTF_DM1', "flags for l #rightarrow #tau_{h}, DM1", 18, 0, 18)
        #self.flags_LTF_DM0 = TH1D('flags_LTF_DM0', "flags for l #rightarrow #tau_{h}, DM0", 18, 0, 18)
        #self.flags_LTF_mis = TH1D('flags_LTF_mis', "flags for l #rightarrow #tau_{h}, DM1, wrong genPartFlav", 18, 0, 18)
        #self.flags_LTF_DM1_sn1 = TH1D('flags_LTF_DM1_sn1', "flags for l #rightarrow #tau_{h}, DM1 (status!=1)", 18, 0, 18)
        #self.flags_LTF_DM0_sn1 = TH1D('flags_LTF_DM0_sn1', "flags for l #rightarrow #tau_{h}, DM0 (status!=1)", 18, 0, 18)
        #self.flags_LTF_mis_sn1 = TH1D('flags_LTF_mis_sn1', "flags for l #rightarrow #tau_{h}, DM1, wrong genPartFlav (status!=1)", 18, 0, 18)
        #for hist in [self.flags_LTF_DM1, self.flags_LTF_DM0, self.flags_LTF_mis, self.flags_LTF_DM0_sn1, self.flags_LTF_DM1_sn1, self.flags_LTF_mis_sn1]:
        #  hist.GetXaxis().SetBinLabel( 1,  "isPrompt"                            )
        #  hist.GetXaxis().SetBinLabel( 2,  "isDirectPromptTauDecayProduct"       )
        #  hist.GetXaxis().SetBinLabel( 3,  "isHardProcess"                       )
        #  hist.GetXaxis().SetBinLabel( 4,  "fromHardProcess"                     )
        #  hist.GetXaxis().SetBinLabel( 5,  "isDirectHardProcessTauDecayProduct"  )
        #  hist.GetXaxis().SetBinLabel( 6,  "fromHardProcessBeforeFSR"            )
        #  hist.GetXaxis().SetBinLabel( 7,  "isFirstCopy"                         )
        #  hist.GetXaxis().SetBinLabel( 8,  "isLastCopy"                          )
        #  hist.GetXaxis().SetBinLabel( 9,  "isLastCopyBeforeFSR"                 )
        #  hist.GetXaxis().SetBinLabel(10,  "status==1"                           )
        #  hist.GetXaxis().SetBinLabel(11,  "status==23"                          )
        #  hist.GetXaxis().SetBinLabel(12,  "status==44"                          )
        #  hist.GetXaxis().SetBinLabel(13,  "status==51"                          )
        #  hist.GetXaxis().SetBinLabel(14,  "status==52"                          )
        #  hist.GetXaxis().SetBinLabel(15,  "other status"                        )
        #  hist.GetXaxis().SetLabelSize(0.041)
        #self.genmatch_corr     = TH2D("genmatch_corr","correlation between Tau_genPartFlav and genmatch",6,0,6,6,0,6)
        #self.genmatch_corr_DM0 = TH2D("genmatch_corr_DM0","correlation between Tau_genPartFlav and genmatch for DM0",6,0,6,6,0,6)
        #self.genmatch_corr_DM1 = TH2D("genmatch_corr_DM1","correlation between Tau_genPartFlav and genmatch for DM1",6,0,6,6,0,6)
        
        
        #############
        #   EVENT   #
        #############
        
        self.addBranch('run',                     int)
        self.addBranch('lumi',                    int)
        self.addBranch('event',                   int)
        self.addBranch('isData',                  bool, self._isData)
        
        self.addBranch('npvs',                    int)
        self.addBranch('npvsGood',                int)
        self.addBranch('metfilter',               bool)
        
        if not self._isData:
          self.addBranch('nPU',                   int, -1)
          self.addBranch('nTrueInt',              int, -1)
          self.addBranch('LHE_Njets',             int, -1)
        
        
        ##############
        #   WEIGHT   #
        ##############
        
        if not self._isData:
          self.addBranch('weight',                float, 1.)
          self.addBranch('genweight',             float, 1.)
          self.addBranch('trigweight',            float, 1.)
          self.addBranch('puweight',              float, 1.)
          self.addBranch('idisoweight_1',         float, 1.)
          self.addBranch('idisoweight_2',         float, 1.)
          self.addBranch('zptweight',             float, 1.)
          self.addBranch('ttptweight',            float, 1.)
          self.addBranch('btagweight',            float, 1.)
          self.addBranch('btagweight_loose',      float, 1.)
        
        
        ############
        #   JETS   #
        ############
        
        self.addBranch('njets',                   int)
        self.addBranch('njets50',                 int)
        self.addBranch('ncjets',                  int)
        self.addBranch('nfjets',                  int)
        self.addBranch('nbtag',                   int)
        self.addBranch('nbtag50',                 int)
        self.addBranch('nbtag_loose',             int)
        self.addBranch('nbtag50_loose',           int)
        
        self.addBranch('jpt_1',                   float)
        self.addBranch('jeta_1',                  float)
        self.addBranch('jphi_1',                  float)
        self.addBranch('jdeepb_1',                float)
        self.addBranch('jpt_2',                   float)
        self.addBranch('jeta_2',                  float)
        self.addBranch('jphi_2',                  float)
        self.addBranch('jdeepb_2',                float)
        
        self.addBranch('bpt_1',                   float)
        self.addBranch('beta_1',                  float)
        self.addBranch('bpt_2',                   float)
        self.addBranch('beta_2',                  float)
        
        self.addBranch('met',                     float)
        self.addBranch('metphi',                  float)
        ###self.addBranch('puppimet',                float)
        ###self.addBranch('puppimetphi',             float)
        ###self.addBranch('metsignificance',         float)
        ###self.addBranch('metcovXX',                float)
        ###self.addBranch('metcovXY',                float)
        ###self.addBranch('metcovYY',                float)
        ###self.addBranch('fixedGridRhoFastjetAll',  float)
        if not self._isData:
          self.addBranch('genmet',                float, -1)
          self.addBranch('genmetphi',             float, -9)
        
        
        #############
        #   OTHER   #
        #############
        
        self.addBranch('pfmt_1',                  float)
        self.addBranch('pfmt_2',                  float)
        self.addBranch('m_vis',                   float)
        self.addBranch('pt_ll',                   float)
        self.addBranch('dR_ll',                   float)
        self.addBranch('dphi_ll',                 float)
        self.addBranch('deta_ll',                 float)
        
        self.addBranch('pzetamiss',               float)
        self.addBranch('pzetavis',                float)
        self.addBranch('dzeta',                   float)
        
        self.addBranch('dilepton_veto',           bool)
        self.addBranch('extraelec_veto',          bool)
        self.addBranch('extramuon_veto',          bool)
        self.addBranch('lepton_vetos',            bool)
        
        if not self._isData:
          self.addBranch('ngentauhads',           int,   -1)
          self.addBranch('ngentaus',              int,   -1)
          self.addBranch('m_genboson',            float, -1)
          self.addBranch('pt_genboson',           float, -1)
          if self.isVectorLQ:
            self.addBranch('ntops',               int,   -1)
        
        #self.addBranch('m_taub',                  float)
        #self.addBranch('m_taumub',                float)
        #self.addBranch('m_tauj',                  float)
        #self.addBranch('m_muj',                   float)
        #self.addBranch('m_coll_muj',              float)
        #self.addBranch('m_coll_tauj',             float)
        #self.addBranch('mt_coll_muj',             float)
        #self.addBranch('mt_coll_tauj',            float)
        #self.addBranch('m_max_lj',                float)
        #self.addBranch('m_max_lb',                float)
        #self.addBranch('m_mub',                   float)
        
    
    def addBranch(self, name, dtype=float, default=None):
        """Add branch with a given name, and create an array of the same name as address."""
        if hasattr(self,name):
          print "ERROR! TreeProducerCommon.addBranch: Branch of name '%s' already exists!"%(name)
          exit(1)
        setattr(self,name,num.zeros(1,dtype=dtype))
        self.tree.Branch(name, getattr(self,name), '%s/%s'%(name,root_dtype[dtype]))
        if default!=None:
          getattr(self,name)[0] = default
        
    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()
    

