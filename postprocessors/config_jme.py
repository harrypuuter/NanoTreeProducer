# Author: Izaak Neutelings (May 2019)
# Description: Configuration of JEC/JER versions
# Links:
#   https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
#   https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
#   https://github.com/cms-jet/JECDatabase/raw/master/tarballs/
#   https://github.com/cms-jet/JRDatabase/tree/master/textFiles/
#   https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/data/jme
#   https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/jetRecalib.py
#   https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/jetmetUncertainties.py
import re
from PhysicsTools.NanoAODTools.postprocessing.modules.jme import jetmetUncertainties
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertaintiesProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme import jetRecalib


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
    

def getJetCalibrationData(year,era=""):
    """Get JME calibrator for dataset of a given year and era."""
    calibrators = { }
    if year==2016:
      calibrators = {
        'BCD': jetRecalib.jetRecalib2016BCD,
        'EF':  jetRecalib.jetRecalib2016EF,
        'GH':  jetRecalib.jetRecalib2016GH,
      }
    elif year==2017:
      calibrators = {
        'B':  jetRecalib.jetRecalib2017B,
        'C':  jetRecalib.jetRecalib2017C,
        'DE': jetRecalib.jetRecalib2017DE,
        'F':  jetRecalib.jetRecalib2017F,
      }
    else:
      calibrators = {
        'A': jetRecalib.jetRecalib2018A,
        'B': jetRecalib.jetRecalib2018B,
        'C': jetRecalib.jetRecalib2018C,
        'D': jetRecalib.jetRecalib2018D,
      }
    for eraset in calibrators:
      if era in eraset:
        return calibrators[eraset]()
    raise "Could not find an appropiate calibrator for year %s and era %s..."%(year,era)
    

def getJetCalibrationMC(year):
    """Get JME calibrator for MC of a given year."""
    if year==2016:
      jetmetUncertainties2016 = lambda: jetmetUncertaintiesProducer('2016',"Summer16_07Aug2017_V11_MC",['Total'],redoJEC=True)
      return jetmetUncertainties2016
      #return jetmetUncertainties.jetmetUncertainties2016
    elif year==2017:
      jetmetUncertainties2017 = lambda: jetmetUncertaintiesProducer("2017", "Fall17_17Nov2017_V32_MC",['Total'],redoJEC=True)
      return jetmetUncertainties2017
      #return jetmetUncertainties.jetmetUncertainties2017
    else:
      jetmetUncertainties2018 = lambda: jetmetUncertaintiesProducer("2018", "Autumn18_V8_MC",['Total'],redoJEC=True)
      return jetmetUncertainties2018
      #return jetmetUncertainties.jetmetUncertainties2018
    
