# V0 candidate building and selection

Scripts for selecting V0 candidates and calculating their properties.

### How to use
The basic script is `v0builder.py`. Run with `python3 v0builder.py -h` for a list of required and available command line arguments. Job submission over multiple files/samples can be done with `v0builder_submit.py`.

The selections are defined in `v0selections.py`

The script `merge.py` can be used to merge the files resulting from the v0building step, to obtain one file per sample. This is convenient for the following analysis steps.

### On CMSSW releases
This code does not depend on the specifics of a CMSSW release.
However, a CMSSW release should still be sourced before compiling to have access to shared software.
One has to use `12_X` (with `python3`) should work (specifically for the imports of `uproot` and `awkward`).
