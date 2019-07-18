## JEC and JER files

Instructions to use these files are given in the parent directory [`corrections`](..#jetmet-corrections).

The JES and JER files can be downloaded from
* <https://github.com/cms-jet/JECDatabase/raw/master/tarballs/>, see <https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC>
* <https://github.com/cms-jet/JRDatabase/tree/master/textFiles/>, see <https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution>


### How to get the text files and make a tarball

Use `svn` by replacing `tree/master` with `trunk` in the url:
```
svn checkout https://github.com/cms-jet/JRDatabase/trunk/textFiles/Fall17_25nsV1_MC Fall17_25nsV1_MC
cd Fall17_25nsV1_MC
rm -r .svn
tar -cvzf Fall17_25nsV1_MC.tar.gz *txt
```
