#################################################################
# Split a tree in PreVFP and PostVFP based on run number branch #
#################################################################

import sys
import os
import argparse
import numpy as np
import uproot


if __name__=='__main__':

  inputfile = sys.argv[1]
  treename = sys.argv[2]
  prefile = sys.argv[3]
  postfile = sys.argv[4]

  # open input file and get tree
  with uproot.open(inputfile) as f:
    tree = f[treename]
    branches = tree.arrays(tree.keys(), library='np')

  # get the run number and make selection
  # threshold value comes from here: 
  # https://twiki.cern.ch/twiki/bin/view/CMS/PdmVDatasetsUL2016
  runnbs = branches['_runNb']
  threshold = 278769
  premask = (runnbs < threshold)
  postmask = (runnbs > threshold)
  preevents = {key: val[premask] for key,val in branches.items()}
  postevents = {key: val[postmask] for key,val in branches.items()}

  # printouts for testing
  print('Total number of events: {}'.format(len(runnbs)))
  print('Events in PreVFP: {}'.format(np.sum(premask)))
  print('Events in PostVFP: {}'.format(np.sum(postmask)))

  # write output files
  with uproot.recreate(prefile) as f:
    f[treename] = preevents
  with uproot.recreate(postfile) as f:
    f[treename] = postevents
