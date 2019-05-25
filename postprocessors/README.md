# Postprocessing of nanoAOD

## Locally
For a **local run**, do something like
```
./postprocessors/local.py -c mutau -y 2017
```


## Batch

For job submission, you need to modify the list of samples you want to process in the config file, e.g.
```
samples_2017.cfg
```
and then do, **submit** with something like
```
./submit.py -c mutau -y 2017
```
To **check job success**, you need to ensure that all the output file contains the expected tree with the expected number of events (`-d`):
```
./checkFiles.py -c mutau -y 2017 -d
```
If the output is fine, one can hadd (`-m`) all the output:
```
./checkFiles.py -c mutau -y 2017 -m
```
Use the `-o` option for the desired output directory, or edit `samplesdir` in `checkFiles.py` to set your default one.

To **resubmit failed jobs**, do:
```
./resubmit.py -c mutau -y 2017
```
Note: this submission works for the Sun Grid Engine (SGE) system of PSI Tier3 with `qsub`. For other batch systems, one needs to create their own version of `submit.sh` and `psibatch_runner.sh`.


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
