#################################################################
# Split a tree in PreVFP and PostVFP based on run number branch #
#################################################################

import sys
import os
import argparse
import numpy as np
import uproot


if __name__=='__main__':

  # read command line arguments
  parser = argparse.ArgumentParser( description = 'Split trees in PreVFP and PostVFP' )
  parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
  parser.add_argument('-t', '--treenames', required=True, nargs='+')
  parser.add_argument('--prefile', required=True)
  parser.add_argument('--postfile', required=True)
  args = parser.parse_args()

  # loop over treenames
  for i,treename in enumerate(args.treenames):

    # open input file and read tree
    with uproot.open(args.inputfile) as f:
      print('Reading tree {}...'.format(treename))
      tree = f[treename]
      branches = tree.arrays(tree.keys(), library='np')

    # get the run number and make selection
    # threshold value comes from here: 
    # https://twiki.cern.ch/twiki/bin/view/CMS/PdmVDatasetsUL2016
    print('Splitting tree {}...'.format(treename))
    runnbs = branches['_runNb']
    threshold = 278769
    premask = (runnbs < threshold)
    postmask = (runnbs >= threshold)
    preevents = {key: val[premask] for key,val in branches.items()}
    postevents = {key: val[postmask] for key,val in branches.items()}

    # printouts for testing
    print('  Total number of instances: {}'.format(len(runnbs)))
    print('  Instances in PreVFP: {}'.format(np.sum(premask)))
    print('  Instances in PostVFP: {}'.format(np.sum(postmask)))

    # write output files
    writefunction = uproot.recreate
    if i>0: writefunction = uproot.update
    with writefunction(args.prefile) as f:
      f[treename] = preevents
    with writefunction(args.postfile) as f:
      f[treename] = postevents
