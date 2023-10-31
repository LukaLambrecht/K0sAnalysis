###################################
# Looper for make_single_plots.py #
###################################

import sys
import os
sys.path.append(os.path.abspath('../../tools'))
import condortools as ct
# WARNING: job submission does not yet work,
# due to issues with spaces in arguments and the escaping of quotes.

if __name__=='__main__':

  # run settings
  runlocal = True

  # loop settings
  v0types = ['ks', 'la']
  treenames = {'ks':'laurelin', 'la':'telperion'}

  # loop-independent settings
  inputfile = os.path.abspath('../../files/oldfiles/Run2016B_DoubleMuon/skim_ztomumu_all.root')
  inputinfo = '2016B data'
  outputdir = 'output_test'
  nprocess = -1
  normalize = True

  # clean output directory
  if os.path.exists(outputdir):
    print('WARNING: output directory {} already exists.'.format(outputdir))
    print('Clean it? (y/n)')
    go = raw_input()
    if not go == 'y': sys.exit()
    os.system('rm -r {}'.format(outputdir))
  os.makedirs(outputdir)

  # do loop
  cmds = []
  for v0type in v0types:
 
    # loop-dependent settings
    treename = treenames[v0type]
    variables = os.path.abspath('../../variables/variables_{}_withdr.json'.format(v0type))
    v0info = None
    if v0type=='ks': v0info = 'K^{0}_{S} candidates'
    elif v0type=='la': v0info = '#Lambda^{0} candidates'
    extrainfos = inputinfo
    if v0info is not None: extrainfos += ',{}'.format(v0info)
    if normalize: extrainfos += ',Normalized'

    # make command
    cmd = 'python make_single_plots.py'
    cmd += ' --inputfile {}'.format(inputfile)
    cmd += ' --outputdir {}'.format(outputdir)
    cmd += ' --nprocess {}'.format(nprocess)
    if normalize: cmd += ' --normalize'
    cmd += ' --treename {}'.format(treename)
    cmd += ' --variables {}'.format(variables)
    cmd += ' --extrainfos \'{}\''.format(extrainfos)
    cmds.append(cmd)

    # print command
    print('Executing {}'.format(cmd))

    # execute command
    if runlocal: os.system(cmd)

# submit jobs
if not runlocal:
  ct.submitCommandsAsCondorCluster('cjob_make_single_plots_loop', cmds,
    cmssw_version='/user/llambrec/CMSSW_10_2_20')
