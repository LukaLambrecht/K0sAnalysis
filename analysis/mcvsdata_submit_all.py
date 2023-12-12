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

  cmds = []

  # control variable plots
  if args.docontrol:
    if args.dopreul:
      cmd = 'python3 mcvsdata_submit.py -i {}'.format(preuldir)
      cmd += ' -o output_{}_controlvars_preul'.format(args.datetag)
      cmd += ' -v run2preul -c config_controlvars_preul.py --runmode condor'
      cmds.append(cmd)
    if args.doul:
      cmd = 'python3 mcvsdata_submit.py -i {}'.format(uldir)
      cmd += ' -o output_{}_controlvars_ul'.format(args.datetag)
      cmd += ' -v run2ul -c config_controlvars_ul.py --runmode condor'
      cmds.append(cmd)

  # run all commands
  for cmd in cmds: os.system(cmd)
