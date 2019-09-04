#! /usr/bin/env python
# Authors: Yuta Takahashi & Izaak Neutelings (2018)
# Description: This postprocessor is used for local runs, to test the framework
#print
from postprocessors import modulepath, ensureDirectory
from postprocessors.config_jme import getEra
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-i', '--infiles',  dest='infiles',  action='store', type=str, default=[ ])
parser.add_argument('-o', '--outdir',   dest='outdir',   action='store', type=str, default=".")
parser.add_argument('-c', '--channel',  dest='channel',  action='store', choices=['tautau','mutau','eletau','mumu','elemu'], type=str, default='tautau')
parser.add_argument('-t', '--type',     dest='type',     action='store', choices=['data','mc'], default=None)
parser.add_argument('-y', '--year',     dest='year',     action='store', choices=[2016,2017,2018], type=int, default=2017)
parser.add_argument('-e', '--era',      dest='era',      action='store', type=str, default="")
parser.add_argument('-m', '--max',      dest='maxEvts',  action='store', type=int, default=None)
parser.add_argument('-T', '--tes',      dest='tes',      action='store', type=float, default=1.0)
parser.add_argument('-L', '--ltf',      dest='ltf',      action='store', type=float, default=1.0)
parser.add_argument('-J', '--jtf',      dest='jtf',      action='store', type=float, default=1.0)
parser.add_argument('-l', '--tag',      dest='tag',      action='store', type=str, default="")
parser.add_argument('-M', '--Zmass',    dest='Zmass',    action='store_true',  default=False)
parser.add_argument('-Z', '--doZpt',    dest='doZpt',    action='store_true',  default=False)
parser.add_argument('-R', '--doRecoil', dest='doRecoil', action='store_true',  default=False)
parser.add_argument(      '--no-jec',   dest='doJEC',    action='store_false', default=True)
parser.add_argument(      '--jec-sys',  dest='doJECSys', action='store_true',  default=None)
args = parser.parse_args()

channel       = args.channel
outdir        = ensureDirectory(args.outdir)
year          = args.year
era           = args.era
dataType      = args.type
infiles       = args.infiles
maxEvts       = args.maxEvts
args.doJECSys = args.tes==1 and args.ltf==1 and args.jtf==1 if args.doJECSys==None else args.doJECSys
if args.tag and args.tag[0]!='_': args.tag = '_'+args.tag
postfix  = "%s/%s_%s%s.root"%(outdir,channel,year,args.tag)
kwargs = {
  'year':        args.year,
  'era':         args.era,
  'tes':         args.tes,
  'ltf':         args.ltf,
  'jtf':         args.jtf,
  'doZpt':       args.doZpt,
  'doRecoil':    args.doRecoil,
  'doJEC':       args.doJEC,
  'doJECSys':    args.doJECSys,
  'ZmassWindow': args.Zmass,
}

if isinstance(infiles,str):
  infiles = infiles.split(',')
if infiles:
  if not dataType:
    if infiles and 'SingleMuon' in infiles[0] or "/Tau/" in infiles[0] or 'SingleElectron' in infiles[0] or 'EGamma' in infiles[0]:
      dataType = 'data'
    else:
      dataType = 'mc'
else:
  if not dataType:
    dataType = 'mc'
  if dataType=='data':
    if year==2016:
      if channel in ['mutau','elemu','mumu']:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/9DC46213-FB51-5347-89A4-4FF02435B663.root', #    3457
          'root://xrootd-cms.infn.it//store/data/Run2016F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/705EBC01-6F4A-F943-9834-64387A0D5480.root', #   41623
          'root://xrootd-cms.infn.it//store/data/Run2016G/SingleMuon/NANOAOD/Nano14Dec2018-v1/00000/57E51EC1-15B2-AC46-9D69-32C4FAC9E94B.root',  #   14731
          #'root://xrootd-cms.infn.it//store/data/Run2016H/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/152878C4-A061-9048-9739-F46D95A2D975.root',  #   80513
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/2DB769EC-677C-AE40-9DDC-0779DFA63C1B.root',  #   23917
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/82567C99-BA85-4B4C-B2F9-FBB86412DC99.root',  #  127126
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/6A0AC5DD-83F5-954D-81CF-C825E7ABD6EE.root', #  505313
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/4913A5BF-28E2-E74B-B7D5-6C48675251D5.root', # 1007425
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/0173E504-EA31-9A47-91C5-C9275D97F857.root', # 2070856
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/5E0D3E5D-F3CA-634C-96AB-E4EE60F7696F.root', # 4965165
          #'root://xrootd-cms.infn.it//store/data/Run2016F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/F972BC9B-9921-144F-8F98-595D13C6704F.root', # 1386994
          #'root://xrootd-cms.infn.it//store/data/Run2016F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/C479CC7A-1EE8-F248-9F59-405463FDDFD2.root', # 2011005
          #'root://xrootd-cms.infn.it//store/data/Run2016F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/51FD4C9D-439D-4640-ABDB-4B114D4CD609.root', # 3296522
          #'root://xrootd-cms.infn.it//store/data/Run2016G/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/AC99D058-E037-444D-8C3A-FDDBA67D6679.root',  #  106111
          #'root://xrootd-cms.infn.it//store/data/Run2016G/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/E70046B1-F06B-FE46-BD8C-827AF85057B9.root',  # 1159217
          #'root://xrootd-cms.infn.it//store/data/Run2016H/SingleMuon/NANOAOD/Nano14Dec2018-v1/90000/84BFF2B9-585A-EB4F-8FD2-6AB790CB45D4.root',  #  124789
          #'root://xrootd-cms.infn.it//store/data/Run2016H/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/C262DA69-257B-A94E-AFBF-DE9B547618E8.root',  # 1012728
        ]
      elif channel=='eletau':
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2016C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/818A7503-6954-B947-AC2D-CFA8E52F17FC.root',  #  561867
          'root://xrootd-cms.infn.it//store/data/Run2016G/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/0FE6DEF4-4573-C543-B7A6-55F77A444CD6.root',  #    8642
          'root://xrootd-cms.infn.it//store/data/Run2016H/SingleElectron/NANOAOD/Nano14Dec2018-v1/80000/0D190EC8-21F3-7C4B-B490-EA8164D3DE1C.root',  #   97845
          #'root://xrootd-cms.infn.it//store/data/Run2016E/SingleElectron/NANOAOD/Nano14Dec2018-v1/280000/73A427C9-BA4C-774E-88A1-6199CE4E82A0.root', #  180978
          #'root://xrootd-cms.infn.it//store/data/Run2016F/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/04669647-35BB-2A42-A759-24A6A1F4C0E0.root',  #  234903
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleElectron/NANOAOD/Nano14Dec2018-v1/00000/5EB0A0C7-B8B1-6C48-8F7A-21910E7BC729.root',  #  848593
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleElectron/NANOAOD/Nano14Dec2018-v1/00000/0BAAA253-0C6C-7E44-B661-BAAB6818B63F.root',  # 1028257
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/1961B3E9-84DD-DE4B-AB12-F6F95925C463.root',  # 2017705
          #'root://xrootd-cms.infn.it//store/data/Run2016C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/D555DE64-01FA-324B-B898-F9FD72AE046B.root',  # 3010509
          #'root://xrootd-cms.infn.it//store/data/Run2016E/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/26800340-E06F-744F-9577-197D44909958.root',  #  216347
          #'root://xrootd-cms.infn.it//store/data/Run2016E/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/D5DEB1E5-EE3B-F14D-BA5B-0BA2EB8E1801.root',  # 1102228
          #'root://xrootd-cms.infn.it//store/data/Run2016F/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/16522F78-F805-4644-8353-67D7034C8E97.root',  #  579875
          #'root://xrootd-cms.infn.it//store/data/Run2016F/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/973A5084-79AD-7344-90A3-F1725F3EB905.root',  # 1351452
          #'root://xrootd-cms.infn.it//store/data/Run2016G/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/B26A8D2E-3BB4-394D-9A1B-4E8D5AF5161F.root',  #  460131
          #'root://xrootd-cms.infn.it//store/data/Run2016G/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/7755F8E5-1782-5541-9373-945A8B4DD26A.root',  # 1007053
          #'root://xrootd-cms.infn.it//store/data/Run2016H/SingleElectron/NANOAOD/Nano14Dec2018-v1/80000/DBC2CD0B-47E0-914A-84BC-F02FE7FA5FFD.root',  #  556163
          #'root://xrootd-cms.infn.it//store/data/Run2016H/SingleElectron/NANOAOD/Nano14Dec2018-v1/80000/E5197BDA-4A01-3942-9D27-8C88FE272526.root',  # 1043998
        ]
      else:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2016D/Tau/NANOAOD/Nano14Dec2018-v1/280000/4DF248CA-BF9D-634A-8FC8-E8A19B6B112F.root', #  284643
          #'root://xrootd-cms.infn.it//store/data/Run2016C/Tau/NANOAOD/Nano14Dec2018-v1/80000/5786DD17-39DE-AF4C-A995-E929E6761908.root',  #  975129
          #'root://xrootd-cms.infn.it//store/data/Run2016H/Tau/NANOAOD/Nano14Dec2018-v1/90000/54987BB8-6019-6D4E-9E81-43C26C6F5E3B.root',  #  852034
          #'root://xrootd-cms.infn.it//store/data/Run2016C/Tau/NANOAOD/Nano14Dec2018-v1/80000/B7F7955D-8540-6B4D-8D19-CFBCDDEBFF8B.root',  # 1056337
          #'root://xrootd-cms.infn.it//store/data/Run2016C/Tau/NANOAOD/Nano14Dec2018-v1/80000/BC6F1760-F079-DC4A-8BB3-2BAEEB3DE596.root',  # 3129062
          #'root://xrootd-cms.infn.it//store/data/Run2016D/Tau/NANOAOD/Nano14Dec2018-v1/80000/C7095693-5E9B-4448-B864-8780E27EDB06.root',  #  408052
          #'root://xrootd-cms.infn.it//store/data/Run2016D/Tau/NANOAOD/Nano14Dec2018-v1/280000/148DAEB7-9889-F540-91DD-C1641DDB12ED.root', # 1327493
          #'root://xrootd-cms.infn.it//store/data/Run2016F/Tau/NANOAOD/Nano14Dec2018-v1/90000/5CD178AA-DCDE-6341-9B9B-1C40D9713788.root',  # 1116498
          #'root://xrootd-cms.infn.it//store/data/Run2016F/Tau/NANOAOD/Nano14Dec2018-v1/90000/A3DAE6CA-3B69-724E-82E2-2CFA37E1B65E.root',  # 2038362
          #'root://xrootd-cms.infn.it//store/data/Run2016F/Tau/NANOAOD/Nano14Dec2018-v1/90000/5DA048FA-E667-EF4D-A410-436530B2094F.root',  # 3962621
          #'root://xrootd-cms.infn.it//store/data/Run2016H/Tau/NANOAOD/Nano14Dec2018-v1/90000/F2164880-6B4E-3943-BD37-23A39C3CC88F.root',  # 1177908
        ]
    elif year==2017:
      if channel in ['mutau','elemu','mumu']:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/8C0C1B20-DFC2-2B49-AD49-3BDD07650DD6.root',  #   10908
          'root://xrootd-cms.infn.it//store/data/Run2017F/SingleMuon/NANOAOD/Nano14Dec2018-v1/280000/5C980020-7798-7B4D-B7B5-54EAA473D79A.root', #   89470
          #'root://xrootd-cms.infn.it//store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/46665B58-B1DF-4641-9CFB-B72822DDD495.root',  #  439959
          #'root://xrootd-cms.infn.it//store/data/Run2017E/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/CC18ED10-8282-754F-846A-F0D05C855BD3.root',  #  571009
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/03ADC41C-9ECC-9844-9048-A0F311ABE6FF.root',  #  536329
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleMuon/NANOAOD/Nano14Dec2018-v1/90000/46F89E46-758F-4F47-8827-8D55F40D9BDB.root',  #  998543
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/69D09690-949C-1244-BD49-769D4F5C35E2.root',  # 1066787
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/28580FFC-D1E3-D44F-ACB4-88D93C1302AD.root',  # 3673825
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/FBF3CF45-684A-BC49-A9D2-90E2ADC84464.root',  #  641842
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/30660B72-2981-D048-9DBD-DA640B21484D.root',  # 1183934
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/D06D1252-28B1-4C42-B268-D8A40D85D1B7.root',  # 3025734
          #'root://xrootd-cms.infn.it//store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/B562A8FC-B2C3-5046-A29A-C10E74A8D476.root',  # 1070092
          #'root://xrootd-cms.infn.it//store/data/Run2017E/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/B110FC65-83A9-E74B-BC9B-DC25E5276470.root',  # 1136462
        ]
      elif channel=='eletau':
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/35DC0682-783D-AF4A-A1CE-3D9F82894551.root',  #     589
          'root://xrootd-cms.infn.it//store/data/Run2017D/SingleElectron/NANOAOD/Nano14Dec2018-v1/20000/E569EA42-5595-474D-BCB9-BF3AD79B9859.root',  #   92298
          'root://xrootd-cms.infn.it//store/data/Run2017E/SingleElectron/NANOAOD/Nano14Dec2018-v1/20000/EC9A71F9-4BBB-DD47-80B4-8D0F5CA40E02.root',  #   47941
          'root://xrootd-cms.infn.it//store/data/Run2017F/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/23DD615C-1DDC-7245-9BD4-6A51D326DE85.root',  #   46868
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleElectron/NANOAOD/Nano14Dec2018-v1/20000/D6BC55CC-0849-3D45-8376-DF514CC23440.root',  #  732393
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleElectron/NANOAOD/Nano14Dec2018-v1/20000/D34D7EAC-50D9-134B-A1BD-C5B92A43A90A.root',  # 1159333
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleElectron/NANOAOD/Nano14Dec2018-v1/20000/2F692FE7-3162-7A47-8D50-9E40C2E4FE3A.root',  # 2039019
          #'root://xrootd-cms.infn.it//store/data/Run2017B/SingleElectron/NANOAOD/Nano14Dec2018-v1/20000/9D19FB14-4049-F34D-9C5C-B94A3E518D19.root',  # 3204947
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/E2B1106E-2614-3443-8516-A651A11C0DB2.root',  #  155069
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/84CACF7E-4582-DD4C-850C-0E06988F4220.root',  #  274934
          #'root://xrootd-cms.infn.it//store/data/Run2017C/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/8F9DAF84-85B6-7D49-AD45-8FB799680D2B.root',  # 1107036
          #'root://xrootd-cms.infn.it//store/data/Run2017D/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/5D8050E3-F1C8-5C44-BC53-DA47C99372B4.root',  #  173709
          #'root://xrootd-cms.infn.it//store/data/Run2017D/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/16B6E834-E2C0-F84A-B1F8-285C5E1510A4.root',  #  957003
          #'root://xrootd-cms.infn.it//store/data/Run2017D/SingleElectron/NANOAOD/Nano14Dec2018-v1/90000/38BB4776-B8AF-0447-816F-697072C038E1.root',  #  968126
          #'root://xrootd-cms.infn.it//store/data/Run2017E/SingleElectron/NANOAOD/Nano14Dec2018-v1/280000/3561AB6B-BEC2-FF46-85E1-4733623BD59D.root', #  570088
        ]
      else:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2017B/Tau/NANOAOD/Nano14Dec2018-v1/20000/E81AD055-2B85-AB49-B44C-7EBCD3F3D1B6.root', #    8039
          'root://xrootd-cms.infn.it//store/data/Run2017F/Tau/NANOAOD/Nano14Dec2018-v1/10000/00F1A05B-D799-3840-8530-E7434C2DD196.root', #   26045
          #'root://xrootd-cms.infn.it//store/data/Run2017B/Tau/NANOAOD/Nano14Dec2018-v1/20000/0D5C052E-6E12-8D4E-8B8E-BEC2C33C507C.root', #  476575
          #'root://xrootd-cms.infn.it//store/data/Run2017B/Tau/NANOAOD/Nano14Dec2018-v1/20000/9F9A0D5C-E83A-F14C-B932-4DDC092E54FC.root', # 1194077
          #'root://xrootd-cms.infn.it//store/data/Run2017B/Tau/NANOAOD/Nano14Dec2018-v1/20000/5D68BD33-486F-7E44-B851-481437C29AE0.root', # 3042894
          #'root://xrootd-cms.infn.it//store/data/Run2017C/Tau/NANOAOD/Nano14Dec2018-v1/00000/8D9B5752-DD66-5F42-B227-C19C4954AF4D.root', #  294170
          #'root://xrootd-cms.infn.it//store/data/Run2017C/Tau/NANOAOD/Nano14Dec2018-v1/00000/3BDA0489-860D-5A41-B09E-6BFD03D1D8E4.root', # 1072601
          #'root://xrootd-cms.infn.it//store/data/Run2017D/Tau/NANOAOD/Nano14Dec2018-v1/20000/DA025253-B82B-AB4F-8F79-5C742A101291.root', #  875078
          #'root://xrootd-cms.infn.it//store/data/Run2017D/Tau/NANOAOD/Nano14Dec2018-v1/20000/C72D2688-2A74-9E49-B495-FFE1D4D876AE.root', # 1018170
          
        ]
    elif year==2018:
      if channel in ['mutau','elemu','mumu']:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/5FA66B97-0267-B244-8761-3D1BE9F3428F.root', #    6107
          'root://xrootd-cms.infn.it//store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/4FC2DBE0-183D-6A49-9E59-55B89D34A722.root', #   61529
          'root://xrootd-cms.infn.it//store/data/Run2018A/SingleMuon/NANOAOD/Nano14Dec2018-v1/20000/17CF17FF-ACE6-A944-9021-0C0FC9F25F9B.root', #   98698
          #'root://xrootd-cms.infn.it//store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1/40000/741DDE3C-CFE5-374C-801E-452B157FB94A.root', # 1154179
          #'root://xrootd-cms.infn.it//store/data/Run2018A/SingleMuon/NANOAOD/Nano14Dec2018-v1/40000/1A17C2F2-55E5-614D-9083-F6983F065380.root', # 1019856
          #'root://xrootd-cms.infn.it//store/data/Run2018B/SingleMuon/NANOAOD/Nano14Dec2018-v1/10000/8DCE3FFC-5EAD-FF48-8C5E-23033F6A39AF.root', #  690840
          #'root://xrootd-cms.infn.it//store/data/Run2018B/SingleMuon/NANOAOD/Nano14Dec2018-v1/90000/E1F89DDE-086F-8340-B7A9-A1B568130AC7.root', # 1022036
          #'root://xrootd-cms.infn.it//store/data/Run2018D/SingleMuon/NANOAOD/Nano14Dec2018_ver2-v1/20000/12AE335A-4458-2942-8E29-5E58ED742AEE.root', #   41820
          #'root://xrootd-cms.infn.it//store/data/Run2018D/SingleMuon/NANOAOD/Nano14Dec2018_ver2-v1/20000/832A8280-3EF2-D34E-8E62-EE9762445AF3.root', # 1023668
        ]
      elif channel in ['eletau']:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2018A/EGamma/NANOAOD/Nano14Dec2018-v1/50000/FAAD00AF-D164-C04C-87FC-9F55719421C5.root',  #    5136
          'root://xrootd-cms.infn.it//store/data/Run2018C/EGamma/NANOAOD/Nano14Dec2018-v1/30000/60016101-5033-DF45-80A8-9DF4880378BD.root',  #    8000
          'root://xrootd-cms.infn.it//store/data/Run2018D/EGamma/NANOAOD/Nano14Dec2018_ver2-v1/30000/4FFAE261-F1EF-5D49-9D97-C7921EBC0232.root',  #    4653
          #'root://xrootd-cms.infn.it//store/data/Run2018A/EGamma/NANOAOD/Nano14Dec2018-v1/80000/7F41F987-BDC0-6F46-916D-F3BD388938DC.root',  #    9694
          #'root://xrootd-cms.infn.it//store/data/Run2018A/EGamma/NANOAOD/Nano14Dec2018-v1/280000/8824D6B1-31D1-6B4C-A78E-F7EEE0C97013.root', #   11647
          #'root://xrootd-cms.infn.it//store/data/Run2018A/EGamma/NANOAOD/Nano14Dec2018-v1/270000/09F18ED8-A99F-EC40-B01E-1E92B0594EB1.root', #  105753
          #'root://xrootd-cms.infn.it//store/data/Run2018A/EGamma/NANOAOD/Nano14Dec2018-v1/30000/71568515-73E3-D749-8D69-FFC9419A8AA4.root',  # 1005146
          #'root://xrootd-cms.infn.it//store/data/Run2018A/EGamma/NANOAOD/Nano14Dec2018-v1/90000/2DDE598D-64DB-984E-81A6-672EB77EDA7D.root',  # 2060693
          #'root://xrootd-cms.infn.it//store/data/Run2018B/EGamma/NANOAOD/Nano14Dec2018-v1/20000/3C925E07-E4F2-D841-A7A8-5A93B0F0D63D.root',  # 1303591
          #'root://xrootd-cms.infn.it//store/data/Run2018C/EGamma/NANOAOD/Nano14Dec2018-v1/50000/53DDD0D2-FBB1-A549-B523-547FC122400F.root',  #   17506
          #'root://xrootd-cms.infn.it//store/data/Run2018C/EGamma/NANOAOD/Nano14Dec2018-v1/50000/C0586AC8-7A40-1D47-B59C-567EDE4488AE.root',  #   99871
          #'root://xrootd-cms.infn.it//store/data/Run2018C/EGamma/NANOAOD/Nano14Dec2018-v1/50000/72A4C264-E621-E749-881F-609BD4B3912C.root',  #  104382
          #'root://xrootd-cms.infn.it//store/data/Run2018D/EGamma/NANOAOD/Nano14Dec2018_ver2-v1/40000/FC924B52-57B2-A94A-9913-26C3202AE9BC.root',  #   20778
          #'root://xrootd-cms.infn.it//store/data/Run2018D/EGamma/NANOAOD/Nano14Dec2018_ver2-v1/110000/8A854EAE-83DA-8640-9A78-FA11222DB36A.root', #   74053
          #'root://xrootd-cms.infn.it//store/data/Run2018D/EGamma/NANOAOD/Nano14Dec2018_ver2-v1/110000/BE16779A-984A-1641-AB61-1631FE24A63D.root', #  109295
          #'root://xrootd-cms.infn.it//store/data/Run2018D/EGamma/NANOAOD/Nano14Dec2018_ver2-v1/280000/E808D2DF-B6C8-8E4C-833F-057528DB29A7.root', # 1263800
        ]
      else:
        infiles = [
          'root://xrootd-cms.infn.it//store/data/Run2018A/Tau/NANOAOD/Nano14Dec2018-v1/40000/EF19DF60-F32E-3343-82CA-C79A7FC80158.root',     #    1212
          'root://xrootd-cms.infn.it//store/data/Run2018B/Tau/NANOAOD/Nano14Dec2018-v1/80000/65F6D0A7-84B1-B14B-8ECD-8FE9F0FC8AC4.root',     #   18185
#           'root://xrootd-cms.infn.it//store/data/Run2018C/Tau/NANOAOD/Nano14Dec2018-v1/280000/D3DA2DE0-60BE-964F-AF46-38BBFC500B6D.root',    #    8070
#           'root://xrootd-cms.infn.it//store/data/Run2018A/Tau/NANOAOD/Nano14Dec2018-v1/40000/A273F86C-EEA5-A045-91C6-58FBC2709F06.root',     #    4732
#           'root://xrootd-cms.infn.it//store/data/Run2018A/Tau/NANOAOD/Nano14Dec2018-v1/50000/5CE993F1-C822-BA4D-A09F-865A39C859DE.root',     #   12462
          #'root://xrootd-cms.infn.it//store/data/Run2018A/Tau/NANOAOD/Nano14Dec2018-v1/280000/BBF7FF8D-0E03-1246-96A6-FB59F421DD96.root',    #  106907
          #'root://xrootd-cms.infn.it//store/data/Run2018A/Tau/NANOAOD/Nano14Dec2018-v1/280000/7FDF91AF-7C29-9247-A204-46894479D63C.root',    # 1006638
          #'root://xrootd-cms.infn.it//store/data/Run2018B/Tau/NANOAOD/Nano14Dec2018-v1/90000/05C42610-AAFE-2B4A-8ADF-4A2173E2A598.root',     #   31121
          #'root://xrootd-cms.infn.it//store/data/Run2018B/Tau/NANOAOD/Nano14Dec2018-v1/90000/5B559D87-B033-744D-94CF-10EAF03FCEE1.root',     #   53032
          #'root://xrootd-cms.infn.it//store/data/Run2018B/Tau/NANOAOD/Nano14Dec2018-v1/80000/53CA02B1-504B-AD44-A453-D1BEB49D2B41.root',     #  100288
          #'root://xrootd-cms.infn.it//store/data/Run2018B/Tau/NANOAOD/Nano14Dec2018-v1/80000/C4DEC04D-C287-8D4D-9FFF-0A48C28A5ED4.root',     # 1028177
          #'root://xrootd-cms.infn.it//store/data/Run2018C/Tau/NANOAOD/Nano14Dec2018-v1/40000/45068EB0-D2AD-D647-A432-E49ABB8CA372.root',     #  449136
          #'root://xrootd-cms.infn.it//store/data/Run2018C/Tau/NANOAOD/Nano14Dec2018-v1/40000/8C26A193-C377-5B4D-A4C5-4E87DBD07B29.root',     # 1008049
          #'root://xrootd-cms.infn.it//store/data/Run2018D/Tau/NANOAOD/Nano14Dec2018_ver2-v1/20000/3E9CB252-E7B6-6149-BBCC-4507C67A7A72.root' #  429924
          #'root://xrootd-cms.infn.it//store/data/Run2018D/Tau/NANOAOD/Nano14Dec2018_ver2-v1/20000/BA687E06-9300-124B-93DD-C99F79EC0CA3.root' #  857399
          #'root://xrootd-cms.infn.it//store/data/Run2018D/Tau/NANOAOD/Nano14Dec2018_ver2-v1/90000/81FD777F-1743-E94A-A958-F2352EE40B1C.root' # 1503207
        ]
  else:
    if year==2016:
        infiles = [
          'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/9D218D0A-1530-D246-8276-47C3A91FFBC3_skimmed.root', #   26252
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/E09772BC-2F9F-134B-976D-E4E64791B7E7_skimmed.root', #  182048
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/07293E5F-D70A-DD49-90F2-C9EA6E5D11AF_skimmed.root', #  442877
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/NANOAODSIM/2F904CF5-941A-5B47-819C-53BA3308007A_skimmed.root', #  887665
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2016/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/NANOAODSIM/47560595-D7E2-DD4D-989A-39EB01F213FA_skimmed.root', #  522739
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/47560595-D7E2-DD4D-989A-39EB01F213FA.root', #  522739
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/BEF8D775-B527-634D-8049-4CE5F091D665.root', #  760101
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/80000/023EF5F4-AFB1-564F-AA15-675AC8E3CDD0.root', # 1103428
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext2-v1/40000/9655C99D-1B7F-0D4C-AF8F-14B03E3732C8.root',
          #'root://xrootd-cms.infn.it//store/mc/RunIISummer16NanoAODv4/W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/40000/FCA16302-526D-784B-88C6-28421B7CCE19.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_LQ_nonres_2016_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_LQ_nonres_2016_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_LQ_pair_2016_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_LQ_pair_2016_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_LQ_single_2016_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_LQ_single_2016_5f_Madgraph_LO_M1000_1.root',
        ]
    elif year==2017:
        infiles = [
          'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/99/myNanoProdMc2017_NANO_998.root', #   83977
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/1C5D9C07-B3BA-254E-832D-89AD21C9F258_skimmed.root', #  109916
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/94D4274B-B7AE-3E4B-9F98-398C07A5B18D_skimmed.root', #  257903
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/FF440F9C-5EC7-CB4F-A75A-81A055F3A3BD_skimmed.root', #  757244
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM/6C947766-1461-104E-8300-9A27AB3A2B68_skimmed.root', # 1010557
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2017/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM/7CB6F5AC-0C1C-FC49-8898-F0601142D9BA_skimmed.root', #  843859
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/90000/946BE003-BA74-554C-81C4-98F9B4D41772.root',  #   83977
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/1C5D9C07-B3BA-254E-832D-89AD21C9F258.root', #  109916
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/280000/01CBA228-11A8-7848-8710-DF8CFEA1454E.root', #  169467
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_v3_102X_mc2017_realistic_v6_ext1-v1/80000/94D4274B-B7AE-3E4B-9F98-398C07A5B18D.root',  #  257903
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
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/100000/00E4EFFB-F496-E811-AC18-A4BF0112BD2A.root', #  4599
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/40000/FABEEF78-34A1-E811-A538-EC0D9A0B3360.root',  #  5843
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAOD/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/40000/18961888-34A1-E811-A230-00266CFFBED8.root',  # 29068
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LQ3ToTauB_Fall2017_5f_Madgraph_LO_pair-M500/nanoAOD/v1/nanoAOD_LQ3ToTauB_Fall2017_5f_Madgraph_LO_pair-M500_1602.root'
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000/nanoAOD/v1/nanoAOD_VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000_1036.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000/nanoAOD/v1/nanoAOD_VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000_105.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000/nanoAOD/v1/nanoAOD_VectorLQ3ToTauB_Fall2017_5f_Madgraph_LO_pair_M1000_1059.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_1.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_10.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_100.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_NonRes_5f_Madgraph_LO_M1000_101.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_1.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_10.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_100.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Pair_5f_Madgraph_LO_M1000_101.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_0.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_1.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_10.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_100.root',
          #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2017_LQ_Single_5f_Madgraph_LO_M1000_101.root',
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/SingleVectorLQ_InclusiveDecay_M-1000_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/280000/0A39C2EA-6216-8C44-91B6-5B6B2F334089.root', #  84000
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/SingleVectorLQ_InclusiveDecay_M-1000_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/280000/BD99C649-C5E7-D643-BCB7-2ED148297E78.root', # 905000
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/SingleVectorLQ_InclusiveDecay_M-2500_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/80000/2A0AF07C-DC2A-DB4F-A800-9889130CF9D5.root',  #  80000
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/SingleVectorLQ_InclusiveDecay_M-2500_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/80000/946A566B-5001-834B-999F-B9C94C122DC8.root',  #  84000
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/PairVectorLQ_InclusiveDecay_M-1000_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/00000/4F29BB0F-E041-1B42-98E1-CA0542B60CF5.root',
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/PairVectorLQ_InclusiveDecay_M-1000_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/40000/1D21AB6D-D603-994D-81FA-512FC5B5444C.root',
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/PairVectorLQ_InclusiveDecay_M-2500_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/80000/3D33C19F-1B26-BC4A-A84E-D68D46120797.root', # 301000
          #'root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/PairVectorLQ_InclusiveDecay_M-2500_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/80000/483DBAB3-4723-AA4B-8FB6-EF985DDD82BE.root', # 671000
        ]
    elif year==2018:
      infiles = [
        'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/109547CA-E528-6E47-95A0-B575447DEA1E_skimmed.root', #   29731
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/160142BE-A86B-C542-B223-B0957E1CEAA9_skimmed.root', #   72476
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/9A143B2D-E595-9147-A323-9C5818EC0CA0_skimmed.root', #  144358
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/072B9074-E8BF-A148-A2C2-7CF4FDFD0F8F_skimmed.root', #  551972
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM/1CFBAD3C-A38D-774E-8AA3-47068B7F7278_skimmed.root', #  721709
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/NANOAOD_2018/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/NANOAODSIM/70EC8A67-D08F-1240-97DA-768AEADB5C6B_skimmed.root', # 1254738
        #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/110000/70EC8A67-D08F-1240-97DA-768AEADB5C6B.root', # 1254738
        #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/110000/50C141E6-2191-1245-BB55-957902BB8AF2.root', # 1398323
        #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/70000/041BE5DF-8172-5844-96DD-346BB1D4564D.root', #  146996
        #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/70000/1FB0AB96-2400-5541-AC4F-E616DA7556FD.root', #  220019
        #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/60000/389BB9AA-F85B-0946-A707-2650EB8024D4.root', #  723015
        #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv4/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/70000/988A2893-AE4D-404E-8DAD-B1A8899A41A1.root', # 1101957
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/ytakahas/test_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_test_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_1.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_10.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_100.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_NonRes_5f_Madgraph_LO_M1000_101.root
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_1.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_10.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_100.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Pair_5f_Madgraph_LO_M1000_101.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_0.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_1.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_10.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_100.root',
        #'dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/rdelburg/LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000/nanoAOD/v1/nanoAOD_LegacyRun2_2018_LQ_Single_5f_Madgraph_LO_M1000_101.root',
      ]

if dataType=='data' and era=="" and infiles:
  kwargs['era'] = getEra(infiles[0],year)

print '-'*80
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = '%s'"%('channel',channel)
print ">>> %-10s = %s"  %('year',kwargs['year'])
print ">>> %-10s = '%s'"%('era',kwargs['era'])
print ">>> %-10s = '%s'"%('dataType',dataType)
print ">>> %-10s = %s"  %('maxEvts',maxEvts)
print ">>> %-10s = %s"  %('infiles',infiles)
print '-'*80

if channel=='tautau':
    from modules.ModuleTauTau import *
    module2run = lambda: TauTauProducer(postfix, dataType, **kwargs)
elif channel=='mutau':
    from modules.ModuleMuTau import *
    #from modules.ModuleMuTau_check import *
    module2run = lambda: MuTauProducer(postfix, dataType, **kwargs)
elif channel=='eletau':
    from modules.ModuleEleTau import *
    module2run = lambda: EleTauProducer(postfix, dataType, **kwargs)
elif channel=='mumu':
    from modules.ModuleMuMu import *
    module2run = lambda: MuMuProducer(postfix, dataType, **kwargs)
elif channel=='elemu':
    from modules.ModuleEleMu import *
    module2run = lambda: EleMuProducer(postfix, dataType, **kwargs)
else:
    print 'Invalid channel name'

p = PostProcessor(".", infiles, None, noOut=True, modules=[module2run()], postfix=postfix, maxEntries=maxEvts)
p.run()
print
