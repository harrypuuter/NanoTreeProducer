#! /usr/bin/env python
# Author: Izaak Neutelings (January 2019)

import os, sys
from argparse import ArgumentParser
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gStyle, gROOT, TFile, TTree, TH2F, TCanvas, kRed
gStyle.SetOptStat(False)
gROOT.SetBatch(True)

argv = sys.argv
description = '''This script extracts histograms from the analysis framework output run on MC samples to create b tag efficiencies.'''
parser = ArgumentParser(prog="pileup",description=description,epilog="Succes!")
parser.add_argument('-y', '--year',    dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                       help="year to run" )
parser.add_argument('-c', '--channel', dest='channels', choices=['eletau','mutau','tautau','elemu','mumu'], type=str, nargs='+', default=['mutau'], action='store',
                                       help="channels to run" )
parser.add_argument('-t', '--tagger',  dest='taggers', choices=['CSVv2','DeepCSV'], type=str, nargs='+', default=['DeepCSV'], action='store',
                                       help="tagger to run" )
parser.add_argument('-w', '--wp',      dest='wps', choices=['loose','medium','tight'], type=str, nargs='+', default=['medium'], action='store',
                                       help="working point to run" )
parser.add_argument('-p', '--plot',    dest="plot", default=False, action='store_true', 
                                       help="plot efficiencies" )
parser.add_argument('-v', '--verbose', dest="verbose", default=False, action='store_true', 
                                       help="print verbose" )
args = parser.parse_args()



def getBTagEfficiencies(tagger,wp,outfilename,samples,year,channel,plot=False):
    """Get pileup profile in MC by adding Pileup_nTrueInt histograms from a given list of samples."""
    print ">>> getBTagEfficiencies(%s)"%(outfilename)
    
    # PREPARE numerator and denominator histograms per flavor
    nhists  = { }
    hists   = { }
    histdir = 'btag'
    for flavor in ['b','c','udsg']:
      histname = '%s_%s_%s'%(tagger,flavor,wp)
      hists[histname] = None
      hists[histname+'_all'] = None
    
    # ADD numerator and denominator histograms
    for filename in samples:
      print ">>>   %s"%(filename)
      file = TFile(filename,'READ')
      if not file or file.IsZombie():
        print ">>>   Warning! getBTagEfficiencies: Could not open %s"%(filename)
        continue
      for histname in hists:
        histpath = "%s/%s"%(histdir,histname)
        hist = file.Get(histpath)
        if not hist:
          print ">>>   Warning! getBTagEfficiencies: Could not open histogram '%s' in %s"%(histpath,filename)        
          dir = file.Get(histdir)
          if dir: dir.ls()
          continue
        if hists[histname]==None:
          hists[histname] = hist.Clone(histname)
          hists[histname].SetDirectory(0)
          nhists[histname] = 1
        else:
          hists[histname].Add(hist)
          nhists[histname] += 1
      file.Close()
    
    # CHECK
    if len(nhists)>0:
      print ">>>   added %d MC hists:"%(sum(nhists[n] for n in nhists))
      for histname, nhist in nhists.iteritems():
        print ">>>     %-26s%2d"%(histname+':',nhist)
    else:
      print ">>>   no histograms added !"
      return
    
    # DIVIDE and SAVE histograms
    print ">>>   writing to %s..."%(outfilename)
    file = TFile(outfilename,'UPDATE') #RECREATE
    ensureTDirectory(file,channel)
    for histname, hist in hists.iteritems():
      if 'all' in histname:
        continue
      histname_all = histname+'_all'
      histname_eff = 'eff_'+histname
      print ">>>      writing %s..."%(histname)
      print ">>>      writing %s..."%(histname_all)
      print ">>>      writing %s..."%(histname_eff)
      hist_all = hists[histname_all]
      hist_eff = hist.Clone(histname_eff)
      hist_eff.SetTitle(makeTitle(histname_eff,channel))
      hist_eff.Divide(hist_all)
      hist.Write(histname,TH2F.kOverwrite)
      hist_all.Write(histname_all,TH2F.kOverwrite)
      hist_eff.Write(histname_eff,TH2F.kOverwrite)
      if plot:
        plot2D(histname_eff,hist_eff,year,channel,log=True)
        plot2D(histname_eff,hist_eff,year,channel,log=False)
    file.Close()
    print ">>> "
  

def plot2D(histname,hist,year,channel,log=False):
    """Plot efficiency."""
    dir    = ensureDirectory('plots/%d'%year)
    name   = "%s/%s_%s"%(dir,histname,channel)
    if log:
      name += "_log"
    xtitle = 'jet p_{T} [GeV]'
    ytitle = 'jet #eta'
    ztitle = 'b tag efficiencies' if '_b_' in histname else 'b mistag rate'
    xmin, xmax = 20, hist.GetXaxis().GetXmax()
    
    canvas = TCanvas('canvas','canvas',100,100,800,700)
    canvas.SetFillColor(0)
    canvas.SetBorderMode(0)
    canvas.SetFrameFillStyle(0)
    canvas.SetFrameBorderMode(0)
    canvas.SetTopMargin(  0.07 ); canvas.SetBottomMargin( 0.13 )
    canvas.SetLeftMargin( 0.12 ); canvas.SetRightMargin(  0.17 )
    canvas.SetTickx(0); canvas.SetTicky(0)
    canvas.SetGrid()
    if log:
      canvas.SetLogx()
      canvas.SetLogz()
    canvas.cd()
    
    hist.Draw('COLZTEXT%d'%(22 if log else 77))
    hist.GetXaxis().SetTitle(xtitle)
    hist.GetYaxis().SetTitle(ytitle)
    hist.GetZaxis().SetTitle(ztitle)
    hist.GetXaxis().SetLabelSize(0.048)
    hist.GetYaxis().SetLabelSize(0.048)
    hist.GetZaxis().SetLabelSize(0.048)
    hist.GetXaxis().SetTitleSize(0.058)
    hist.GetYaxis().SetTitleSize(0.058)
    hist.GetZaxis().SetTitleSize(0.056)
    hist.GetXaxis().SetTitleOffset(1.03)
    hist.GetYaxis().SetTitleOffset(1.04)
    hist.GetZaxis().SetTitleOffset(1.03)
    hist.GetXaxis().SetLabelOffset(-0.004 if log else 0.005)
    hist.GetZaxis().SetLabelOffset(-0.005 if log else 0.005)
    hist.GetXaxis().SetRangeUser(xmin,xmax)
    hist.SetMinimum(0.01 if log else 0.0)
    hist.SetMaximum(1.0)
    
    gStyle.SetPaintTextFormat('.2f')
    hist.SetMarkerColor(kRed)
    hist.SetMarkerSize(1.8 if log else 1)
    
    canvas.SaveAs(name+'.pdf')
    canvas.SaveAs(name+'.png')
    canvas.Close()
  

def makeTitle(string,channel):
  string = string.replace('_',' ')
  string = string.replace(' c ',' c jet ')
  string = string.replace(' udsg ',' light-flavor jet ')
  string = "%s (%s)"%(string,channel.replace('tau',"#tau").replace('mu',"#mu").replace('ele',"e"))
  return string
  

def ensureTDirectory(file,dirname):
  dir = file.GetDirectory(dirname)
  if not dir:
    dir = file.mkdir(dirname)
    print ">>>   created directory %s in %s" % (dirname,file.GetName())
  dir.cd()
  return dir
  

def ensureDirectory(dirname):
  """Make directory if it does not exist."""
  if not os.path.exists(dirname):
    os.makedirs(dirname)
    print '>>> made directory "%s"'%(dirname)
    if not os.path.exists(dirname):
      print '>>> failed to make directory "%s"'%(dirname)
  return dirname
  

def main():
    
    years    = args.years
    channels = args.channels
    
    
    for year in args.years:
      
      # SAMPLES: list of analysis framework output run on MC samples
      #          that is used to add together and compute the efficiency
      if year==2016:
        samples = [
          ( 'TT', "TT",                   ),
          ( 'DY', "DYJetsToLL_M-10to50",  ),
          ( 'DY', "DYJetsToLL_M-50_reg",  ),
          ( 'DY', "DY1JetsToLL_M-50",     ),
          ( 'DY', "DY2JetsToLL_M-50",     ),
          ( 'DY', "DY3JetsToLL_M-50",     ),
          ( 'WJ', "WJetsToLNu",           ),
          ( 'WJ', "W1JetsToLNu",          ),
          ( 'WJ', "W2JetsToLNu",          ),
          ( 'WJ', "W3JetsToLNu",          ),
          ( 'WJ', "W4JetsToLNu",          ),
          ( 'ST', "ST_tW_top",            ),
          ( 'ST', "ST_tW_antitop",        ),
          ( 'ST', "ST_t-channel_top",     ),
          ( 'ST', "ST_t-channel_antitop", ),
          #( 'ST', "ST_s-channel",         ),
          ( 'VV', "WW",                   ),
          ( 'VV', "WZ",                   ),
          ( 'VV', "ZZ",                   ),
        ]
      elif year==2017:
        samples = [ 
          ( 'TT', "TTTo2L2Nu",            ),
          ( 'TT', "TTToHadronic",         ),
          ( 'TT', "TTToSemiLeptonic",     ),
          ( 'DY', "DYJetsToLL_M-10to50",  ),
          ( 'DY', "DYJetsToLL_M-50",      ),
          ( 'DY', "DY1JetsToLL_M-50",     ),
          ( 'DY', "DY2JetsToLL_M-50",     ),
          ( 'DY', "DY3JetsToLL_M-50",     ),
          ( 'DY', "DY4JetsToLL_M-50",     ),
          ( 'WJ', "WJetsToLNu",           ),
          ( 'WJ', "W1JetsToLNu",          ),
          ( 'WJ', "W2JetsToLNu",          ),
          ( 'WJ', "W3JetsToLNu",          ),
          ( 'WJ', "W4JetsToLNu",          ),
          ( 'ST', "ST_tW_top",            ),
          ( 'ST', "ST_tW_antitop",        ),
          ( 'ST', "ST_t-channel_top",     ),
          ( 'ST', "ST_t-channel_antitop", ),
          #( 'ST', "ST_s-channel",         ),
          ( 'VV', "WW",                   ),
          ( 'VV', "WZ",                   ),
          ( 'VV', "ZZ",                   ),
        ]
      else:
        samples = [
          ( 'TT', "TTTo2L2Nu",            ),
          ( 'TT', "TTToHadronic",         ),
          ( 'TT', "TTToSemiLeptonic",     ),
          ( 'DY', "DYJetsToLL_M-10to50",  ),
          ( 'DY', "DYJetsToLL_M-50_reg",  ),
          ( 'DY', "DY1JetsToLL_M-50",     ),
          ( 'DY', "DY2JetsToLL_M-50",     ),
          ( 'DY', "DY3JetsToLL_M-50",     ),
          ( 'DY', "DY4JetsToLL_M-50",     ),
          #( 'WJ', "WJetsToLNu",           ),
          ( 'WJ', "W1JetsToLNu",          ),
          ( 'WJ', "W2JetsToLNu",          ),
          ( 'WJ', "W3JetsToLNu",          ),
          ( 'WJ', "W4JetsToLNu",          ),
          ( 'ST', "ST_tW_top",            ),
          ( 'ST', "ST_tW_antitop",        ),
          ( 'ST', "ST_t-channel_top",     ),
          ( 'ST', "ST_t-channel_antitop", ),
          ( 'ST', "ST_s-channel",         ),
          ( 'VV', "WW",                   ),
          ( 'VV', "WZ",                   ),
          ( 'VV', "ZZ",                   ),
        ]
      
      # MC CAMPAIGN NAMES of each year 
      campaigns = { 2016: "Moriond17", 2017: "12Apr2017", 2018: "Autumn18" }
      
      # LOOP over channels
      for channel in args.channels:
        
        # SAMPLE FILE NAMES
        indir = "/scratch/ineuteli/analysis/LQ_%d"%(year)
        samplefilenames = ["%s/%s/%s_%s.root"%(indir,subdir,samplename,channel) for subdir, samplename in samples]
        
        # COMPUTE and SAVE b tag efficiencies
        for tagger in args.taggers:
          for wp in args.wps:
            outfilename = "%s_%d_%s_eff.root"%(tagger,year,campaigns[year])
            getBTagEfficiencies(tagger,wp,outfilename,samplefilenames,year,channel,plot=args.plot)
    


if __name__ == '__main__':
    print
    main()
    print ">>> done\n"
    

