# Author: Izaak Neutelings (May 2019)
import os, re
modulepath = os.path.dirname(__file__)


def ensureDirectory(dirname):
    """Make directory if it does not exist."""
    if not os.path.exists(dirname):
      os.makedirs(dirname)
      print '>>> made directory "%s"'%(dirname)
      if not os.path.exists(dirname):
        print '>>> failed to make directory "%s"'%(dirname)
    return dirname
    

def getEra(filename,year):
    """Get era of data filename."""
    era = ""
    matches = re.findall(r"Run(201[678])([A-Z]+)",filename)
    if not matches:
      print "Warning! Could not find an era in %s"%filename
    elif year!=int(matches[0][0]):
      print "Warning! Given year does not match the data file %s"%filename
    else:
      era = matches[0][1]
    return era
    
