# Postprocessing of nanoAOD


## Official examples

Official examples can by found in <https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples>


## Simple example of skimming

A simple example of a postprocessor that skims a nanoAOD file by applying a simple preselection and selecting branches, can be found in
```
./skim_example.py
```
Both the input and output files are of the nanoAOD format.


## Simple analysis example

A simple example of a postprocessor with a simple analysis code in [modules/ModuleSimple.py](modules/ModuleSimple.py) can be run as
```
./simple_example.py
```
The input file should be in the nanoAOD format. The output file will be created by the analysis module itself (`TreeProducerSimple`), as opposed to the postprocessor, which is has setting `noOut=True`. The output file contains a custom tree with variables needed for the analysis.


## Example of applying jet/MET corrections

There are two example postprocessors that apply jet/MET corrections meant for local testing.
* `jme_test_central.py` uses the [official JME tools](https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/modules/jme), has output in the nanoAOD format.
* `jme_test_custom.py` uses the JME tools in of this framework ([corrections/JetMETCorrectionTool.py](../corrections/JetMETCorrectionTool.py)), has a custom analysis output according to [modules/ModuleSimpleJME.py](../modules/ModuleSimpleJME.py).


## Complete example of skimming

`skim.py` is a complete example of skimming of Run-II samples, including selecting data in the JSON (good run list), dropping unwanted branches, and applying latest JECs. It is meant to be submitted by [submit_skim.py](../submit_skim.py).
```
./skim.py -y 2017
```


## Local analysis
For a **local run** of the ditau analysis in Run II, do something like
```
./local.py -c mutau -y 2017
```


## Full analysis

`job.py` is a complete ditau analysis in Run-II, and is meant for job submission with [submit.py](../submit.py).
```
./job.py -c mutau -y 2017 -i root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/260000/CFDCF0D4-A3BD-E04B-89D5-1BE152CB8754.root
```
