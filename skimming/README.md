# Skim ntuples

Scripts for skimming ntuples, i.e. for reducing the file size by removing events that do not specify the event selection (Z -> mu+ mu-) and by removing branches that are not needed in further steps of the analysis.

### How to use
The heavy lifting is done in `skim_ztomumu.cc`. Compile it using `make -f make_skim_ztomumu` (after having set a suitable CMSSW environment with `cmsenv`) and run it using `./skim_ztomumu [inputfile] [outputfile]`.

The script `skim_submit.py` can be used to run the skimming over a collection of samples. See the comments in the script for more info, and run `python skim_submit.py -h` for a list of required and available command line arguments.

The script `merge.py` can be used to merge the files resulting from the skimming step, to obtain one file per sample. However, it is probably better to skip merging at this stage and only do the merging after the next step in the analysis (see the `v0building` folder) to have a better parallellized workflow.

### On CMSSW releases
This code does not depend on the specifics of a CMSSW release.
However, a CMSSW release should still be sourced before compiling to have access to shared software.
It does not really matter which one; both `10_6_X` (with `python2`) and `12_X` (with `python3`) should work.
Note: the CMSSW version defined in the `skim_submit.py` script must match the one against which the `./skim_ztomumu` executable has been compiled, else the jobs will fail with strange error messages.
