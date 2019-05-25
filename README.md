# NanoTreeProducer
Produce skimmed analysis trees directly from centrally-produced NanoAOD.
This repository is meant for an analysis with a pair of tau leptons in several final states, and for 2016, 2017 and 2018 data.


## Installation

First, install `NanoAODTools`:
```
cmsrel CMSSW_9_4_6
cd CMSSW_9_4_6/src
cmsenv
git cms-init   #not really needed unless you later want to add some other cmssw stuff
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
scram b
```

Then, install this `NanoTreeProducer`:
```
git clone https://github.com/IzaakWN/NanoTreeProducer
```

In case you use [lepton scale factors and efficiencies from the HTT group](https://github.com/CMS-HTT/LeptonEfficiencies), you will also need to get
```
cd corrections/leptonEfficiencies
git clone https://github.com/CMS-HTT/LeptonEfficiencies HTT
```

And if you want to use [recoil corrections of the MET](https://github.com/CMS-HTT/RecoilCorrections/blob/master/instructions.txt) for W/Z/Higgs samples:
```
cd ${CMSSW_BASE}/src
git clone https://github.com/CMS-HTT/RecoilCorrections.git HTT-utilities/RecoilCorrections 
scram b
```

Each time you want to run the code in a new shell session, do
```
cd CMSSW_9_4_6/src
cmsenv
source setupEnv.sh
```



## Analysis

You need to change the **analyse code** in the modules and **tree branches** for the analysis you want to perform.
These are the examples for an analysis selecting for a muon and tau:
```
ModuleMuTau.py
TreeProducerMuTau.py
TreeProducerCommon.py
```


## Run

### Locally
For a **local run**, do something like
```
./postprocessors/local.py -c mutau -y 2017
```


### Batch

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


### Examples

A simple example of a postprocessor with a simple analysis code in [modules/ModuleSimple.py](modules/ModuleSimple.py) can be run as
```
./postprocessors/simple_example.py
```

A simple example of a postprocessor that skims a nanoAOD file, by applying a simple preselection and selecting branches, can be found in
```
./postprocessors/skim_example.py
```

Official examples can by found in <https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/python/postprocessing/examples>


## Notes

### NanoAOD

* **working book**: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
* **2016 `9_4_X`**: https://cms-nanoaod-integration.web.cern.ch/integration/master/mc94X2016_doc.html
* **2017 `9_4_X`**: https://cms-nanoaod-integration.web.cern.ch/integration/master/mc94X_doc.html
* **2018 `10_2_X`**: https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html

More [notes](https://www.evernote.com/l/Ac8PKYGpaJxJArj4eng5ed95_wvpzwSNTgc).


### Samples

[PPD Run II summary table](https://docs.google.com/presentation/d/1YTANRT_ZeL5VubnFq7lNGHKsiD7D3sDiOPNgXUYVI0I/edit#slide=id.g4dfd66f53d_1_7)
* **2016**: [list](https://github.com/IzaakWN/NanoTreeProducer/blob/master/samples_2016.cfg), [DAS](https://cmsweb.cern.ch/das/request?view=plain&limit=50&instance=prod%2Fglobal&input=dataset%3D%2F*%2FRunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic*%2FNANOAODSIM), [notes](https://www.evernote.com/l/Ac9nVeF2tcdJI7R-is1KPT2Ukv7A260zNX0)
* **2017**: [list](https://github.com/IzaakWN/NanoTreeProducer/blob/master/samples_2017.cfg), [DAS](https://cmsweb.cern.ch/das/request?view=plain&limit=50&instance=prod%2Fglobal&input=dataset+dataset%3D%2F*%2F*94X*_realistic_v14*%2FNANOAOD*), [notes](https://www.evernote.com/l/Ac8WfL3Mzx1MrKdm1LfIOl-F-j7NeScPKxs)
* **2018**: [list](https://github.com/IzaakWN/NanoTreeProducer/blob/master/samples_2018.cfg), [DAS](https://cmsweb.cern.ch/das/request?view=plain&limit=50&instance=prod%2Fglobal&input=%2F*%2FRunIIAutumn18NanoAODv4-Nano14Dec2018*%2FNANOAODSIM), [notes](https://www.evernote.com/l/Ac9yyi7wtg9LaYgxOIz11jFyzLV0ztkemtE)


### Integrated luminosity

* **2016**: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2016Analysis#DATA
* **2017**: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis#DATA, [brilcalc](https://ineuteli.web.cern.ch/ineuteli/lumi/2017/)
* **2018**: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2018Analysis#DATA, [brilcalc](https://ineuteli.web.cern.ch/ineuteli/lumi/2018/)

JSON files are copied to the [`json`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/json) directory to prevent issues with connection to `/afs`.


### Pileup

* **2017**: [profiles](https://ineuteli.web.cern.ch/ineuteli/pileup/2017/)
* **2018**: [profiles](https://ineuteli.web.cern.ch/ineuteli/pileup/2018/)


### Corrections

Tools to apply corrections are available in [corrections](corrections).

