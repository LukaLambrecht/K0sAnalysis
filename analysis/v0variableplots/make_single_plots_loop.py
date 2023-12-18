###################################
# Looper for make_single_plots.py #
###################################

import sys
import os
import argparse
from six.moves import input
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
import tools.condortools as ct
from analysis.mcvsdata_getfiles import getfiles
CMSSW = '/user/llambrec/CMSSW_12_4_6'


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
  v0types = ['ks', 'la']
  treenamedict = {'ks':'laurelin', 'la':'telperion'}
  if args.version=='run2preul':
    variabledict = {'ks': os.path.abspath('../../variables/variables_ks_old.json'),
                    'la': os.path.abspath('../../variables/variables_la_old.json')}
  elif args.version=='run2ul':
    variabledict = {'ks': os.path.abspath('../../variables/variables_ks_new.json'),
                    'la': os.path.abspath('../../variables/variables_la_new.json')}
  outputdict = {'ks': 'ksplots',
                'la': 'laplots'}

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
  for v0type in v0types:
 
    # loop-dependent settings
    treename = treenamedict[v0type]
    variables = variabledict[v0type]
    v0info = None
    if v0type=='ks': v0info = 'K^{0}_{S} candidates'
    elif v0type=='la': v0info = '#Lambda^{0} candidates'

    # get files and labels
    inputfiles = []
    inputlabels = []
    for era in eralist:
        thisinputfiles = era['datain']
        if len(thisinputfiles)>1:
          msg = 'ERROR: this script can not handle multiple input files per era'
          msg += ' (found {})'.format(thisinputfiles)
          raise Exception(msg)
        thisinputfile = thisinputfiles[0]['file']
        thisinputlabel = thisinputfiles[0]['label']
        inputfiles.append( thisinputfile )
        inputlabels.append( '\'{}\''.format(thisinputlabel) )

    # loop over files
    for inputfile, inputlabel in zip(inputfiles, inputlabels):

      # make info to display on plot
      extrainfos = inputlabel.strip('\'')
      if v0info is not None: extrainfos += ',{}'.format(v0info)
      extrainfos = extrainfos.strip(',')

      # make output directory
      subdir = inputlabel.replace(' ','').replace('.','').replace('\'','')
      outputdir = os.path.join(args.outputdir, outputdict[v0type], subdir)

      # make command
      cmd = 'python3 make_single_plots.py'
      cmd += ' --inputfile {}'.format(inputfile)
      cmd += ' --outputdir {}'.format(outputdir)
      cmd += ' --nprocess {}'.format(args.nprocess)
      cmd += ' --treename {}'.format(treename)
      cmd += ' --variables {}'.format(variables)
      if args.runmode=='local': extrainfosarg = '\'{}\''.format(extrainfos)
      elif args.runmode=='condor': extrainfosarg = extrainfos.replace(' ','-')
      cmd += ' --extrainfos {}'.format(extrainfosarg)
      cmds.append(cmd)

# run or submit jobs
if args.runmode=='local':
  for cmd in cmds:
    print(cmd)
    os.system(cmd)
elif args.runmode=='condor':
  for cmd in cmds: print(cmd)
  ct.submitCommandsAsCondorCluster('cjob_make_single_plots_loop', cmds,
    cmssw_version=CMSSW)
