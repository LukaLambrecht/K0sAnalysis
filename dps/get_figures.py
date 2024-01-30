###########################################################
# Collect all figures that go into the DPS into one place #
###########################################################

import sys
import os

if __name__=='__main__':

  # settings
  outputdir = 'figures'

  # make output directory
  if not os.path.exists(outputdir): os.makedirs(outputdir)

  # initialize list of copy commands
  cmds = []

  # regular yield vs distance plots
  datetag = '20240129'
  years = ['2016', '2016PreVFP', '2016PostVFP', '2017', '2018', 'run2']
  processings = ['preul', 'ul']
  for year in years:
    for processing in processings:
      inputfile = os.path.join('../analysis/output_{}_ksvars_{}'.format(datetag,processing),
                    year, 'rpv_bkgsideband_normrange_finebins', 'rpv_log.pdf')
      outputfile = os.path.join(outputdir, 'rpv_{}_{}.pdf'.format(year, processing))
      cmd = 'cp {} {}'.format(inputfile, outputfile)
      cmds.append(cmd)

  # yield vs distance plots with detector layers
  datetag = '20240129'
  years = ['2016', '20172018']
  processings = ['ul']
  for year in years:
    for processing in processings:
      inputfile = os.path.join('../analysis/output_{}_ksdetector_{}'.format(datetag,processing),
                    year, 'rpv_bkgsideband_normrangesmall_finebins', 'rpv.pdf')
      outputfile = os.path.join(outputdir, 'rpv_{}_{}_detector.pdf'.format(year, processing))
      cmd = 'cp {} {}'.format(inputfile, outputfile)
      cmds.append(cmd)

  # invariant mass plots
  datetag = '20240129'
  years = ['run2']
  appendices = ['', '_split_0', '_split_1', '_split_3']
  for year in years:
    for appendix in appendices:
      inputfile = os.path.join('../fitting/plots_{}'.format(datetag), year+appendix+'.pdf')
      outputfile = os.path.join(outputdir, 'mass_{}{}.pdf'.format(year, appendix))
      cmd = 'cp {} {}'.format(inputfile, outputfile)
      cmds.append(cmd)

  # execute all commands
  for cmd in cmds: os.system(cmd)
