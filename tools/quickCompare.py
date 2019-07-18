#! /usr/bin/env python
# Author: Izaak Neutelings (May 2019)
from ROOT import gROOT, gPad, gDirectory, TFile, TEntryList, TH1D, TCanvas, kBlue, kRed
from postprocessors import ensureDirectory
gROOT.SetBatch(True)
director_store = "root://xrootd-cms.infn.it/"
director_pnfs  = "root://t3dcachedb.psi.ch:1094/"



def ensureDirector(filename):
  """Ensure a given root file has the correct director."""
  if 'root://' in filename:
    return filename
  elif '/pnfs/' in filename:
    return director_pnfs+filename
  elif '/store/' in filename:
    return director_store+filename
  return filename
  


def makeHists(tree1,tree2,var1,var2,nbins,xmin,xmax,cut1,cut2):
  name1 = var1+'_1'
  name2 = var2+'_2'
  hist1 = TH1D(name1,var1,nbins,xmin,xmax)
  hist2 = TH1D(name2,var2,nbins,xmin,xmax)
  out1  = tree1.Draw("%s >> %s"%(var1,name1),cut1,'gOff')
  out2  = tree2.Draw("%s >> %s"%(var2,name2),cut2,'gOff')
  print ">>>   %s: %s vs. %s entries"%(var1,out1,out2)
  return hist1, hist2
  


def getCommon(tree1,tree2):
  #https://github.com/CMS-HTT/2016-sync/blob/ML2018/compare.py#L84
  list1, list1 = TEntryList(), TEntryList()
  
  tree1.Draw('event',"",'gOff')
  events1 = tree1.GetV1()
  
  return list1, list2
  


def getVariables(var):
  if isinstance(var,tuple):
    var1, var2 = var
    var = var1
  else:
    var1, var2 = var, var
  return var, var1, var2
  


def compareFiles(filename1,filename2,variables,**kwargs):
  """Compare distributions in two given files in NANOAOD format."""
  print ">>> compareFiles"
  
  outdir    = kwargs.get('outdir', '.'      )
  tag       = kwargs.get('tag',    ""       )
  treename  = kwargs.get('tree',   'Events' )
  treename1 = kwargs.get('tree1',  treename )
  treename2 = kwargs.get('tree2',  treename )
  cut       = kwargs.get('tree',   ""       )
  cut1      = kwargs.get('cut1',   cut      )
  cut2      = kwargs.get('cut2',   cut      )
  common    = kwargs.get('common', True     )
  plot      = kwargs.get('plot',   True     )
  nmax      = kwargs.get('max',    1000     )
  
  file1 = TFile.Open(filename1)
  file2 = TFile.Open(filename2)
  tree1 = file1.Get(treename1)
  tree2 = file2.Get(treename2)
  entries1 = tree1.GetEntries()
  entries2 = tree2.GetEntries()
  ensureDirectory(outdir)
  
  print ">>> %10s"%("tree entries")
  print ">>> %10s, %s"%(entries1,filename1)
  print ">>> %10s, %s"%(entries2,filename2)
  
  #if common:
  #  list1, list2 = getCommon(tree1,tree2)
  #  tree1.SetEntryList(list1)
  #  tree2.SetEntryList(list2)
  
  if plot:
    for var, nbins, xmin, xmax in variables:
      var, var1, var2 = getVariables(var)
      if 'LHE' in var and 'Single' in filename1:
        continue
      hist1, hist2 = makeHists(tree1,tree2,var1,var2,nbins,xmin,xmax,cut1,cut2)
      name = "%s/%s%s.png"%(outdir,var.replace('[0]','_1').replace('[1]','_2'),tag)
      plotRatio(var,name,hist1,hist2)
  
  else:
    variables = [var for var, nbins, xmin, xmax in variables]
    entries = min(entries1,entries2,nmax)
    
    header = ">>> "
    for variable in variables:
      var, var1, var2 = getVariables(variable)
      header += " %10s - %8s"%(var1,var2)
    print header
    
    for i in xrange(entries):
      tree1.GetEntry(i)
      tree2.GetEntry(i)
      row = ">>> "
      for variable in variables:
        var, var1, var2 = getVariables(variable)
        val1 = getattr(tree1,var1.split('[')[0])[0] if '[0]' in var1 else getattr(tree1,var1)
        val2 = getattr(tree2,var2)
        row += " %10.3f - %8.3f"%(val1,val2)
      print row
      
  
  file1.Close()
  file2.Close()
  


def plotRatio(var,name,hist1,hist2):
  """Plot minimal ratio of two histograms."""
  
  canvas = TCanvas('canvas','canvas',100,100,800,800)
  canvas.Divide(2)
  canvas.cd(1)
  gPad.SetPad('pad1','pad1',0,0.42,1,1,0,-1,0)
  gPad.SetTopMargin(  0.10 ); gPad.SetBottomMargin( 0.01 )
  
  hist1.Draw()
  hist2.Draw('SAME')
  
  hist1.SetLineColor(kBlue)
  hist2.SetLineColor(kRed)
  hist1.SetLineWidth(2)
  hist2.SetLineWidth(2)
  hist1.SetLineStyle(1)
  hist2.SetLineStyle(2)
  hist1.Draw('HIST')
  hist2.Draw('HIST SAMES')
  gPad.Update()
  
  stats1 = hist1.GetListOfFunctions().FindObject('stats')
  stats2 = hist2.GetListOfFunctions().FindObject('stats')
  stats1.SetY1NDC(.74); stats1.SetY2NDC(.94)
  stats2.SetY1NDC(.50); stats2.SetY2NDC(.70)
  stats1.Draw()
  stats2.Draw()
  
  canvas.cd(2)
  gPad.SetPad('pad2','pad2',0,0,1,0.41,0,-1,0)
  gPad.SetTopMargin(  0.05 ); gPad.SetBottomMargin( 0.24 )
  ratio = hist1.Clone('ratio')
  ratio.Divide(hist2)
  for i, (y1, y2, r) in enumerate(zip(hist1,hist2,ratio),0):
    if hist1.GetBinContent(i)==0 and hist2.GetBinContent(i)==0:
      ratio.SetBinContent(i,1)
  
  ratio.GetXaxis().SetTitle(var)
  ratio.GetXaxis().SetLabelSize(0.045)
  ratio.GetYaxis().SetLabelSize(0.045)
  ratio.GetXaxis().SetTitleSize(0.060)
  ratio.SetMinimum(0.2)
  ratio.SetMaximum(1.8)
  ratio.Draw()
  
  statsr = ratio.GetListOfFunctions().FindObject('stats')
  statsr.SetY1NDC(.65); statsr.SetY2NDC(.98)
  
  canvas.SaveAs(name)
  canvas.Close()
  gDirectory.Delete(hist1.GetName())
  gDirectory.Delete(hist2.GetName())
  gDirectory.Delete(ratio.GetName())
  


def main():
  
  #for f in ../filelist/filelist_SingleMuon/Run201*.txt; do b=`head -n 1 $f`; echo; c=`basename $b`; printf '( "", "%s",\n' $b; printf '  "%s"),' `ls /pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_201*/SingleMuon*/*${c/.root/}*root`; done; echo
  #for f in ../filelist/filelist_DY*.txt; do b=`head -n 1 $f`; echo; c=`basename $b`; printf '( "", "%s",\n' $b; printf '  "%s"),' `ls /pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_201*/DY*/*${c/.root/}*root`; done; echo
  files = [
    
#     ("DYJets_LM_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/20000/090E23D2-F49A-D24F-B6BC-ABC8AF45AB98.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM/090E23D2-F49A-D24F-B6BC-ABC8AF45AB98_skimmed.root"),
#     ("DYJets_LM_2016", "root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/80000/DCFC4629-0F57-9249-9474-017E7FF54359.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/DCFC4629-0F57-9249-9474-017E7FF54359_skimmed.root"),
#     ("DYJets_2018", "root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/110000/F84049F6-E35A-6941-AD05-C89BBEA73723.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/NANOAODSIM/F84049F6-E35A-6941-AD05-C89BBEA73723_skimmed.root"),
#     ("DYJets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/260000/CFDCF0D4-A3BD-E04B-89D5-1BE152CB8754.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM/CFDCF0D4-A3BD-E04B-89D5-1BE152CB8754_skimmed.root"),
#     ("DYJets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/260000/835DD563-D81A-274A-892B-A4AD8F98DFE7.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/835DD563-D81A-274A-892B-A4AD8F98DFE7_skimmed.root"),
#     ("DYJets_2016", "root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/65F4CD47-EC91-0A4B-9EE0-D0B9E39B49D7.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/NANOAODSIM/65F4CD47-EC91-0A4B-9EE0-D0B9E39B49D7_skimmed.root"),
#     ("DYJets_2016", "root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext2-v1/90000/07E1A503-1639-D643-BC7B-8E6CA3F25FD2.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext2-v1/NANOAODSIM/07E1A503-1639-D643-BC7B-8E6CA3F25FD2_skimmed.root"),
#     
#     ("DY1Jets_2018", "root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/270000/3F2D5349-6F37-6C40-A38F-91C151DA97FA.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/3F2D5349-6F37-6C40-A38F-91C151DA97FA_skimmed.root"),
#     ("DY1Jets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/80000/05BF8997-6762-BE43-89EE-ED02A0722E5D.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/05BF8997-6762-BE43-89EE-ED02A0722E5D_skimmed.root"),
#     ("DY1Jets_2017_1", "/store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/E3768A0E-3EF3-EB49-BF79-5C3E7679BB13.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/E3768A0E-3EF3-EB49-BF79-5C3E7679BB13_skimmed.root"),
#     ("DY1Jets_2016", "root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/40000/84F8299F-093B-9C4F-9233-C24B20748049.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/84F8299F-093B-9C4F-9233-C24B20748049_skimmed.root"),
#     
#     ("DY2Jets_2018", "root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/270000/42C80EE0-9FF5-7940-9A7D-74F6FE9E6DBD.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/42C80EE0-9FF5-7940-9A7D-74F6FE9E6DBD_skimmed.root"),
#     ("DY2Jets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/80000/FAAFCAD3-447E-934F-8F8C-60A099B71305.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM/FAAFCAD3-447E-934F-8F8C-60A099B71305_skimmed.root"),
#     ("DY2Jets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/10000/2E430F02-D6A7-0B40-9CDD-2C34D05747E4.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/2E430F02-D6A7-0B40-9CDD-2C34D05747E4_skimmed.root"),
#     ("DY2Jets_2016", "root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/30000/2A589D2E-9C30-3340-BA59-B96F4A4BF8D2.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/2A589D2E-9C30-3340-BA59-B96F4A4BF8D2_skimmed.root"),
#     
#     ("DY3Jets_2018", "root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/110000/F56D9AC6-BB99-FD49-9D2E-7DBDA7348938.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/F56D9AC6-BB99-FD49-9D2E-7DBDA7348938_skimmed.root"),
#     ("DY3Jets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/40000/5CCCE3BE-A806-9E4E-B281-73B5530EB55A.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM/5CCCE3BE-A806-9E4E-B281-73B5530EB55A_skimmed.root"),
#     ("DY3Jets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/90000/CE72D4A1-A7C9-E745-862B-C88AC7E65004.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/CE72D4A1-A7C9-E745-862B-C88AC7E65004_skimmed.root"),
#     ("DY3Jets_2016", "root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/50000/6A368940-6AE8-FD4C-843E-C42917377592.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/6A368940-6AE8-FD4C-843E-C42917377592_skimmed.root"),
#     
#     ("DY4Jets_2018", "root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/60000/09622B16-5AB4-7A41-950E-D632D0945B38.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/09622B16-5AB4-7A41-950E-D632D0945B38_skimmed.root"),
#     ("DY4Jets_2017", "root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v2_102X_mc2017_realistic_v6-v1/80000/FFAEE821-1A0D-3B4F-B5C9-E54936F0F2EE.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v2_102X_mc2017_realistic_v6-v1/NANOAODSIM/FFAEE821-1A0D-3B4F-B5C9-E54936F0F2EE_skimmed.root"),
#     ("DY4Jets_2018", "root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/110000/BBDE47BF-CEA4-154A-B713-56480CA9C97F.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/BBDE47BF-CEA4-154A-B713-56480CA9C97F_skimmed.root"),
    
#     ("SingleMuon_Run2016B", "/store/data/Run2016B_ver2/SingleMuon/NANOAOD/Nano14Dec2018_ver2-v1/80000/0C3486B0-624D-AB4D-86A9-2D41AE79FF4C.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016B_ver2-Nano14Dec2018_ver2-v1/NANOAOD/0C3486B0-624D-AB4D-86A9-2D41AE79FF4C_skimmed.root"),
#     ("SingleMuon_Run2016C", "/store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/79F59377-7829-3744-B387-8F3E8F3880DD.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016C-Nano14Dec2018-v1/NANOAOD/79F59377-7829-3744-B387-8F3E8F3880DD_skimmed.root"),
#     ("SingleMuon_Run2016D", "/store/data/Run2016D/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/4D5F505A-AE73-3F4D-B1E6-6A647D1ABF1E.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016D-Nano14Dec2018-v1/NANOAOD/4D5F505A-AE73-3F4D-B1E6-6A647D1ABF1E_skimmed.root"),
#     ("SingleMuon_Run2016E", "/store/data/Run2016E/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/EE001DE1-10BB-A044-A5E1-B582C2EFA68B.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016E-Nano14Dec2018-v1/NANOAOD/EE001DE1-10BB-A044-A5E1-B582C2EFA68B_skimmed.root"),
#     ("SingleMuon_Run2016F", "/store/data/Run2016F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/F972BC9B-9921-144F-8F98-595D13C6704F.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016F-Nano14Dec2018-v1/NANOAOD/F972BC9B-9921-144F-8F98-595D13C6704F_skimmed.root"),
#     ("SingleMuon_Run2016G", "/store/data/Run2016G/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/AAC4466D-0EFC-554B-9889-FFEDCA83A3D0.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016G-Nano14Dec2018-v1/NANOAOD/AAC4466D-0EFC-554B-9889-FFEDCA83A3D0_skimmed.root"),
#     ("SingleMuon_Run2016H", "/store/data/Run2016H/SingleMuon/NANOAOD/Nano14Dec2018-v1/90000/84BFF2B9-585A-EB4F-8FD2-6AB790CB45D4.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/SingleMuon/Run2016H-Nano14Dec2018-v1/NANOAOD/84BFF2B9-585A-EB4F-8FD2-6AB790CB45D4_skimmed.root"),
    
#     ("SingleMuon_Run2017B", "/store/data/Run2017B/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/FAE75F95-3C85-334A-939B-53495B8DB326.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/SingleMuon/Run2017B-Nano14Dec2018-v1/NANOAOD/FAE75F95-3C85-334A-939B-53495B8DB326_skimmed.root"),
#     ("SingleMuon_Run2017C", "/store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/5E9A6578-B5FA-0E4C-AC40-5BE6BB856802.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/SingleMuon/Run2017C-Nano14Dec2018-v1/NANOAOD/5E9A6578-B5FA-0E4C-AC40-5BE6BB856802_skimmed.root"),
#     ("SingleMuon_Run2017D", "/store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/21A3C033-D062-7745-9892-A1194A4547BF.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/SingleMuon/Run2017D-Nano14Dec2018-v1/NANOAOD/21A3C033-D062-7745-9892-A1194A4547BF_skimmed.root"),
#     ("SingleMuon_Run2017E", "/store/data/Run2017E/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/59331E0C-36C1-E040-A98C-61CCA3CA9109.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/SingleMuon/Run2017E-Nano14Dec2018-v1/NANOAOD/59331E0C-36C1-E040-A98C-61CCA3CA9109_skimmed.root"),
#     ("SingleMuon_Run2017F", "/store/data/Run2017F/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/42090D8D-9D80-3C42-8417-EA144FDFE785.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/SingleMuon/Run2017F-Nano14Dec2018-v1/NANOAOD/42090D8D-9D80-3C42-8417-EA144FDFE785_skimmed.root"),
    
#     ("SingleMuon_Run2018A", "/store/data/Run2018A/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/A88333E6-6D83-1E40-8047-458CEC301FAF.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/SingleMuon/Run2018A-Nano14Dec2018-v1/NANOAOD/A88333E6-6D83-1E40-8047-458CEC301FAF_skimmed.root"),
#     ("SingleMuon_Run2018B", "/store/data/Run2018B/SingleMuon/NANOAOD/Nano14Dec2018-v1/90000/8C2AE8D3-E2DA-524D-9F98-05FEA3DF3063.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/SingleMuon/Run2018B-Nano14Dec2018-v1/NANOAOD/8C2AE8D3-E2DA-524D-9F98-05FEA3DF3063_skimmed.root"),
#     ("SingleMuon_Run2018C", "/store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1/40000/CEE672D6-67F8-4941-A02C-C4A12E7BAA65.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/SingleMuon/Run2018C-Nano14Dec2018-v1/NANOAOD/CEE672D6-67F8-4941-A02C-C4A12E7BAA65_skimmed.root"),
#     ("SingleMuon_Run2018D", "/store/data/Run2018D/SingleMuon/NANOAOD/Nano14Dec2018_ver2-v1/20000/E8F54BB3-9E5B-7B4E-AE63-C25297ECC363.root",
#      "/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/SingleMuon/Run2018D-Nano14Dec2018_ver2-v1/NANOAOD/E8F54BB3-9E5B-7B4E-AE63-C25297ECC363_skimmed.root"),
    
    #("jme_check", "8C0C1B20-DFC2-2B49-AD49-3BDD07650DD6_jme_2017.root", "jme_2017.root"),
    ("jme_check", "5FA66B97-0267-B244-8761-3D1BE9F3428F_jme_2018.root", "jme_2018.root"),
    
  ]
  
  variables = [
  
#     ("Muon_pt",     100,   0,  300),
#     #("Muon_phi",    100,  -4,    4),
#     #("Muon_eta",    100,  -6,    6),
#     ("Electron_pt", 100,   0,  300),
#     #("Electron_phi",100,  -4,    4),
#     #("Electron_eta",100,  -6,    6),
#     ("Jet_pt",      100,   0,  300),
#     ("MET_pt",      100,   0,  300),
#     ("MET_phi",     100,  -4,    4),
#     ("LHE_Njets",    10, -10,   10),
    
    (("Jet_pt_nom[0]", "jpt_1"),  100,   0,  300),
    (("MET_pt_nom",    "met"  ),  100,   0,  300),
    
  ]
  
  outdir = "plots"
  tree1, tree2 = 'Events','Events'
  tree1, tree2 = 'Events','tree'
  plot   = True #and False
  
  for sample, file1, file2 in files:
      tag   = '_'+sample #file2.split('/')[-1]
      file1 = ensureDirector(file1)
      file2 = ensureDirector(file2)
      compareFiles(file1,file2,variables,tag=tag,outdir=outdir,tree1=tree1,tree2=tree2,plot=plot)
  


if __name__ == '__main__':
    print
    main()
    print
    

