#! /usr/bin/env python

from argparse import ArgumentParser
from ROOT import TFile

parser = ArgumentParser()
parser.add_argument('samples',         type=str, action='store', nargs='+',
                                       help="sample to check" )
parser.add_argument('-n', '--nFiles',  dest='nFiles', action='store', type=int, default=-1,
                                       help="number of files" )
parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                                       help="set verbose" )
args = parser.parse_args()
import submit
from submit import getFileListDAS, getFileListDAS
submit.args = args


def main():
    
    samples = args.samples
    nFiles  = args.nFiles
    
    for sample in samples:
      
      print ">>> checking %s..."%(sample)
      
      if 'pnfs' in sample:
        files = getFileListPNFS(sample)
      else:
        files = getFileListDAS(sample)
      print ">>>   found %d files"%(len(files))
      max = nFiles if nFiles>0 else len(files)
      
      events = [ ]
      for filename in files[:max]:
        file = TFile.Open(filename, 'READ')
        if not file or not hasattr(file,'IsZombie'):
          print ">>>   Warning! Could not open file %s"%(filename)
          continue
        if file.IsZombie():
          print ">>>   Warning! Zombie file %s"%(filename)
          continue
        tree = file.Get('Events')
        if not tree:
          print ">>>   Warning! No tree in %s"%(filename)
          continue
        events.append((tree.GetEntries(),filename))
      
      print ">>> files ordered from smallest to largest number of events:"
      for nevents, filename in sorted(events):
        print ">>> %12d: %s"%(nevents,filename)
    


if __name__ == "__main__":
    
    print
    main()
    print "Done\n"
	

