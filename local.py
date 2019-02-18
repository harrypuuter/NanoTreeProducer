#!/usr/bin/env python
import os, sys
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-i', '--infiles',  dest='infiles', action='store', type=str, default=[ ])
parser.add_argument('-c', '--channel',  dest='channel', action='store', choices=['tautau','mutau','eletau','elemu','mumu'], type=str, default='tautau')
parser.add_argument('-t', '--type',     dest='type', action='store', choices=['data','mc'], default='mc')
parser.add_argument('-y', '--year',     dest='year', action='store', choices=[2016,2017,2018], type=int, default=2017)
parser.add_argument('-T', '--tes',      dest='tes', action='store', type=float, default=1.0)
parser.add_argument('-L', '--ltf',      dest='ltf', action='store', type=float, default=1.0)
parser.add_argument('-l', '--tag',      dest='tag', action='store', type=str, default="")
parser.add_argument('-Z', '--doZpt',    dest='doZpt', action='store_true', default=False)
parser.add_argument('-R', '--doRecoil', dest='doRecoil', action='store_true', default=False)
args = parser.parse_args()

channel  = args.channel
year     = args.year
dataType = args.type
infiles  = args.infiles
if args.tag and args.tag[0]!='_': args.tag = '_'+args.tag
postfix  = channel + args.tag + '.root'
kwargs = {
  'year':     args.year,
  'tes':      args.tes,
  'ltf':      args.ltf,
  'doZpt':    args.doZpt,
  'doRecoil': args.doRecoil,
}

if isinstance(infiles,str):
  infiles = infiles.split(',')
if infiles:
  dataType = 'mc'
  if infiles[0].find("/SingleMuon/")!=-1 or infiles[0].find("/Tau/")!=-1 or infiles[0].find("/SingleElectron/")!=-1:
    dataType = 'data'
else:
  if dataType=='data':
    if year==2016:
      if channel=='mutau':
        infiles = [
          ###'root://xrootd-cms.infn.it//store/data/Run2016B_ver1/SingleMuon/NANOAOD/Nano14Dec2018_ver1-v1/90000/87B8F064-C966-FD4F-BD32-E1FCB470AC7B.root',
          'root://xrootd-cms.infn.it//store/data/Run2016E/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/9DD2B819-9BE0-844E-8E12-6C0BCCBAF0E3.root',
          ###'root://xrootd-cms.infn.it//store/data/Run2016G/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/4BBB9D59-04A9-6241-9A92-C00B53E6D241.root',
          ###'root://xrootd-cms.infn.it//store/data/Run2016H/SingleMuon/NANOAOD/Nano14Dec2018-v1/90000/C6500BE6-28D9-7E46-A520-78C627F2E67E.root',
        ]
      else:
        infiles = [
          ###'root://xrootd-cms.infn.it//store/data/Run2016B_ver1/Tau/NANOAOD/Nano14Dec2018_ver1-v1/20000/5CB7D478-B9E8-6A48-8393-EC6C6412B2D3.root',
          'root://xrootd-cms.infn.it//store/data/Run2016E/Tau/NANOAOD/Nano14Dec2018-v1/10000/0ED24CE7-B408-BD48-8551-BFB7EAD2F4EB.root',
          ###'root://xrootd-cms.infn.it//store/data/Run2016E/Tau/NANOAOD/Nano14Dec2018-v1/10000/79A93CBE-80B7-8F4C-ADAF-0B97E1049397.root',
          ###'root://xrootd-cms.infn.it//store/data/Run2016H/Tau/NANOAOD/Nano14Dec2018-v1/90000/F39817D2-E1F1-4046-B45A-65B42945C313.root',
        ]
    elif year==2017:
      if channel=='mutau':
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/31Mar2018-v1/100000/EC085F70-1A64-E811-A184-003048F2E8C2.root', #    4686
          'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/31Mar2018-v1/30000/3666FB57-B255-E811-BC5F-1866DA7F7AC2.root',  #   43637
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/31Mar2018-v1/30000/DCA41AD0-A752-E811-A430-44A8420CC940.root',  # 1878250
        ]
      elif channel=='eletau':
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/31Mar2018-v1/70000/B49726E9-2C47-E811-A3A5-0CC47A745282.root', #   88572
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/31Mar2018-v1/70000/3213D26F-2046-E811-B06C-0CC47A4C8E22.root', #  950133
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/31Mar2018-v1/70000/C28E7FB2-4345-E811-AEB0-02163E017FF5.root', # 3094290
        ]
      else:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2017B/Tau/NANOAOD/31Mar2018-v1/10000/04463969-D044-E811-8DC1-0242AC130002.root'
        ]
    elif year==2018: 
        infiles = [
          'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/SingleMuon/Run2018A-from_17Sep2018_ver2-NanoAODv4Priv/181216_124906/0000/myNanoRunData2018ABC_NANO_352.root',
          ###'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/SingleMuon/Run2018B-from_17Sep2018_ver1-NanoAODv4Priv/181216_124922/0000/myNanoRunData2018ABC_NANO_212.root',
          ###'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/SingleMuon/Run2018D-from_PromptReco_ver2-NanoAODv4Priv/181216_124954/0000/myNanoRunData2018D_NANO_991.root',
        ]
  else:
    if year==2016:
        infiles = [
          'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/47560595-D7E2-DD4D-989A-39EB01F213FA.root', #  522739
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/BEF8D775-B527-634D-8049-4CE5F091D665.root', #  760101
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/023EF5F4-AFB1-564F-AA15-675AC8E3CDD0.root', # 1103428
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/F8B2DAE4-D2A7-584D-B55A-AC5CBA128EC8.root', # 1257893
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/7A7507D2-AF14-2B43-A7DD-BBE1F189125A.root', # 1413644
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext2-v1/40000/9655C99D-1B7F-0D4C-AF8F-14B03E3732C8.root',
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/40000/FCA16302-526D-784B-88C6-28421B7CCE19.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_LQ_nonres_2016_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_LQ_nonres_2016_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_LQ_pair_2016_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_LQ_pair_2016_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_LQ_single_2016_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_LQ_single_2016_5f_Madgraph_LO_M1000_1.root',
        ]
    elif year==2017:
        infiles = [
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/20000/16F5B835-C646-E811-825E-E0071B749CA0.root', #  69733
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/20000/D81B7BA0-3247-E811-8609-B499BAAC0270.root', #  83843
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/70000/B28E4243-3245-E811-B18F-001E67E71BAA.root', # 117636
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/20000/A456953E-4246-E811-8230-484D7E8DF051.root', # 165260
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/90000/1CEBB44E-4548-E811-8798-A4BF0115951C.root', # 212400
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/20000/E4D51829-5745-E811-92DD-E0071B74AC00.root', # 712312
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/70000/6040CB3C-3245-E811-A47A-E0071B73B6E0.root', # 906109
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/10000/0A5AB04B-4B42-E811-AD7F-A4BF0112BDE6.root']
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/20000/8E726150-8F42-E811-B862-001E67FA408C.root', # 623832
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/20000/82C67179-0942-E811-9BA7-001E67FA3920.root', # 953382
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/20000/44917CDB-2842-E811-852C-001E6739AD61.root', # 976374
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/20000/042667FA-1542-E811-B81A-001E673D23F9.root', # 998736
          'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/100000/00E4EFFB-F496-E811-AC18-A4BF0112BD2A.root', #  4599
          'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/40000/FABEEF78-34A1-E811-A538-EC0D9A0B3360.root',  #  5843
          'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/40000/18961888-34A1-E811-A230-00266CFFBED8.root',  # 29068
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LQ3ToTauB_Fall2017_5f_Madgraph_LO_pair-M500/nanoAOD/v1/nanoAOD_LQ3ToTauB_Fall2017_5f_Madgraph_LO_pair-M500_1602.root'
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000/nanoAOD/v1/nanoAOD_VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000_1036.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000/nanoAOD/v1/nanoAOD_VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000_105.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000/nanoAOD/v1/nanoAOD_VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000_1059.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_0.root',
        ]
    elif year==2018:
      infiles = [
        'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_731.root', #  18103
        #'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_132.root', # 136514
        #'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_176.root', # 136590
        #'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_513.root', # 136609
        #'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_101.root', # 137004
        #'root://xrootd-cms.infn.it//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver2/181216_125027/0000/myNanoRunMc2018_NANO_75.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_0.root',
      ]


print ">>> %-10s = %s"%('channel',channel)
print ">>> %-10s = %s"%('dataType',dataType)
print ">>> %-10s = %s"%('year',kwargs['year'])
print ">>> %-10s = %s"%('tes',kwargs['tes'])
print ">>> %-10s = %s"%('ltf',kwargs['ltf'])
print ">>> %-10s = %s"%('postfix',postfix)

if channel=='tautau':
    from TauTauModule import *
    module2run = lambda : TauTauProducer(postfix, dataType, **kwargs)
elif channel=='mutau':
    from MuTauModule import *
    module2run = lambda : MuTauProducer(postfix, dataType, **kwargs)
elif channel=='eletau':
    from EleTauModule import *
    module2run = lambda : EleTauProducer(postfix, dataType, **kwargs)
elif channel=='mumu':
    from MuMuModule import *
    module2run = lambda : MuMuProducer(postfix, dataType, **kwargs)
elif channel=='elemu':
    from EleMuModule import *
    module2run = lambda : EleMuProducer(postfix, dataType, **kwargs)
else:
    print 'Invalid channel name'

#p = PostProcessor(".",["../../../crab/WZ_TuneCUETP8M1_13TeV-pythia8.root"],"Jet_pt>150","keep_and_drop.txt",[exampleModule()],provenance=True)
p = PostProcessor(".", infiles, None, "keep_and_drop.txt", noOut=True, modules=[module2run()], provenance=False, postfix=postfix)
#p = PostProcessor(".",infiles,None,"keep_and_drop.txt",noOut=True, modules=[module2run()],provenance=False, jsonInput='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PromptReco/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt', postfix=postfix)

p.run()
