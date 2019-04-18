# Author: Izaak Neutelings (November 2018)
# 2016: https://github.com/rmanzoni/triggerSF/tree/moriond17
# 2017: https://github.com/truggles/TauTriggerSFs/tree/final_2017_MCv2
import os
from math import sqrt, pi
from CorrectionTools import modulepath, ensureTFile, extractTH1
from ROOT import TMath
path = modulepath+"/tauEfficiencies/"
        


class TauTriggerSFs(object):
    
    def __new__(self,*args,**kwargs):
        if kwargs.get('year',0)==2016:
          return TauTriggerSFs2016(*args,**kwargs) #TauTriggerSFs2016.__new__(*args,**kwargs)
        return object.__new__(TauTriggerSFs)
    
    def __init__(self, trigger, wp='medium', id='MVAv2', year=2016):
        """Load tau trigger histograms from files."""
        print "Loading TauTriggerSFs for %s (%s WP)..."%(trigger,wp)
        
        trigger = trigger.replace('tautau','ditau').replace('eletau','etau')
        assert(trigger in ['ditau', 'mutau', 'etau']), "Choose from: 'ditau', 'mutau', 'etau' triggers."
        assert(wp in ['vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']), "You must choose a WP from: vloose, loose, medium, tight, vtight, or vvtight"
        assert(id in ['MVAv2', 'dR0p3']), "Choose from two provided ID types: 'MVAv2', 'dR0p3'. 'MVAv2' uses dR0p5, and 'dR0p3' is also an MVA-based ID."
        assert(id=='MVAv2'), "Tau POG is currently only providing efficiencies for MVAv2, sorry."
        assert(year in [2016,2017,2018]), "You must choose a year from: 2016, 2017, or 2018."
        print "Loading Efficiencies for trigger %s usingTau %s ID WP %s for year %i"%(trigger,id,wp,year)
        
        # Assume this is in CMSSW with the below path structure
        if year==2018: year = 2017
        file = ensureTFile( path+'%d/tauTriggerEfficiencies%i.root'%(year,year), 'r' )
        
        self.fit_data = { }
        self.fit_mc   = { }
        self.fitUnc_data = { }
        self.fitUnc_mc   = { }
        self.effEtaPhi_data = { }
        self.effEtaPhi_mc   = { }
        self.effEtaPhiAvg_data = { }
        self.effEtaPhiAvg_mc   = { }
        for dm in [0,1,10]:
          
          # Load the TF1s containing the analytic best-fit results.
          self.fit_data[dm] = extractTH1(file,'%s_%s%s_dm%d_DATA_fit'%(trigger,wp,id,dm))
          self.fit_mc[dm]   = extractTH1(file,'%s_%s%s_dm%d_MC_fit'%(  trigger,wp,id,dm))
          
          # Load the TH1s containing the analytic best-fit result in 1 GeV incriments and the associated uncertainty.
          self.fitUnc_data[dm] = extractTH1(file,'%s_%s%s_dm%d_DATA_errorBand'%(trigger,wp,id,dm))
          self.fitUnc_mc[dm]   = extractTH1(file,'%s_%s%s_dm%d_MC_errorBand'%(  trigger,wp,id,dm))
          
          # Load the TH2s containing the eta phi efficiency corrections
          self.effEtaPhi_data[dm] = extractTH1(file,'%s_%s%s_dm%d_DATA'%(trigger,wp,id,dm))
          self.effEtaPhi_mc[dm]   = extractTH1(file,'%s_%s%s_dm%d_MC'%(  trigger,wp,id,dm))
          
          # Eta Phi Averages
          self.effEtaPhiAvg_data[dm] = extractTH1(file,'%s_%s%s_dm%d_DATA_AVG'%(trigger,wp,id,dm))
          self.effEtaPhiAvg_mc[dm]   = extractTH1(file,'%s_%s%s_dm%d_MC_AVG'%(  trigger,wp,id,dm))
        
        file.Close()
        
        self.trigger = trigger
        self.year = year
        self.wp = wp
        self.id = id
        
    
    def ptCheck( self, pt ):
        """Make sure we stay on our histograms."""
        if pt > 450:  pt = 450
        elif pt < 20: pt = 20
        return pt
        
    def dmCheck( self, dm ):
        """Make sure to have only old DMs, DM0, DM1, DM10"""
        if dm==2:  dm = 1  # Originally, DM=2 was included in oldDM, but with the dynamic strip clustering the second strip was reconstructed together with the first one. So it ends up to DM=1. But, there are still some cases where DM=2 survives.
        if dm==11: dm = 10
        return dm
        
    def getEfficiency( self, pt, eta, phi, fit, uncHist, etaPhiHist, etaPhiAvgHist, uncert='Nominal' ):
        pt = self.ptCheck(pt)
        eff = fit.Eval(pt)
        
        # Shift the pt dependent efficiency by the fit uncertainty if requested
        if uncert != 'Nominal':
            assert( uncert in ['Up', 'Down'] ), "Uncertainties are provided using 'Up'/'Down'"
            if uncert == 'Up':
                eff += uncHist.GetBinError( uncHist.FindBin(pt) )
            else: # must be Down
                eff -= uncHist.GetBinError( uncHist.FindBin(pt) )
        
        # Adjust SF based on (eta, phi) location
        # keep eta barrel boundaries within SF region
        # but, for taus outside eta limits or with unralistic
        # phi values, return zero SF
        if eta == 2.1:    eta = 2.09
        elif eta == -2.1: eta = -2.09
        
        etaPhiVal = etaPhiHist.GetBinContent( etaPhiHist.FindBin( eta, phi ) )
        etaPhiAvg = etaPhiAvgHist.GetBinContent( etaPhiAvgHist.FindBin( eta, phi ) )
        if etaPhiAvg <= 0.0:
            print "One of the provided tau (eta, phi) values (%3.3f, %3.3f) is outside the boundary of triggering taus" % (eta, phi)
            print "Returning efficiency = 0.0"
            return 0.0
        eff *= etaPhiVal / etaPhiAvg
        if eff > 1.: eff = 1.
        if eff < 0.: eff = 0. # Some efficiency fits go negative at very low tau pT, prevent that.
        return eff
        
    
    def getTriggerEfficiencyData(self, pt, eta, phi, dm):
        """Return the data efficiency or the +/- 1 sigma uncertainty shifted efficiency."""
        dm = self.dmCheck(dm)
        assert(dm in [0,1,10]), "Efficiencies only provided for DMs 0, 1, 10. You provided DM %i" % dm
        return self.getEfficiency(pt,eta,phi,self.fit_data[dm],self.fitUnc_data[dm], \
                                  self.effEtaPhi_data[dm], self.effEtaPhiAvg_data[dm])
        
    def getTriggerEfficiencyDataUncertUp(self, pt, eta, phi, dm):
        dm = self.dmCheck(dm)
        assert(dm in [0,1,10]), "Efficiencies only provided for DMs 0, 1, 10. You provided DM %i" % dm
        return self.getEfficiency(pt,eta,phi,self.fit_data[dm],self.fitUnc_data[dm], \
                                  self.effEtaPhi_data[dm], self.effEtaPhiAvg_data[dm], 'Up')
        
    def getTriggerEfficiencyDataUncertDown(self, pt, eta, phi, dm):
        dm = self.dmCheck(dm)
        assert(dm in [0,1,10]), "Efficiencies only provided for DMs 0, 1, 10. You provided DM %i" % dm
        return self.getEfficiency(pt,eta,phi,self.fit_data[dm],self.fitUnc_data[dm], \
                                  self.effEtaPhi_data[dm], self.effEtaPhiAvg_data[dm], 'Down')
        
    
    def getTriggerEfficiencyMC(self, pt, eta, phi, dm):
        """Return the MC efficiency or the +/- 1 sigma uncertainty shifted efficiency."""
        dm = self.dmCheck(dm)
        assert(dm in [0,1,10]), "Efficiencies only provided for DMs 0, 1, 10. You provided DM %i" % dm
        return self.getEfficiency(pt,eta,phi,self.fit_mc[dm],self.fitUnc_mc[dm], \
                                  self.effEtaPhi_mc[dm], self.effEtaPhiAvg_mc[dm])
        
    def getTriggerEfficiencyMCUncertUp(self, pt, eta, phi, dm):
        dm = self.dmCheck(dm)
        assert(dm in [0,1,10]), "Efficiencies only provided for DMs 0, 1, 10. You provided DM %i" % dm
        return self.getEfficiency(pt,eta,phi,self.fit_mc[dm],self.fitUnc_mc[dm], \
                                  self.effEtaPhi_mc[dm], self.effEtaPhiAvg_mc[dm], 'Up')
        
    def getTriggerEfficiencyMCUncertDown(self, pt, eta, phi, dm):
        dm = self.dmCheck(dm)
        assert(dm in [0,1,10]), "Efficiencies only provided for DMs 0, 1, 10. You provided DM %i" % dm
        return self.getEfficiency(pt,eta,phi,self.fit_mc[dm],self.fitUnc_mc[dm], \
                                  self.effEtaPhi_mc[dm], self.effEtaPhiAvg_mc[dm], 'Down')
        
    
    def getTriggerSF(self, pt, eta, phi, dm, genmatch=5):
        """Return the data/MC scale factor."""
        pt = self.ptCheck(pt)
        dm = self.dmCheck(dm)
        effData = self.getTriggerEfficiencyData( pt, eta, phi, dm )
        effMC = self.getTriggerEfficiencyMC( pt, eta, phi, dm )
        if effMC < 1e-5:
            print "Eff MC is suspiciously low. Please contact Tau POG."
            print " - %s Trigger SF for Tau ID: %s   WP: %s   pT: %f   eta: %s   phi: %f" % (self.trigger, self.id, self.wp, pt, eta, phi)
            print " - MC Efficiency = %f" % effMC
            return 0.0
        sf = effData / effMC
        return sf
        
    
    # return the data/MC scale factor with +1/-1 sigma uncertainty.
    # Data and MC fit uncertainties are treated as uncorrelated.
    # The calculated uncertainties are symmetric. Do error propagation
    # for simple division. Using getTriggerEfficiencyXXXUncertDown instead
    # of Up ensures we have the full uncertainty reported. Up sometimes
    # is clipped by efficiency max of 1.0.
    def getTriggerScaleFactorUncert( self, pt, eta, phi, dm, uncert ):
        assert( uncert in ['Up', 'Down'] ), "Uncertainties are provided using 'Up'/'Down'"
        pt = self.ptCheck(pt)
        dm = self.dmCheck(dm)
        effData = self.getTriggerEfficiencyData( pt, eta, phi, dm )
        effDataDown = self.getTriggerEfficiencyDataUncertDown( pt, eta, phi, dm )
        relDataDiff = (effData - effDataDown) / effData
        
        effMC = self.getTriggerEfficiencyMC( pt, eta, phi, dm )
        effMCDown = self.getTriggerEfficiencyMCUncertDown( pt, eta, phi, dm )
        if effMC < 1e-5:
            # already printed an error for the nominal case...
            return 0.0
        relMCDiff = (effMC - effMCDown) / effMC
        
        deltaSF = sqrt( relDataDiff**2 + relMCDiff**2 )
        sf = (effData / effMC)
        if uncert == 'Up':
            return sf * (1. + deltaSF)
        else: # must be Down
            return sf * (1. - deltaSF)
    


class TauTriggerSFs2016():
    
    def __init__(self, trigger='tautau', wp='medium', id='MVAv2', year=2016):
        """Load histograms from files."""
        print "Loading TauTriggerSFs2016 for %s (%s WP)..."%(trigger,wp)
        
        trigger = trigger.replace('tautau','ditau').replace('eletau','etau')
        assert(trigger in ['ditau', 'mutau', 'etau'] ), "Choose from: 'ditau', 'mutau', 'etau' triggers."
        assert(wp in ['vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight'] ), "You must choose a WP from: vloose, loose, medium, tight, vtight, or vvtight"
        assert(year==2016), "TauTriggerSFs2016 is only implemented for 2016."
        wp = wp.replace('v','V').replace('loose','Loose').replace('medium','Medium').replace('tight','Tight')
        
        import json
        filename = path+"%s/ditau/fitresults_tt_moriond2017.json"%(year)
        with open(filename) as file:
          data = json.load(file)
          self.fitFake_data = { }
          self.fitFake_mc   = { }
          self.fitReal_data = { }
          self.fitReal_mc   = { }
          for dm in [0,1,10]:
            self.fitReal_data[dm] = CrystallBallEfficiency(data['data_genuine_%sIso_dm%d'%(wp,dm)])
            self.fitFake_data[dm] = CrystallBallEfficiency(data['data_fake_%sIso_dm%d'%(wp,dm)])
            self.fitReal_mc[dm]   = CrystallBallEfficiency(data['mc_genuine_%sIso_dm%d'%(wp,dm)])
            self.fitFake_mc[dm]   = CrystallBallEfficiency(data['mc_fake_%sIso_dm%d'%(wp,dm)])
        
        self.trigger  = trigger
        self.year     = year
        self.wp    = wp
        self.filename = file
        
    
    def getTriggerSF(self, pt, eta, phi, dm, genmatch=5):
        """Return the data/MC scale factor."""
        if genmatch==5:
          sf = self.fitReal_data[dm].eval(pt)/self.fitReal_mc[dm].eval(pt)
        else:
          sf = self.fitFake_data[dm].eval(pt)/self.fitFake_mc[dm].eval(pt)
        return sf
    


class CrystallBallEfficiency:
    """Convolution between crystal ball and step function."""
    
    def __init__(self, params):
        # https://github.com/rmanzoni/triggertools/blob/master/objects/FitFunctions.py#L153
        
        alpha = params['alpha']
        sigma = params['sigma']
        norm  = params['norm']
        m0    = params['m_{0}']
        n     = params['n']
        
        sqrtPi2  = sqrt(pi/2)
        sqrt2    = sqrt(2.)
        absSig   = abs(sigma)
        absAlpha = abs(alpha/absSig)
        a        = (n/absAlpha)**n * TMath.Exp(-0.5 * absAlpha * absAlpha)
        b        = absAlpha - n/absAlpha
        arg      = absAlpha / sqrt2;
        erf      = 1 if arg>5. else -1 if arg<-5. else  TMath.Erf(arg)
        
        leftArea  = (1. + erf) * sqrtPi2
        rightArea = ( a * 1./(absAlpha-b)**(n-1)) / (n-1)
        area      = leftArea + rightArea
        
        self.norm      = norm
        self.alpha     = alpha
        self.sigma     = sigma
        self.m0        = m0
        self.nm1       = n-1
        self.absAlpha  = absAlpha
        self.b         = b
        self.sqrt2     = sqrt2
        self.norm1     = norm*sqrtPi2/area
        self.norm2     = norm*a/(1-n)/area
        self.sigma1    = absSig * alpha / abs(alpha)
        self.A         = norm*leftArea/area - self.norm2/(absAlpha-b)**self.nm1
        
    def eval(self,x):
        t = (x - self.m0)/self.sigma1
        if t <= self.absAlpha:
          arg = t / self.sqrt2
          erf = 1 if arg>5. else -1 if arg<-5. else TMath.Erf(arg)
          return self.norm1 * (1 + erf)
        else:
          return self.A + self.norm2/(t-self.b)**self.nm1
    


# class CrystallBall:
#     
#     def __init__(self, params):
#         # https://github.com/rmanzoni/triggertools/blob/master/objects/FitFunctions.py#L119
#         # https://en.wikipedia.org/wiki/Crystal_Ball_function
#         alpha = params['alpha']
#         sigma = params['sigma']
#         norm  = params['norm']
#         mu    = params['m_{0}']
#         n     = params['n']
#         gauss = TMath.Exp(-0.5*abs(alpha)**2.))
#         A = (n/abs(alpha))**n * gauss
#         B = n / abs(alpha) - abs(alpha)
#         C = n / (abs(alpha) * (n - 1.)) * gauss
#         D = sqrt(pi/2.) * (1. + TMath.Erf(abs(alpha)/sqrt(2.))) 
#         N = 1. / (sigma * (C + D))
#         self.norm  = N * norm
#         self.alpha = alpha
#         self.sigma = sigma
#         self.mu    = mu
#         self.n     = n
#         self.A     = A
#         self.B     = B
#         
#     def eval(self,x):
#         pull = (x-self.mu)/self.sigma
#         if pull>-self.alpha:
#           return self.norm * TMath.Gaus(x,self.mu,self.sigma)
#         else:
#           return self.norm * self.A * (self.B-pull)**(-self.n)
    

