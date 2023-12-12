###################################################
# Convenience looper over standard configurations #
###################################################

import os
import sys
import json
import argparse


if __name__=='__main__':

  # read command-line arguments
  parser = argparse.ArgumentParser( description = 'Submitter' )
  parser.add_argument('-d', '--datetag', required=True)
  parser.add_argument('--dopreul', default=False, action='store_true')
  parser.add_argument('--doul', default=False, action='store_true')
  parser.add_argument('--docontrol', default=False, action='store_true')
  parser.add_argument('--doks', default=False, action='store_true')
  parser.add_argument('--doks2d', default=False, action='store_true')
  args = parser.parse_args()

  # hard-coded settings
  preuldir = '/pnfs/iihe/cms/store/user/llambrec/k0sanalysisdata/preulfiles/'
  uldir = '/pnfs/iihe/cms/store/user/llambrec/k0sanalysisdata/ulfiles/selected_new/'
  controlconfig = 'config_controlvars.'

  cmds = []

  # control variable plots
  python3 mcvsdata_submit.py -i /pnfs/iihe/cms/store/user/llambrec/k0sanalysisdata/ulfiles/selected_new/ -v run2ul -c config_controlvars_ul.py -o output_20231212_controlvars_ul --runmode condor 
