##################################
# Looper for make_multi_plots.py #
##################################

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
  inputfiles = []
  labels = []
  inputfiles.append( os.path.abspath('../../files/oldfiles/Run2016_DoubleMuon/skim_ztomumu_all.root') )
  labels.append('2016 data')
  #inputfiles.append( os.path.abspath('../../files/oldfiles/Run2016BtoF_DoubleMuon/skim_ztomumu_all.root') )
  #labels.append('2016 (B-F) data')
  #inputfiles.append( os.path.abspath('../../files/oldfiles/Run2016GtoH_DoubleMuon/skim_ztomumu_all.root') )
  #labels.append('2016 (G-H) data')
  inputfiles.append( os.path.abspath('../../files/oldfiles/Run2017_DoubleMuon/skim_ztomumu_all.root') )
  labels.append('2017 data')
  inputfiles.append( os.path.abspath('../../files/oldfiles/Run2018_DoubleMuon/skim_ztomumu_all.root') )
  labels.append('2018 data')
  outputdir = 'output_test'
  #nprocess = 500000
  nprocess = 1000
  normalize = True
  colors = None
  #colors = '2016split'

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
    variables = os.path.abspath('../../variables/variables_{}.json'.format(v0type))
    v0info = None
    if v0type=='ks': v0info = 'K^{0}_{S} candidates'
    elif v0type=='la': v0info = '#Lambda^{0} candidates'
    extrainfos = ''
    if v0info is not None: extrainfos += ',{}'.format(v0info)
    if normalize: extrainfos += ',Normalized'
    extrainfos = extrainfos.strip(',')

    # make command
    cmd = 'python make_multi_plots.py'
    cmd += ' --inputfiles {}'.format(' '.join(inputfiles))
    cmd += ' --inputlabels {}'.format(' '.join(['\'{}\''.format(label) for label in labels]))
    cmd += ' --outputdir {}'.format(outputdir)
    cmd += ' --nprocess {}'.format(nprocess)
    if normalize: cmd += ' --normalize'
    cmd += ' --treename {}'.format(treename)
    cmd += ' --variables {}'.format(variables)
    cmd += ' --extrainfos \'{}\''.format(extrainfos)
    if colors is not None: cmd += ' --colors {}'.format(colors)
    cmds.append(cmd)

    # print command
    print('Executing {}'.format(cmd))

    # execute command
    if runlocal: os.system(cmd)

# submit jobs
if not runlocal:
  ct.submitCommandsAsCondorCluster('cjob_make_multi_plots_loop', cmds,
    cmssw_version='/user/llambrec/CMSSW_10_2_20')
