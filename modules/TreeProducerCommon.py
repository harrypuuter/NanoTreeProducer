import numpy as num
from ROOT import TTree, TFile, TH1D, TH2D

root_dtype = {
  float: 'D',  int: 'I',  bool: 'O',
  'f':   'D',  'i': 'I',  '?':  'O',  'b': 'b',
  'F':   'D',  'I': 'I',  'B':  'O',
}

num_dtype = {
  'D':   'f',  'I': 'i',  'O':  '?',  'b': 'b'
}


class TreeProducerCommon(object):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, dataType, **kwargs):
        print 'TreeProducerCommon is called', name
        
        self.name       = name
        self._isData    = dataType=='data'
        self.doJECSys   = kwargs.get('doJECSys', True ) and not self._isData
        ###self.isVectorLQ = kwargs.get('isVectorLQ', 'VectorLQ' in self.name )
        
        # TREE
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        
        # HISTOGRAM
        self.cutflow = TH1D('cutflow', 'cutflow',  25, 0,  25)
        self.pileup  = TH1D('pileup',  'pileup',  100, 0, 100)
        
        #### CHECK genPartFlav
        ###self.flags_LTF_DM1 = TH1D('flags_LTF_DM1', "flags for l #rightarrow #tau_{h}, DM1", 18, 0, 18)
        ###self.flags_LTF_DM0 = TH1D('flags_LTF_DM0', "flags for l #rightarrow #tau_{h}, DM0", 18, 0, 18)
        ###self.flags_LTF_mis = TH1D('flags_LTF_mis', "flags for l #rightarrow #tau_{h}, DM1, wrong genPartFlav", 18, 0, 18)
        ###self.flags_LTF_DM1_sn1 = TH1D('flags_LTF_DM1_sn1', "flags for l #rightarrow #tau_{h}, DM1 (status!=1)", 18, 0, 18)
        ###self.flags_LTF_DM0_sn1 = TH1D('flags_LTF_DM0_sn1', "flags for l #rightarrow #tau_{h}, DM0 (status!=1)", 18, 0, 18)
        ###self.flags_LTF_mis_sn1 = TH1D('flags_LTF_mis_sn1', "flags for l #rightarrow #tau_{h}, DM1, wrong genPartFlav (status!=1)", 18, 0, 18)
        ###for hist in [self.flags_LTF_DM1, self.flags_LTF_DM0, self.flags_LTF_mis, self.flags_LTF_DM0_sn1, self.flags_LTF_DM1_sn1, self.flags_LTF_mis_sn1]:
        ###  hist.GetXaxis().SetBinLabel( 1,  "isPrompt"                            )
        ###  hist.GetXaxis().SetBinLabel( 2,  "isDirectPromptTauDecayProduct"       )
        ###  hist.GetXaxis().SetBinLabel( 3,  "isHardProcess"                       )
        ###  hist.GetXaxis().SetBinLabel( 4,  "fromHardProcess"                     )
        ###  hist.GetXaxis().SetBinLabel( 5,  "isDirectHardProcessTauDecayProduct"  )
        ###  hist.GetXaxis().SetBinLabel( 6,  "fromHardProcessBeforeFSR"            )
        ###  hist.GetXaxis().SetBinLabel( 7,  "isFirstCopy"                         )
        ###  hist.GetXaxis().SetBinLabel( 8,  "isLastCopy"                          )
        ###  hist.GetXaxis().SetBinLabel( 9,  "isLastCopyBeforeFSR"                 )
        ###  hist.GetXaxis().SetBinLabel(10,  "status==1"                           )
        ###  hist.GetXaxis().SetBinLabel(11,  "status==23"                          )
        ###  hist.GetXaxis().SetBinLabel(12,  "status==44"                          )
        ###  hist.GetXaxis().SetBinLabel(13,  "status==51"                          )
        ###  hist.GetXaxis().SetBinLabel(14,  "status==52"                          )
        ###  hist.GetXaxis().SetBinLabel(15,  "other status"                        )
        ###  hist.GetXaxis().SetLabelSize(0.041)
        ###self.genmatch_corr     = TH2D("genmatch_corr","correlation between Tau_genPartFlav and genmatch",6,0,6,6,0,6)
        ###self.genmatch_corr_DM0 = TH2D("genmatch_corr_DM0","correlation between Tau_genPartFlav and genmatch for DM0",6,0,6,6,0,6)
        ###self.genmatch_corr_DM1 = TH2D("genmatch_corr_DM1","correlation between Tau_genPartFlav and genmatch for DM1",6,0,6,6,0,6)
        
        
        #############
        #   EVENT   #
        #############
        
        self.addBranch('run',                     'I')
        self.addBranch('lumi',                    'I')
        self.addBranch('event',                   'I')
        self.addBranch('isData',                  '?', self._isData)
        
        self.addBranch('npvs',                    'I')
        self.addBranch('npvsGood',                'I')
        self.addBranch('metfilter',               '?')
        
        if not self._isData:
          self.addBranch('nPU',                   'I', -1)
          self.addBranch('nTrueInt',              'I', -1)
          self.addBranch('LHE_Njets',             'I', -1)
        
        
        ##############
        #   WEIGHT   #
        ##############
        
        if not self._isData:
          self.addBranch('weight',                'F', 1.)
          self.addBranch('genweight',             'F', 1.)
          self.addBranch('trigweight',            'F', 1.)
          self.addBranch('puweight',              'F', 1.)
          self.addBranch('idisoweight_1',         'F', 1.)
          self.addBranch('idisoweight_2',         'F', 1.)
          self.addBranch('zptweight',             'F', 1.)
          self.addBranch('ttptweight',            'F', 1.)
          self.addBranch('btagweight',            'F', 1.)
          self.addBranch('btagweight_loose',      'F', 1.)
        
        
        ############
        #   JETS   #
        ############
        
        self.addBranch('njets',                   'I')
        self.addBranch('njets50',                 'I')
        self.addBranch('ncjets',                  'I')
        self.addBranch('nfjets',                  'I')
        self.addBranch('nbtag',                   'I')
        self.addBranch('nbtag50',                 'I')
        self.addBranch('nbtag_loose',             'I')
        self.addBranch('nbtag50_loose',           'I')
        
        self.addBranch('jpt_1',                   'F')
        self.addBranch('jeta_1',                  'F')
        self.addBranch('jphi_1',                  'F')
        self.addBranch('jdeepb_1',                'F')
        self.addBranch('jpt_2',                   'F')
        self.addBranch('jeta_2',                  'F')
        self.addBranch('jphi_2',                  'F')
        self.addBranch('jdeepb_2',                'F')
        
        self.addBranch('bpt_1',                   'F')
        self.addBranch('beta_1',                  'F')
        self.addBranch('bpt_2',                   'F')
        self.addBranch('beta_2',                  'F')
        
        if self.doJECSys:
          for uncertainty in ['jer','jes']:
            for variation in ['Down','Up']:
              label = '_'+uncertainty+variation
              self.addBranch('njets'+label,         'I')
              self.addBranch('njets50'+label,       'I')
              self.addBranch('nbtag50'+label,       'I')
              self.addBranch('nbtag50_loose'+label, 'I')
              self.addBranch('jpt_1'+label,         'F')
              self.addBranch('jpt_2'+label,         'F')
        
        self.addBranch('met',                     'F')
        self.addBranch('metphi',                  'F')
        ###self.addBranch('puppimet',                'F')
        ###self.addBranch('puppimetphi',             'F')
        ###self.addBranch('metsignificance',         'F')
        ###self.addBranch('metcovXX',                'F')
        ###self.addBranch('metcovXY',                'F')
        ###self.addBranch('metcovYY',                'F')
        ###self.addBranch('fixedGridRhoFastjetAll',  'F')
        if not self._isData:
          self.addBranch('genmet',                'F', -1)
          self.addBranch('genmetphi',             'F', -9)
        
        
        #############
        #   OTHER   #
        #############
        
        self.addBranch('pfmt_1',                  'F')
        self.addBranch('pfmt_2',                  'F')
        self.addBranch('m_vis',                   'F')
        self.addBranch('pt_ll',                   'F')
        self.addBranch('dR_ll',                   'F')
        self.addBranch('dphi_ll',                 'F')
        self.addBranch('deta_ll',                 'F')
        
        self.addBranch('pzetamiss',               'F')
        self.addBranch('pzetavis',                'F')
        self.addBranch('dzeta',                   'F')
        
        if self.doJECSys:
          for uncertainty in ['jer','jes','unclEn']:
            for variation in ['Down','Up']:
              label = '_'+uncertainty+variation
              self.addBranch('met'+label,         'F')
              self.addBranch('pfmt_1'+label,      'F')
              self.addBranch('dzeta'+label,       'F')
        
        self.addBranch('dilepton_veto',           '?')
        self.addBranch('extraelec_veto',          '?')
        self.addBranch('extramuon_veto',          '?')
        self.addBranch('lepton_vetos',            '?')
        
        if not self._isData:
          ###self.addBranch('ngentauhads',           'I', -1)
          ###self.addBranch('ngentaus',              'I', -1)
          self.addBranch('m_genboson',            'F', -1)
          self.addBranch('pt_genboson',           'F', -1)
          ###if self.isVectorLQ:
          ###  self.addBranch('ntops',               'I', -1)
        
        ###self.addBranch('m_taub',                  'F')
        ###self.addBranch('m_taumub',                'F')
        ###self.addBranch('m_tauj',                  'F')
        ###self.addBranch('m_muj',                   'F')
        ###self.addBranch('m_coll_muj',              'F')
        ###self.addBranch('m_coll_tauj',             'F')
        ###self.addBranch('mt_coll_muj',             'F')
        ###self.addBranch('mt_coll_tauj',            'F')
        ###self.addBranch('m_max_lj',                'F')
        ###self.addBranch('m_max_lb',                'F')
        ###self.addBranch('m_mub',                   'F')
        
    
    def addBranch(self, name, dtype='F', default=None):
        """Add branch with a given name, and create an array of the same name as address."""
        if hasattr(self,name):
          print "ERROR! TreeProducerCommon.addBranch: Branch of name '%s' already exists!"%(name)
          exit(1)
        setattr(self,name,num.zeros(1,dtype=dtype))
        self.tree.Branch(name, getattr(self,name), '%s/%s'%(name,root_dtype[dtype]))
        if default!=None:
          getattr(self,name)[0] = default
        
    
    def endJob(self):
        """Write and close files after the job ends."""
        self.outputfile.Write()
        self.outputfile.Close()
        

