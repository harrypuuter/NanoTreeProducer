#! /usr/bin/env python
# Author: Izaak Neutelingsi (May 2019)
# Links:
#    https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM
#    https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2016Analysis
#    https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis
#    https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2018Analysis
#    /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt
#    /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt 
#    /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt
#    /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt
import json, re
import subprocess
#from multiprocessing import Process



def filterJSONByRunNumberRange(jsoninname,jsonoutname,start,end,verbose=False):
  """Split a given JSON file by start and end run number."""
  print ">>> filterJSONByRunNumberRange: %s %s - %s"%(jsonoutname,start,end)
  
  # READ JSON IN
  with open(jsoninname,'r') as jsonin:
    data = json.load(jsonin)
  
  # FILTER run number range
  nkeep = 0
  ndrop = 0
  for element in sorted(data.keys()):
    if element.isdigit():
      runnumber = int(element)
      if runnumber<start or runnumber>end:
        ndrop += 1
        if verbose: print "  dropping %s"%runnumber
        del data[element]
      else:
        nkeep += 1
        if verbose: print "  keeping %s"%runnumber
    else:
      print "Warning! filterJSONByRunNumberRange: element is not an integer (run number): '%s'"%element
  
  # WRITE JSON OUT
  with open(jsonoutname,'w') as jsonout:
    data = json.dump(data,jsonout,sort_keys=True)
  
  # SUMMARY
  print ">>>   saved %s / %s run numbers"%(nkeep,nkeep+ndrop)
  


lumipattern = re.compile(r"\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*[\d\.]+\s*\|\s*([\d\.]+)\s*\|")
def brilcalc(jsonnames,normtag,verbose=True):
  """Caluclate luminosity of a given JSON file."""
  
  if isinstance(jsonnames,str):
    jsonnames = [jsonnames]
  
  # START BRILCALC
  processes = [ ]
  print ">>> submitting jobs:"
  for jsonname in jsonnames:
    command = "brilcalc lumi --normtag %s -u /fb -i %s"%(normtag,jsonname)
    print ">>>   %s"%command
    process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    processes.append((jsonname,process))
  
  # COLLECT output
  luminosities = { }
  print ">>> waiting for jobs to finish..."
  for jsonname, process in processes:
    print ">>>   %s\n"%command
    luminosities[jsonname] = None
    retval = process.wait()
    stdout, stder = process.communicate()
    if 'Summary' not in stdout or verbose:
      print stdout
    else:
      summary = False
      for line in stdout.split('\n'):
        if "#Summary:" in line:
          summary = True
        elif summary:
          if "Check JSON" in line:
            break
          print line
          lumi = lumipattern.search(line)
          if lumi:
            luminosities[jsonname] = float(lumi.group(1))
      if not summary:
        print stdout
    print
    
  # SUMMARY
  print ">>> summary of total recorded luminosity:"
  print ">>>   %12s - %s"%("lumi [/fb]","JSON file")
  for jsonname in jsonnames:
    lumi = luminosities[jsonname]
    print ">>>   %12s - %s"%(lumi,jsonname)
  print "\n"
  


def main():
  
  normtag = "/cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json"
  
  jsonsets = [
    #("Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt",
    ("/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt",
      [("Run2016B",272007,275376),
       ("Run2016C",275657,276283),
       ("Run2016D",276315,276811),
       ("Run2016E",276831,277420),
       ("Run2016F",277772,278808),
       ("Run2016G",278820,280385),
       ("Run2016H",280919,284044),]),
    #("Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt",
    ("/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt",
      [("Run2017B",297020,299329),
       ("Run2017C",299337,302029),
       ("Run2017D",302030,303434),
       ("Run2017E",303435,304826),
       ("Run2017F",304911,306462),]),
    #("Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt",
    ("/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt",
      [("Run2018A",315252,316995),
       ("Run2018B",317080,319310),
       ("Run2018C",319337,320065),
       ("Run2018D",320673,325175),]),
  ]
  
  for jsonin, jsonset in jsonsets:
    print ">>> %s"%jsonin
    jsonouts = [ ]
    for run, start, end in jsonset:
      jsonout = jsonin.split('/')[-1]
      #jsonout = "%s.json"%(run)
      jsonout = re.sub(r"\d{6}-\d{6}",run,jsonout)
      filterJSONByRunNumberRange(jsonin,jsonout,start,end)
      jsonouts.append(jsonout)
    jsonouts.append(jsonin)
    brilcalc(jsonouts,normtag,False)
  


if __name__ == '__main__':
    print
    main()
    print
    

