# Postprocessing of nanoAOD

## Simple analysis example

A simple example of a postprocessor with a simple analysis code in [modules/ModuleSimple.py](modules/ModuleSimple.py) can be run as
```
./postprocessors/simple_example.py
```


## Simple example of skimming

A simple example of a postprocessor that skims a nanoAOD file, by applying a simple preselection and selecting branches, can be found in
```
./postprocessors/skim_example.py
```


## Official examples

Official examples can by found in <https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples>


## Locally
For a **local run** of the ditau analysis in Run II, do something like
```
./postprocessors/local.py -c mutau -y 2017
```


## Batch

`job.py` is a complete ditau analysis in Run-II, and is meant for job submission with [submit.py](../submit.py).


## Skimming

`skim.py` is a complete example of skimming of Run-II samples, including selecting data in the JSON (good run list), dropping unwanted branches, and applying latest JECs. It is meant to be submitted by [submit_skim.py](../submit_skim.py)

