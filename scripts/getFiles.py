#! /usr/bin/env python
import sys
from argparse import ArgumentParser
from ROOT import TFile
sys.path.append('..')

parser = ArgumentParser()
parser.add_argument('samples',         type=str, action='store', nargs='+',
                                       help="sample to check" )
parser.add_argument('-n', '--nFiles',  dest='nFiles', action='store', type=int, default=-1,
                                       help="number of files" )
parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                                       help="set verbose" )
args = parser.parse_args()
import submit
from submit import getFileListPNFS, getFileListDAS
submit.args = args



def getROOTFiles(files,max=None):
    
    if max==None:
      max = len(files)
    
    eventstot = 0
    events    = [ ]
    badfiles  = [ ]
    for filename in files[:max]:
      file = TFile.Open(filename,'READ')
      if not file or not hasattr(file,'IsZombie'):
        print ">>>   Warning! Could not open file %s"%(filename)
        badfiles.append(filename)
        continue
      if file.IsZombie():
        print ">>>   Warning! Zombie file %s"%(filename)
        badfiles.append(filename)
        continue
      tree = file.Get('Events')
      if not tree:
        print ">>>   Warning! No tree in %s"%(filename)
        badfiles.append(filename)
        continue
      events.append((tree.GetEntries(),filename))
      eventstot += tree.GetEntries()
      file.Close()
    
    print ">>>   total events: %d"%(eventstot)
    print "\n>>> files ordered from smallest to largest number of events:"
    for nevents, filename in sorted(events):
      #print ">>> %12d: %s"%(nevents,filename)
      print ">>>  '%s', # %7d"%(filename,nevents)
    
    print ">>> "
    return badfiles
    


def main():
    
    samples = args.samples
    nFiles  = args.nFiles
    
    badfiles = [ ]
    for sample in samples:
      print ">>> checking %s..."%(sample)
      if 'pnfs' in sample:
        files = getFileListPNFS(sample)
      else:
        files = getFileListDAS(sample)
      print ">>>   found %d files"%(len(files))
      max = nFiles if nFiles>0 else len(files)
      badfiles += getROOTFiles(files,max=max)
    
    if badfiles:
      print "'>>> files with a problem:"
      for filename in sorted(badfiles):
        print ">>>      %s"%(filename)
    else:
      print ">>> no files with a problem found"
    print ">>> "
    


if __name__ == "__main__":
    
    print
    main()
    print ">>> done\n"
	

