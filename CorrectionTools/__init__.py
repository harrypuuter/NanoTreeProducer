import os
from ROOT import TFile, TH1
modulepath = os.path.dirname(__file__)
print modulepath

def ensureTFile(filename,option='READ'):
  """Open TFile, checking if the file in the given path exists."""
  if not os.path.isfile(filename):
    print '>>> ERROR! ScaleFactorTool.ensureTFile: File in path "%s" does not exist!'%(filename)
    exit(1)
  file = TFile(filename,option)
  if not file or file.IsZombie():
    print '>>> ERROR! ScaleFactorTool.ensureTFile Could not open file by name "%s"'%(filename)
    exit(1)
  return file
  
def extractTH1(file,histname):
  """Get histogram from a file, and do SetDirectory(0)."""
  if not file or file.IsZombie():
    print '>>> ERROR! ScaleFactorTool.extractTH1 Could not open file!'
    exit(1)
  hist = file.Get(histname)
  if not hist:
    print '>>> ERROR! ScaleFactorTool.extractTH1: Did not find histogtam "%s" in file %s!'%(histname,file.GetName())
    exit(1)
  if isinstance(hist,TH1):
    hist.SetDirectory(0)
  return hist

def warning(string,**kwargs):
  """Print warning with color."""
  print "\033[1m\033[93m%sWarning!\033[0m\033[93m %s\033[0m"%(kwargs.get('pre',""),string)
