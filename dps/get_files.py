#################################################
# Collect all relevant files with scale factors #
#################################################
# Note: so far only 1D histograms, as requested by TRK POG

import sys
import os

if __name__=='__main__':

  # settings
  outputdir = 'files'

  # make output directory
  if not os.path.exists(outputdir): os.makedirs(outputdir)

  # initialize list of copy commands
  cmds = []

  # regular yield vs distance plots
  datetag = '20240205'
  years = ['2016', '2016PreVFP', '2016PostVFP', '2017', '2018', 'run2']
  processings = ['preul', 'ul']
  for year in years:
    for processing in processings:
      inputfile = os.path.join('../analysis/output_{}_ksvars_{}'.format(datetag,processing),
                    year, 'rpv_bkgsideband_normrange_finebins', 'histograms.root')
      outputfile = os.path.join(outputdir, 'ks_yield_vs_radialdistance_{}_{}.root'.format(year, processing))
      cmd = 'cp {} {}'.format(inputfile, outputfile)
      cmds.append(cmd)

  # execute all commands
  for cmd in cmds: os.system(cmd)
