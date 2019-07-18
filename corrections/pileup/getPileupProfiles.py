#! /usr/bin/env python
# Author: Izaak Neutelings (January 2019)
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2018Analysis
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#PileupInformation

import os, sys, shutil
from argparse import ArgumentParser
from corrections import ensureTFileAndTH1
from tools import CMS_style
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT, gDirectory, gStyle, gPad, TFile, TTree, TCanvas, TH1, TLine, TLegend,\
                 kBlack, kRed, kAzure, kGreen, kOrange, kMagenta, kYellow
gROOT.SetBatch(True)
gStyle.SetOptStat(False)
gStyle.SetOptTitle(False)
linecolors = [ kRed+1, kAzure+5, kGreen+2, kOrange+1, kMagenta-4, kYellow+1,
               kRed-9, kAzure-4, kGreen-2, kOrange+6, kMagenta+3, kYellow+2, ]

argv = sys.argv
description = '''This script makes pileup profiles for MC and data.'''
parser = ArgumentParser(prog="pileup",description=description,epilog="Succes!")
parser.add_argument('-y', '--year',    dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2018], action='store',
                                       help="select year" )
parser.add_argument('-c', '--channel', dest='channel', choices=['mutau','etau'], type=str, default='mutau', action='store',
                                       help="select channel" )
parser.add_argument('-t', '--type',    dest='types', choices=['data','mc'], type=str, nargs='+', default=['data','mc'], action='store',
                                       help="make profile for data and/or MC" )
parser.add_argument('-p', '--plot',    dest='plot', default=False, action='store_true', 
                                       help="plot profiles" )
parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true', 
                                       help="print verbose" )
args = parser.parse_args()



def getMCProfile(outfilename,indir,samples,channel,year,tag=""):
    """Get pileup profile in MC by adding Pileup_nTrueInt histograms from a given list of samples."""
    print '>>> getMCProfile("%s")'%(outfilename)
    nprofiles = 0
    histname  = 'pileup'
    tothist   = None
    for subdir, samplename in samples:
      filename = "%s/%s/%s_%s.root"%(indir,subdir,samplename,channel)
      print ">>>   %s"%(filename)
      file, hist = ensureTFileAndTH1(filename,histname)
      if not file or not hist: continue
      if tothist==None:
        tothist = hist.Clone('pileup')
        tothist.SetTitle('pileup')
        #tothist.SetTitle('MC average')
        tothist.SetDirectory(0)
        nprofiles += 1
      else:
        tothist.Add(hist)
        nprofiles += 1
      file.Close()
    print ">>>   added %d MC profiles, %d entries, %.1f mean"%(nprofiles,tothist.GetEntries(),tothist.GetMean())
    
    file = TFile(outfilename,'RECREATE')
    tothist.Write('pileup')
    tothist.SetDirectory(0)
    file.Close()
    
    return tothist
    


def getDataProfile(outfilename,JSON,pileup,bins,year,minbias,local=False):
    """Get pileup profile in data with pileupCalc.py tool."""
    print '>>> getDataProfile("%s",%d,%s)'%(outfilename,bins,minbias)
    
    # CREATE profile
    if local:
      JSON   = copyToLocal(JSON)
      pileup = copyToLocal(pileup)
      command = "./pileupCalc.py -i %s --inputLumiJSON %s --calcMode true --maxPileupBin %d --numPileupBins %d --minBiasXsec %d %s --verbose"%(JSON,pileup,bins,bins,minbias*1000,outfilename)
    else:
      command = "pileupCalc.py -i %s --inputLumiJSON %s --calcMode true --maxPileupBin %d --numPileupBins %d --minBiasXsec %d %s"%(JSON,pileup,bins,bins,minbias*1000,outfilename)
    print ">>>   executing command (this may take a while):"
    print ">>>   " + command
    os.system(command)
    
    # GET profile
    histname = 'pileup'
    if not os.path.isfile(outfilename):
      print ">>>   Warning! getDataProfile: Could find output file %s!"%(outfilename)
      return
    file, hist = ensureTFileAndTH1(outfilename,histname)
    hist.SetName("%s_%s"%(histname,str(minbias).replace('.','p')))
    hist.SetTitle("Data %s, %.1f pb"%(year,minbias))
    hist.SetDirectory(0)
    hist.SetBinContent(0,0.0)
    hist.SetBinContent(1,0.0)
    print ">>>   pileup profile in data with min. bias %s mb has a mean of %.1f"%(minbias,hist.GetMean())
    file.Close()
    
    return hist
    


def getGenProfile(outfilename,year):
    print ">>> getGenProfile(%s):"%(year)
    if year==2016:
      bins = [
        # https://github.com/cms-sw/cmssw/blob/CMSSW_9_4_X/SimGeneral/MixingModule/python/mix_2016_25ns_Moriond17MC_PoissonOOTPU_cfi.py
        1.78653e-05, 2.56602e-05, 5.27857e-05, 8.88954e-05, 0.000109362,
        0.000140973, 0.000240998, 0.00071209,  0.00130121,  0.00245255, 
        0.00502589,  0.00919534,  0.0146697,   0.0204126,   0.0267586,
        0.0337697,   0.0401478,   0.0450159,   0.0490577,   0.0524855,
        0.0548159,   0.0559937,   0.0554468,   0.0537687,   0.0512055,
        0.0476713,   0.0435312,   0.0393107,   0.0349812,   0.0307413,
        0.0272425,   0.0237115,   0.0208329,   0.0182459,   0.0160712,
        0.0142498,   0.012804,    0.011571,    0.010547,    0.00959489,
        0.00891718,  0.00829292,  0.0076195,   0.0069806,   0.0062025,
        0.00546581,  0.00484127,  0.00407168,  0.00337681,  0.00269893,
        0.00212473,  0.00160208,  0.00117884,  0.000859662, 0.000569085,
        0.000365431, 0.000243565, 0.00015688,  9.88128e-05, 6.53783e-05,
        3.73924e-05, 2.61382e-05, 2.0307e-05,  1.73032e-05, 1.435e-05,
        1.36486e-05, 1.35555e-05, 1.37491e-05, 1.34255e-05, 1.33987e-05,
        1.34061e-05, 1.34211e-05, 1.34177e-05, 1.32959e-05, 1.33287e-05,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
      ]
    elif year==2017:
      # https://github.com/cms-sw/cmssw/blob/CMSSW_9_4_X/SimGeneral/MixingModule/python/mix_2017_25ns_WinterMC_PUScenarioV1_PoissonOOTPU_cfi.py
      bins = [
        3.39597497605e-05, 6.63688402133e-06, 1.39533611284e-05, 3.64963078209e-05, 6.00872171664e-05, 9.33932578027e-05,
        0.000120591524486, 0.000128694546198, 0.000361697233219, 0.000361796847553, 0.000702474896113, 0.00133766053707,
        0.00237817050805,  0.00389825605651,  0.00594546732588,  0.00856825906255,  0.0116627396044,   0.0148793350787, 
        0.0179897368379,   0.0208723871946,   0.0232564170641,   0.0249826433945,   0.0262245860346,   0.0272704617569,
        0.0283301107549,   0.0294006137386,   0.0303026836965,   0.0309692426278,   0.0308818046328,   0.0310566806228,
        0.0309692426278,   0.0310566806228,   0.0310566806228,   0.0310566806228,   0.0307696426944,   0.0300103336052,
        0.0288355370103,   0.0273233309106,   0.0264343533951,   0.0255453758796,   0.0235877272306,   0.0215627588047,
        0.0195825559393,   0.0177296309658,   0.0160560731931,   0.0146022004183,   0.0134080690078,   0.0129586991411,
        0.0125093292745,   0.0124360740539,   0.0123547104433,   0.0123953922486,   0.0124360740539,   0.0124360740539,
        0.0123547104433,   0.0124360740539,   0.0123387597772,   0.0122414455005,   0.011705203844,    0.0108187105305,
        0.00963985508986,  0.00827210065136,  0.00683770076341,  0.00545237697118,  0.00420456901556,  0.00367513566191,
        0.00314570230825,  0.0022917978982,   0.00163221454973,  0.00114065309494,  0.000784838366118, 0.000533204105387,
        0.000358474034915, 0.000238881117601, 0.0001984254989,   0.000157969880198, 0.00010375646169,  6.77366175538e-05,
        4.39850477645e-05, 2.84298066026e-05, 1.83041729561e-05, 1.17473542058e-05, 7.51982735129e-06, 6.16160108867e-06,
        4.80337482605e-06, 3.06235473369e-06, 1.94863396999e-06, 1.23726800704e-06, 7.83538083774e-07, 4.94602064224e-07,
        3.10989480331e-07, 1.94628487765e-07, 1.57888581037e-07, 1.2114867431e-07,  7.49518929908e-08, 4.6060444984e-08,
        2.81008884326e-08, 1.70121486128e-08, 1.02159894812e-08, 0.0,               #0.0,
      ]
    elif year==2018:
      # https://github.com/cms-sw/cmssw/blob/CMSSW_10_4_X/SimGeneral/MixingModule/python/mix_2018_25ns_JuneProjectionFull18_PoissonOOTPU_cfi.py
      bins = [
          4.695341e-10, 1.206213e-06, 1.162593e-06, 6.118058e-06, 1.626767e-05,
          3.508135e-05, 7.12608e-05,  0.0001400641, 0.0002663403, 0.0004867473,
          0.0008469,    0.001394142,  0.002169081,  0.003198514,  0.004491138,
          0.006036423,  0.007806509,  0.00976048,   0.0118498,    0.01402411,
          0.01623639,   0.01844593,   0.02061956,   0.02273221,   0.02476554,
          0.02670494,   0.02853662,   0.03024538,   0.03181323,   0.03321895,
          0.03443884,   0.035448,     0.03622242,   0.03674106,   0.0369877,
          0.03695224,   0.03663157,   0.03602986,   0.03515857,   0.03403612,
          0.0326868,    0.03113936,   0.02942582,   0.02757999,   0.02563551,
          0.02362497,   0.02158003,   0.01953143,   0.01750863,   0.01553934,
          0.01364905,   0.01186035,   0.01019246,   0.008660705,  0.007275915,
          0.006043917,  0.004965276,  0.004035611,  0.003246373,  0.002585932,
          0.002040746,  0.001596402,  0.001238498,  0.0009533139, 0.0007282885,
          0.000552306,  0.0004158005, 0.0003107302, 0.0002304612, 0.0001696012,
          0.0001238161, 8.96531e-05,  6.438087e-05, 4.585302e-05, 3.23949e-05,
          2.271048e-05, 1.580622e-05, 1.09286e-05,  7.512748e-06, 5.140304e-06,
          3.505254e-06, 2.386437e-06, 1.625859e-06, 1.111865e-06, 7.663272e-07,
          5.350694e-07, 3.808318e-07, 2.781785e-07, 2.098661e-07, 1.642811e-07,
          1.312835e-07, 1.081326e-07, 9.141993e-08, 7.890983e-08, 6.91468e-08,
          6.119019e-08, 5.443693e-08, 4.85036e-08,  4.31486e-08,  3.822112e-08
      ]
    else:
      print ">>>   Warning! No generator pileup profile for year %s"%(year)
    
    nbins = len(bins)
    hist  = TH1F('pileup','pileup',nbins,0,nbins)
    hist.Sumw2()
    for i, binc in enumerate(bins,1):
      hist.SetBinContent(i,binc)
    
    file = TFile(outfilename,'RECREATE')
    hist.Write('pileup')
    file.Close()
    


def compareMCProfiles(indir,samples,channel,year,tag=""):
    """Compare MC profiles."""
    print ">>> compareMCProfiles()"
    
    histname = 'pileup'
    outdir   = ensureDirectory("plots")
    avehist  = None
    hists    = [ ]
    if tag and tag[0]!='_': tag = '_'+tag
    
    # GET histograms
    for subdir, samplename in samples:
      filename = "%s/%s/%s_%s.root"%(indir,subdir,samplename,channel)
      print ">>>   %s"%(filename)
      file = TFile(filename,'READ')
      if not file or file.IsZombie():
        print ">>>   Warning! compareMCProfiles: Could not open %s"%(filename)
        continue
      hist = file.Get(histname)
      hist.SetName(samplename)
      hist.SetTitle(samplename)
      hist.SetDirectory(0)
      if not hist:
        print ">>>   Warning! compareMCProfiles: Could not open histogram in %s"%(filename)      
        continue
      if avehist==None:
        avehist = hist.Clone('average%s'%tag)
        avehist.SetTitle('MC average')
        avehist.SetDirectory(0)
      avehist.Add(hist)
      hist.Scale(1./hist.Integral())
      hists.append(hist)
      file.Close()
    
    # PLOT
    hists  = [avehist]+hists
    colors = [kBlack]+linecolors
    avehist.Scale(1./avehist.Integral())
    plotname = "%s/pileup_MC_%s%s"%(outdir,year,tag)
    drawHistsWithRatio(hists,plotname,xtitle="Number of true interactions",ytitle="A.U.",
                       textsize=0.032,rmin=0.45,rmax=1.55,colors=colors)
    for hist in hists:
      if hist==avehist: continue
      if hist.GetDirectory():
        gDirectory.Delete(hist.GetName())
      else:
        hist.Delete()
    
    return avehist
    


def compareDataMCProfiles(datahist,mchist,year,minbias,tag=""):
    """Compare data/MC profiles."""
    print ">>> compareDataMCProfiles()"
    if tag and tag[0]!='_': tag = '_'+tag    
    outdir = ensureDirectory("plots")
    hists  = [datahist,mchist]
    colors = [kBlack]+linecolors
    
    datahist.SetTitle("Data %s, %.1f pb"%(year,minbias))
    mchist.SetTitle("MC average")
    datahist.Scale(1./datahist.Integral())
    mchist.Scale(1./mchist.Integral())
    
    plotname = "%s/pileup_Data-MC_%s_%s%s"%(outdir,year,str(minbias).replace('.','p'),tag)
    drawHistsWithRatio(hists,plotname,xtitle="Number of interactions",ytitle="A.U.",rtitle="Data / MC",
                       textsize=0.045,rmin=0.75,rmax=1.25,colors=colors)
    


def drawHistsWithRatio(hists,name,**kwargs):
    """Draw histograms with ratios."""
    
    title      = kwargs.get('title',        ""                   )
    xtitle     = kwargs.get('xtitle',       ""                   )
    ytitle     = kwargs.get('ytitle',       ""                   )
    rtitle     = kwargs.get('rtitle',       "Ratio"              )
    xmin       = kwargs.get('xmin',         hists[0].GetXaxis().GetXmin() )
    xmax       = kwargs.get('xmax',         hists[0].GetXaxis().GetXmax() )
    ymin       = kwargs.get('ymin',         None                 )
    ymax       = kwargs.get('ymax',         None                 )
    rmin       = kwargs.get('rmin',         0.45                 )
    rmax       = kwargs.get('rmax',         1.55                 )
    logx       = kwargs.get('logx',         False                )
    logy       = kwargs.get('logy',         False                )
    denom      = kwargs.get('denom',        1                    )-1 # denominator for ratio
    textsize   = kwargs.get('textsize',     0.045                )
    texts      = kwargs.get('text',         [ ]                  )
    #textheight = kwargs.get('textheight',   1.09                 )
    #ctext      = kwargs.get('ctext',        [ ]                  ) # corner text
    #cposition  = kwargs.get('cposition',    'topleft'            ).lower() # cornertext
    #ctextsize  = kwargs.get('ctextsize',    1.4*legendtextsize   )
    colors     = kwargs.get('colors',       linecolors           )
    if not isinstance(texts,list) or isinstance(texts,tuple):
      texts    = [texts]
    if ymax==None:
      ymax     = 1.12*max(h.GetMaximum() for h in hists)
    
    # MAIN plot
    canvas = TCanvas('canvas','canvas',100,100,800,800)
    canvas.SetFillColor(0)
    canvas.SetBorderMode(0)
    canvas.SetFrameBorderMode(0)
    canvas.Divide(2)
    canvas.SetMargin(0.0,0.0,0.0,0.0)
    canvas.cd(1)
    gPad.SetPad('pad1','pad1',0,0.33,1,1)
    gPad.SetMargin(0.12,0.04,0.02,0.08)
    gPad.SetFillColor(0)
    gPad.SetBorderMode(0)
    gPad.SetTickx(0); gPad.SetTicky(0)
    gPad.SetGrid()
    gPad.Draw()
    canvas.cd(2)
    gPad.SetPad('pad2','pad2',0,0,1,0.33)
    gPad.SetMargin(0.12,0.04,0.30,0.03)
    gPad.SetFillColor(0)
    gPad.SetFillStyle(4000)
    gPad.SetFrameFillStyle(0)
    gPad.SetBorderMode(0)
    gPad.Draw()
    
    # MAIN plot
    canvas.cd(1)
    for i, hist in enumerate(hists):
      color = colors[i%len(colors)]
      hist.SetLineColor(color)
      hist.SetLineWidth(2)
      hist.Draw('HIST SAME')
    frame = hists[0]
    frame.GetYaxis().SetTitleSize(0.060)
    frame.GetXaxis().SetTitleSize(0)
    frame.GetXaxis().SetLabelSize(0)
    frame.GetYaxis().SetLabelSize(0.052)
    frame.GetXaxis().SetLabelOffset(0.010)
    frame.GetXaxis().SetTitleOffset(0.98)
    frame.GetYaxis().SetTitleOffset(1.05)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().SetTitle(ytitle)
    frame.GetXaxis().SetTitle(xtitle)
    if logx: gPad.Update(); gPad.SetLogx()
    if logy: gPad.Update(); gPad.SetLogy()
    if ymin: frame.SetMinimum(ymin)
    if ymax: frame.SetMaximum(ymax)
    
    width    = 0.25
    height   = 1.1*textsize*len([l for l in texts+hists if l])
    x1, y1   = 0.65, 0.88
    x2, y2   = x1+width, y1-height
    legend = TLegend(x1,y1,x2,y2)
    legend.SetTextSize(textsize)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetFillColor(0)
    legend.SetMargin(0.05/width)
    if title:
      legend.SetTextFont(62)
      legend.SetHeader(title)
    legend.SetTextFont(42)
    for hist in hists:
      legend.AddEntry(hist, hist.GetTitle(), 'l')
    for text in texts:
      legend.AddEntry(0, text, '')
    legend.Draw()
    
    gPad.SetTicks(1,1)
    gPad.Modified()
    frame.Draw('AXIS SAME')
    CMS_style.CMS_lumi(gPad,13,0)
    
    # RATIO plot
    canvas.cd(2)
    ratios = [ ]
    for i, hist in enumerate(hists):
      if i==denom: continue
      ratio = hist.Clone(hist.GetName()+"_ratio")
      ratio.Divide(hists[denom])
      ratio.Draw('HIST SAME')
      ratios.append(ratio)
    frame_ratio = ratios[0]
    frame_ratio.GetYaxis().SetRangeUser(rmin,rmax)
    frame_ratio.GetYaxis().CenterTitle()
    frame_ratio.GetYaxis().SetTitleSize(0.13)
    frame_ratio.GetXaxis().SetTitleSize(0.13)
    frame_ratio.GetXaxis().SetLabelSize(0.12)
    frame_ratio.GetYaxis().SetLabelSize(0.11)
    frame_ratio.GetXaxis().SetLabelOffset(0.012)
    frame_ratio.GetXaxis().SetTitleOffset(1.02)
    frame_ratio.GetYaxis().SetTitleOffset(0.48)
    frame_ratio.GetXaxis().SetNdivisions(508)
    frame_ratio.GetYaxis().CenterTitle(True)
    frame_ratio.GetYaxis().SetTitle(rtitle)
    frame_ratio.GetXaxis().SetTitle(xtitle)
    frame_ratio.GetYaxis().SetNdivisions(505)
    if logx: gPad.Update(); gPad.SetLogx()
    line = TLine(xmin,1.,xmax,1.)
    line.SetLineColor(hists[denom].GetLineColor())
    line.SetLineWidth(hists[denom].GetLineWidth())
    line.SetLineStyle(1)
    line.Draw('SAME')
    gPad.SetTicks(1,1)
    gPad.Update()
    gPad.SetGrid()
    gPad.Modified()
    frame_ratio.Draw('SAME AXIS')
    
    canvas.SaveAs(name+".png")
    canvas.SaveAs(name+".pdf")
    canvas.Close()



def copyToLocal(filename):
  """Copy file to current directory, and return new name."""
  fileold = filename
  filenew = filename.split('/')[-1]
  shutil.copyfile(fileold,filenew)
  if not os.path.isfile(filenew):
    print ">>> ERROR! Copy %s failed!"%(filenew)
  return filenew
  


def ensureDirectory(dirname):
  """Make directory if it does not exist."""
  if not os.path.exists(dirname):
    os.makedirs(dirname)
    print '>>> made directory "%s"'%(dirname)
    if not os.path.exists(dirname):
      print '>>> failed to make directory "%s"'%(dirname)
  return dirname
  


def main():
    
    years     = args.years
    channel   = args.channel
    types     = args.types
    minbiases = [ 69.2, 80.0, 69.2*1.046, 69.2*0.954 ]
    
    for year in args.years:
      filename  = "MC_PileUp_%d.root"%(year)
      indir     = "/scratch/ineuteli/analysis/LQ_%d"%(year)
      if year==2016:
        #JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
        JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt"
        pileup  = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt"
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
        filename_bug = filename.replace(".root","_old_pmx.root")
        filename_fix = filename.replace(".root","_new_pmx.root")
        JSON         = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt"
        pileup       = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt"    
        samples_bug  = [
          ( 'DY', "DYJetsToLL_M-50",      ),
          ( 'WJ', "W3JetsToLNu",          ),
          ( 'VV', "WZ",                   ),
        ]
        samples_fix  = [
          ( 'DY', "DYJetsToLL_M-10to50",  ),
          ( 'DY', "DY1JetsToLL_M-50",     ),
          #( 'DY', "DY1JetsToLL_M-50_reg", ),
          #( 'DY', "DY1JetsToLL_M-50_ext", ),
          #( 'DY', "DY2JetsToLL_M-50",     ),
          ( 'DY', "DY2JetsToLL_M-50_reg", ),
          ( 'DY', "DY2JetsToLL_M-50_ext", ),
          #( 'DY', "DY3JetsToLL_M-50",     ),
          ( 'DY', "DY3JetsToLL_M-50_reg", ),
          ( 'DY', "DY3JetsToLL_M-50_ext", ),
          ( 'DY', "DY4JetsToLL_M-50",     ),
          ( 'TT', "TTTo2L2Nu",            ),
          ( 'TT', "TTToHadronic",         ),
          ( 'TT', "TTToSemiLeptonic",     ),
          #( 'WJ', "WJetsToLNu",           ),
          ( 'WJ', "WJetsToLNu_reg",       ),
          ( 'WJ', "WJetsToLNu_ext",       ),
          ( 'WJ', "W1JetsToLNu",          ),
          ( 'WJ', "W2JetsToLNu",          ),
          ( 'WJ', "W4JetsToLNu",          ),
          ( 'ST', "ST_tW_top",            ),
          ( 'ST', "ST_tW_antitop",        ),
          ( 'ST', "ST_t-channel_top",     ),
          ( 'ST', "ST_t-channel_antitop", ),
          #( 'ST', "ST_s-channel",         ),
          ( 'VV', "WW",                   ),
          ( 'VV', "ZZ",                   ),
        ]
        samples = samples_bug + samples_fix
      else:
        JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt"
        pileup  = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt"
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
          #( 'ST', "ST_s-channel",         ),
          ( 'VV', "WW",                   ),
          ( 'VV', "WZ",                   ),
          ( 'VV', "ZZ",                   ),
        ]
      
      # DATA
      datafiles = [ ]
      datahists = [ ]
      if 'data' in args.types:
        for minbias in minbiases:
          filename = "Data_PileUp_%d_%s.root"%(year,str(minbias).replace('.','p'))
          datahist = getDataProfile(filename,JSON,pileup,100,year,minbias)
          datahists.append(datahist)
          datafiles.append(filename)
      elif args.plot:
        for minbias in minbiases:
          filename = "Data_PileUp_%d_%s.root"%(year,str(minbias).replace('.','p'))
          file, hist = ensureTFileAndTH1(filename,'pileup')
          if not file or not hist: continue
          hist.SetDirectory(0)
          file.Close()
          datahists.append(hist)
      
      # MC
      CMS_style.setYear(year)
      if 'mc' in args.types:
        getMCProfile(filename,indir,samples,channel,year)
        if args.plot:
          mchist = compareMCProfiles(indir,samples,channel,year)
          for minbias, datahist in zip(minbiases,datahists):
            compareDataMCProfiles(datahist,mchist,year,minbias)
        if year==2017:
          getMCProfile(filename_bug,indir,samples_bug,channel,year)
          getMCProfile(filename_fix,indir,samples_fix,channel,year)
          if args.plot:
            mchist_bug = compareMCProfiles(indir,samples_bug,channel,year,tag="old_pmx")
            mchist_fix = compareMCProfiles(indir,samples_fix,channel,year,tag="new_pmx")
            for minbias, datahist in zip(minbiases,datahists):
              compareDataMCProfiles(datahist,mchist_bug,year,minbias,tag="old_pmx")
              compareDataMCProfiles(datahist,mchist_fix,year,minbias,tag="new_pmx")
      


if __name__ == '__main__':
    print
    main()
    print ">>> done\n"
    

