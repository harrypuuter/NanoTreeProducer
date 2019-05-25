# Postprocessing of nanoAOD

## Locally
For a **local run**, do something like
```
./postprocessors/local.py -c mutau -y 2017
```


## Batch

`job.py` is meant for job submission with [submit.py](../submit.py).


## Reduced examples

### Simple analysis example

A simple example of a postprocessor with a simple analysis code in [modules/ModuleSimple.py](modules/ModuleSimple.py) can be run as
```
./postprocessors/simple_example.py
```


### Simple example of skimming

A simple example of a postprocessor that skims a nanoAOD file, by applying a simple preselection and selecting branches, can be found in
```
./postprocessors/skim_example.py
```


### Official examples

Official examples can by found in <https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples>
