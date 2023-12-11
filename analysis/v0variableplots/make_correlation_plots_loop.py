##################################
# Looper for make_multi_plots.py #
##################################

import sys
import os
import argparse
from six.moves import input
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
import tools.condortools as ct
from analysis.mcvsdata_getfiles import getfiles
CMSSW='/user/llambrec/CMSSW_12_4_6'


if __name__=='__main__':

  # command line arguments
  parser = argparse.ArgumentParser( description = 'Make V0 plots' )
  parser.add_argument('-i', '--filedir', required=True, type=os.path.abspath)
  parser.add_argument('-v', '--version', required=True)
  parser.add_argument('-o', '--outputdir', default='output_test')
  parser.add_argument('-n', '--nprocess', type=int, default=-1)
  parser.add_argument('--runmode', default='local', choices=['local', 'condor'])
  args = parser.parse_args()

  # other settings (hard-coded)
  variabledict = {
    'rpv_vs_rpvsig': os.path.abspath('../../variables/variables_ks_correlation_rpv_rpvsig.json'),
    'rpv_vs_rpvsig_zoom': os.path.abspath('../../variables/variables_ks_correlation_rpv_rpvsig_zoom.json'),
    'rpv_vs_rpvunc': os.path.abspath('../../variables/variables_ks_correlation_rpv_rpvunc.json'),
  }
  treename = 'laurelin'
  dopixel = True
  
  # manage input arguments to get files
  if args.version=='run2preul': includelist = ['2016', '2017', '2018']
  elif args.version=='run2ul':
        includelist = ([
          '2016PreVFP',
          '2016PostVFP',
          '2017',
          '2018',
        ])
  kwargs = {}
  if args.version=='run2preul':
    kwargs['filemode'] = 'old' # hard-coded setting to run on either new or old convention

  # get the files
  eralist = getfiles( args.filedir, includelist, args.version,
                      check_exist=True, **kwargs)
  
  # clean output directory
  if os.path.exists(args.outputdir):
    print('WARNING: output directory {} already exists.'.format(args.outputdir))
    print('Clean it? (y/n)')
    go = input()
    if not go == 'y': sys.exit()
    os.system('rm -r {}'.format(args.outputdir))
  os.makedirs(args.outputdir)

  # do loop
  cmds = []
  for name, variables in variabledict.items():
    for era in eralist:

        # get input file
        thisinputfiles = era['datain']
        if len(thisinputfiles)>1:
          msg = 'ERROR: this script can not handle multiple input files per era'
          msg += ' (found {})'.format(thisinputfiles)
          raise Exception(msg)
        inputfile = thisinputfiles[0]['file']
        inputlabel = thisinputfiles[0]['label']

        # make extra info
        extrainfos = []
        extrainfos.append('$K^{0}_{S}$ candidates')
        extrainfos.append(inputlabel)

        # make output file name
        outputfile = name+'_'+inputlabel.replace(' ','')+'.png'
        outputfile = os.path.join(args.outputdir, outputfile)

        # set pixel layer plot argument
        pixelarg = None
        if dopixel:
          if '2016' in inputlabel: pixelarg = 'pixel16'
          else: pixelarg = 'pixel1718'

        # make command
        cmd = 'python3 make_correlation_plots.py'
        cmd += ' --inputfile {}'.format(inputfile)
        cmd += ' --outputfile {}'.format(outputfile)
        cmd += ' --nprocess {}'.format(args.nprocess)
        cmd += ' --treename {}'.format(treename)
        cmd += ' --variables {}'.format(variables)
        extrainfosarg = ','.join(extrainfos)
        extrainfosarg = extrainfosarg.replace(' ','-')
        cmd += ' --extrainfos {}'.format(extrainfosarg)
        if dopixel: cmd += ' --{}'.format(pixelarg)
        cmds.append(cmd)

# run or submit jobs
if args.runmode=='local':
  for cmd in cmds:
    print(cmd)
    os.system(cmd)
elif args.runmode=='condor':
  ct.submitCommandsAsCondorCluster('cjob_make_correlation_plots_loop', cmds,
    cmssw_version=CMSSW)
