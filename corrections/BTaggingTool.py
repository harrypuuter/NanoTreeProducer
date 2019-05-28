# Author: Izaak Neutelings (January 2019)
# https://twiki.cern.ch/twiki/bin/view/CMS/BTagSFMethods
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/BTagCalibration
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation80XReReco
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
from corrections import modulepath, ensureTFile, warning
from array import array
import ROOT
#ROOT.gROOT.ProcessLine('.L ./BTagCalibrationStandalone.cpp+')
from ROOT import TH2F, BTagCalibration, BTagCalibrationReader
from ROOT.BTagEntry import OP_LOOSE, OP_MEDIUM, OP_TIGHT, OP_RESHAPING
from ROOT.BTagEntry import FLAV_B, FLAV_C, FLAV_UDSG
path = modulepath+"/btag/"


class BTagWPs:
  """Contain b tagging working points."""
  def __init__( self, tagger, year=2017 ):
    assert( year in [2016,2017,2018] ), "You must choose a year from: 2016, 2017, or 2018."
    if year==2016:
      if 'deep' in tagger.lower():
        self.loose    = 0.2217 # 0.2219 for 2016ReReco vs. 2016Legacy
        self.medium   = 0.6321 # 0.6324
        self.tight    = 0.8953 # 0.8958
      else:
        self.loose    = 0.5426 # for 80X ReReco
        self.medium   = 0.8484
        self.tight    = 0.9535
    elif year==2017:
      if 'deep' in tagger.lower():
        self.loose    = 0.1522 # for 94X
        self.medium   = 0.4941
        self.tight    = 0.8001
      else:
        self.loose    = 0.5803 # for 94X
        self.medium   = 0.8838
        self.tight    = 0.9693
    elif year==2018:
      if 'deep' in tagger.lower():
        self.loose    = 0.1241 # for 102X
        self.medium   = 0.4184
        self.tight    = 0.7527
      else:
        self.loose    = 0.5803 # for 94X
        self.medium   = 0.8838
        self.tight    = 0.9693
  

class BTagWeightTool:
    
    def __init__(self, tagger, wp='medium', sigma='central', channel='mutau', year=2017):
        """Load b tag weights from CSV file."""
        
        assert(year in [2016,2017,2018]), "You must choose a year from: 2016, 2017, or 2018."
        assert(tagger in ['CSVv2','DeepCSV']), "BTagWeightTool: You must choose a tagger from: CSVv2, DeepCSV!"
        assert(wp in ['loose','medium','tight']), "BTagWeightTool: You must choose a WP from: loose, medium, tight!"
        assert(sigma in ['central','up','down']), "BTagWeightTool: You must choose a WP from: central, up, down!"
        #assert(channel in ['mutau','eletau','tautau','mumu']), "BTagWeightTool: You must choose a channel from: mutau, eletau, tautau, mumu!"
        
        # FILE
        if year==2016:
          if 'deep' in tagger.lower():
            csvname = path+'DeepCSV_Moriond17_B_H.csv'
            effname = path+'DeepCSV_2016_Moriond17_eff.root'
          else:
            csvname = path+'CSVv2_Moriond17_B_H.csv'
            effname = path+'CSVv2_2016_Moriond17_eff.root'
        elif year==2017:
          if 'deep' in tagger.lower():
            csvname = path+'DeepCSV_94XSF_V3_B_F.csv'
            effname = path+'DeepCSV_2017_12Apr2017_eff.root'
          else:
            csvname = path+'CSVv2_94XSF_V2_B_F.csv'
            effname = path+'CSVv2_2017_12Apr2017_eff.root'
        elif year==2018:
          if 'deep' in tagger.lower():
            csvname = path+'DeepCSV_94XSF_V3_B_F.csv'
            effname = path+'DeepCSV_2018_Autumn18_eff.root'
          else:
            csvname = path+'CSVv2_94XSF_V2_B_F.csv'
            effname = path+'CSVv2_2018_Autumn18_eff.root'
        
        # TAGGING WP
        self.wpname = wp
        self.wp     = getattr(BTagWPs(tagger,year),wp)
        if 'deep' in tagger.lower():
          tagged = lambda e,i: e.Jet_btagDeepB[i]>self.wp
        else:
          tagged = lambda e,i: e.Jet_btagCSVV2[i]>self.wp
        
        # CSV READER
        print "Loading BTagWeightTool for %s (%s WP)..."%(tagger,wp)
        op        = OP_LOOSE if wp=='loose' else OP_MEDIUM if wp=='medium' else OP_TIGHT if wp=='tight' else OP_RESHAPING
        type_udsg = 'incl'
        type_bc   = 'comb' # 'mujets' for QCD; 'comb' for QCD+TT
        calib     = BTagCalibration(tagger, csvname)
        reader    = BTagCalibrationReader(op, sigma)
        reader.load(calib, FLAV_B, type_bc)
        reader.load(calib, FLAV_C, type_bc)
        reader.load(calib, FLAV_UDSG, type_udsg)
        
        # EFFICIENCIES
        hists      = { } # histograms to compute the b tagging efficiencies in MC
        effmaps    = { } # b tag efficiencies in MC to compute b tagging weight for an event
        efffile    = ensureTFile(effname)
        default    = False
        if not efffile:
          warning("File %s with efficiency histograms does not exist! Reverting to default efficiency histogram..."%(effname),title="BTagWeightTool")
          default  = True
        for flavor in [0,4,5]:
          flavor   = flavorToString(flavor)
          histname = "%s_%s_%s"%(tagger,flavor,wp)
          effname  = "%s/eff_%s_%s_%s"%(channel,tagger,flavor,wp)
          hists[flavor]        = createEfficienyMap(histname)        # numerator   = b tagged jets
          hists[flavor+'_all'] = createEfficienyMap(histname+'_all') # denominator = all jets
          if efffile:
            effmaps[flavor]    = efffile.Get(effname)
            if not effmaps[flavor]:
              warning("histogram '%s' does not exist in %s! Reverting to default efficiency histogram..."%(effname,efffile.GetName()),title="BTagWeightTool")
              default          = True
              effmaps[flavor]  = createDefaultEfficiencyMap(effname,flavor,wp)
          else:
            effmaps[flavor]    = createDefaultEfficiencyMap(effname,flavor,wp)
          effmaps[flavor].SetDirectory(0)
        efffile.Close()
        
        if default:
          warning("Made use of default efficiency histograms! The b tag weights from this module should be regarded as placeholders only,\n"+\
                  "and should NOT be used for analyses. B (mis)tag efficiencies in MC are analysis dependent. Please create your own\n"+\
                  "efficiency histogram with corrections/btag/getBTagEfficiencies.py after running all MC samples with BTagWeightTool.",title="BTagWeightTool")
        
        self.tagged  = tagged
        self.calib   = calib
        self.reader  = reader
        self.hists   = hists
        self.effmaps = effmaps
        
    def getWeight(self,event,jetids):
        """Get b tagging event weight for a given set of jets."""
        weight = 1.
        for id in jetids:
          weight *= self.getSF(event.Jet_pt[id],event.Jet_eta[id],event.Jet_partonFlavour[id],self.tagged(event,id))
        return weight
        
    def getSF(self,pt,eta,flavor,tagged):
        """Get b tag SF for a single jet."""
        FLAV = flavorToFLAV(flavor)
        SF   = self.reader.eval(FLAV,abs(eta),pt)
        if tagged:
          weight = SF
        else:
          eff = self.getEfficiency(pt,eta,flavor)
          if eff==1:
            print "Warning! BTagWeightTool.getSF: MC efficiency is 1 for pt=%s, eta=%s, flavor=%s, SF=%s"%(pt,eta,flavor,SF)
            return 1
          else:
            weight = (1-SF*eff)/(1-eff)
        return weight
        
    def getEfficiency(self,pt,eta,flavor):
        """Get b tag efficiency for a single jet in MC."""
        flavor = flavorToString(flavor)
        hist   = self.effmaps[flavor]
        xbin   = hist.GetXaxis().FindBin(pt)
        ybin   = hist.GetYaxis().FindBin(eta)
        if xbin==0: xbin = 1
        elif xbin>hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>hist.GetYaxis().GetNbins(): ybin -= 1
        eff    = hist.GetBinContent(xbin,ybin)
        #if eff==1:
        #  print "Warning! BTagWeightTool.getEfficiency: MC efficiency is 1 for pt=%s, eta=%s, flavor=%s, SF=%s"%(pt,eta,flavor,SF)
        return eff
        
    def fillEfficiencies(self,event,jetids):
        """Fill histograms to make efficiency map for MC, split by true jet flavor, and
        jet pT and eta. Numerator = b tagged jets; denominator = all jets."""
        for id in jetids:
          flavor = flavorToString(event.Jet_partonFlavour[id])
          if self.tagged(event,id):
            self.hists[flavor].Fill(event.Jet_pt[id],event.Jet_eta[id])
          self.hists[flavor+'_all'].Fill(event.Jet_pt[id],event.Jet_eta[id])
            
    def setDirectory(self,directory,subdirname=None):
        """Set directory of histograms before writing."""
        if subdirname:
          subdir = directory.Get(subdirname)
          if not subdir:
            subdir = directory.mkdir(subdirname)
          directory = subdir
        for histname, hist in self.hists.iteritems():
          hist.SetDirectory(directory)
     


def flavorToFLAV(flavor):
  """Help function to convert an integer flavor ID to a BTagEntry enum value."""
  return FLAV_B if abs(flavor)==5 else FLAV_C if abs(flavor) in [4,15] else FLAV_UDSG       
  
def flavorToString(flavor):
  """Help function to convert an integer flavor ID to a string value."""
  return 'b' if abs(flavor)==5 else 'c' if abs(flavor)==4 else 'udsg'
  
def createEfficienyMap(histname):
    """Help function to create efficiency maps (TH2D) with uniform binning and layout.
    One method to rule them all."""
    ptbins  = array('d',[10,20,30,50,70,100,140,200,300,500,1000,1500])
    etabins = array('d',[-2.5,-1.5,0.0,1.5,2.5])
    bins    = (len(ptbins)-1,ptbins,len(etabins)-1,etabins)
    hist    = TH2F(histname,histname,*bins)
    hist.GetXaxis().SetTitle("jet p_{T} [GeV]")
    hist.GetYaxis().SetTitle("jet #eta")
    hist.SetDirectory(0)
    return hist
    
def createDefaultEfficiencyMap(histname,flavor,wp='medium'):
    """Create default efficiency histograms. WARNING! Do not use for analysis! Use it as a placeholder,
    until you have made an efficiency map from MC for you analysis."""
    if   wp=='loose':  eff = 0.75 if flavor=='b' else 0.11 if flavor=='c' else 0.01
    elif wp=='medium': eff = 0.85 if flavor=='b' else 0.42 if flavor=='c' else 0.10
    else:              eff = 0.60 if flavor=='b' else 0.05 if flavor=='c' else 0.001
    histname = histname.split('/')[-1] + "_default"
    hist     = createEfficienyMap(histname)
    for xbin in xrange(0,hist.GetXaxis().GetNbins()+2):
      for ybin in xrange(0,hist.GetYaxis().GetNbins()+2):
        hist.SetBinContent(xbin,ybin,eff)
    return hist
    

