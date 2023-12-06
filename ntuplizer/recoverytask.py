#!/usr/bin/env python3

########################
# Submit recovery jobs #
########################
# see https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3FAQ#Recovery_task
# and https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookCRAB3Tutorial#Re_analyzing_the_missing_luminos

# imports
import os
import subprocess
import argparse

# help functions

def getmissinglumis(taskdir):
  # kill the task if not done before
  if not 'KILLED' in system('crab status -d ' + taskdir):
    print('Task was found to be not yet killed, while this is needed for reliable reports.')
    print('Now attempting crab kill command.')
    system('crab kill -d ' + taskdir)
  # make a report
  print('Making task report...')
  print(system('crab report -d ' + taskdir))
  missingLumis = os.path.join(taskdir, 'results/notFinishedLumis.json')
  # check report output
  if not os.path.exists(missingLumis):
    print('ERROR: expected output file {} does not seem to have been generated'.format(missingLumis))
    print('Skipping this task.')
    return None
  return missingLumis

def recoverytask(taskdir, missingLumis, recoverylabel='recovery', splitting=None, units=None):
  newname = taskdir.split('/crab_')[-1] + '_{}'.format(recoverylabel)
  cwd = os.getcwd()
  os.chdir(os.path.join(os.environ['CMSSW_BASE'], 'src/heavyNeutrino/multilep/test/'))
  # make a temporary crab config file with modified parameters for recovery task
  with open('crab_temp.py', 'w') as config:
    with open(os.path.join(taskdir, 'crab.log')) as f:
      foundConfigLines = False
      for line in f:
        if foundConfigLines:
          # copy some lines with modifications
          if newname and line.count('requestName'):
            config.write('config.General.requestName="%s"\n' % newname)
          elif line.count('lumiMask'):
            config.write('config.Data.lumiMask="%s"\n' % missingLumis)
          elif splitting is not None and line.count('splitting'):
            config.write('config.Data.splitting="%s"\n' % splitting)
          elif units is not None and line.count('unitsPerJob'):
            config.write('config.Data.unitsPerJob=%s\n' % units)
          elif 'DEBUG' in line: break
          # copy other lines without modification
          else: config.write(line)
        if line.count('from WMCore.Configuration import Configuration'):
          foundConfigLines = True
          config.write('from WMCore.Configuration import Configuration\n')
  # do crab submit
  print(system('crab submit -c crab_temp.py'))
  # remove temporary config files
  os.remove('crab_temp.py')
  os.remove('crab_temp.pyc')
  os.chdir(cwd)

def system(command):
  try: 
    return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()
  except Exception as e:
    return e.output


# main body
if __name__=='__main__':

    # parse arguments
    parser = argparse.ArgumentParser('Submit recovery tasks')
    parser.add_argument('-d', '--taskdirs', required=True, type=os.path.abspath, nargs='+',
      help='CRAB task directories for which to submit a recovery task')
    parser.add_argument('--label', default='recovery',
      help='Label for the name of these recovery tasks')
    parser.add_argument('--splitting', default=None,
      help='Splitting for these recovery tasks (default: keep same as original task)')
    parser.add_argument('--units', default=None,
      help='Units for these recovery tasks (default: keep same as original task)')
    args = parser.parse_args()

    # print arguments
    print('Running with following configuration:')
    for arg in vars(args):
        print('  - {}: {}'.format(arg,getattr(args,arg)))

    args.taskdirs = sorted(args.taskdirs)
    for i,taskdir in enumerate(args.taskdirs):
        print('Now processing task {} ({}/{})'.format(taskdir, i+1, len(args.taskdirs)))
        missinglumis = getmissinglumis(taskdir)
        if missinglumis is None: continue
        recoverytask(taskdir, missinglumis, recoverylabel=args.label,
          splitting=args.splitting, units=args.units)
