#######################################
# Fill and plot MC vs data histograms #
#######################################

import os
import sys
import json
import argparse
import importlib
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
import tools.condortools as ct
from mcvsdata_getfiles import getfiles
CMSSW = '/user/llambrec/CMSSW_12_4_6'


if __name__=='__main__':

  # read command-line arguments
  parser = argparse.ArgumentParser( description = 'Submit analysis' )
  # general arguments
  parser.add_argument('-i', '--filedir', required=True, type=os.path.abspath)
  parser.add_argument('-v', '--version', required=True)
  parser.add_argument('-c', '--config', required=True)
  parser.add_argument('-o', '--outputdir', required=True)
  parser.add_argument('-e', '--eras', default=['default'], nargs='+')
  parser.add_argument('-n', '--nprocess', default=-1, type=int)
  parser.add_argument('--dodetector', default=False, action='store_true')
  parser.add_argument('--runmode', default='local', choices=['local', 'condor'])
  args = parser.parse_args()

  # manage input arguments to get files
  includelist = args.eras
  if 'default' in includelist:
    if args.version=='run2preul':
        includelist = ([
          '2016PreVFP', # split of 2016 file based on run ranges
          '2016PostVFP', # split of 2016 file based on run ranges
          '2016',
          '2017',
          '2018',
          'run2'
        ])
    elif args.version=='run2ul':
        includelist = ([
          '2016PreVFP',
          '2016PostVFP',
          '2016',
          '2017',
          '2018',
          'run2'
        ])
  elif 'perera' in includelist:
    if args.version=='run2preul':
      includelist = ['2016B','2016C','2016D','2016E','2016F','2016G','2016H']
    elif args.version=='run2ul':
      includelist = ([
        '2016PreVFPB',
        '2016PreVFPC',
        '2016PreVFPD',
        '2016PreVFPE',
        '2016PreVFPF',
        '2016PostVFPF',
        '2016PostVFPG',
        '2016PostVFPH'
      ])
  elif 'detector' in includelist:
    if args.version=='run2preul':
      includelist = ([
        '2016PreVFP',
        '2016PostVFP',
        '2016',
        '2017',
        '2018',
        '20172018'
      ])
    elif args.version=='run2ul':
      includelist = ([
        '2016PreVFP',
        '2016PostVFP',
        '2016',
        '2017',
        '2018',
        '20172018',
      ])
  kwargs = {}
  if args.version=='run2preul':
    kwargs['filemode'] = 'new' # hard-coded setting to run on either new or old convention

  # fill eralist with files to run on and related properties
  eralist = getfiles( args.filedir, includelist, args.version, 
                      check_exist=True, **kwargs)

  # read variable configuration
  if args.config.endswith('.json'):
    with open(args.config) as f:
      settings = json.load(f)
  elif args.config.endswith('.py'):
    settings = importlib.import_module(args.config.replace('.py','')).config
  else:
    msg = 'ERROR: file extension not recognized for config file {}'.format(args.config)
    raise Exception(msg)
  varnames = list(settings.keys())

  # loop over eras
  for era in eralist:
    # set output directory
    thiseradir = os.path.join(args.outputdir,era['label'])
    if not os.path.exists(thiseradir): os.makedirs(thiseradir)
    # write input configuration
    configjson = os.path.join(thiseradir, 'config.json')
    with open(configjson, 'w') as f:
      json.dump(era, f)
    # loop over variables and corresponding settings
    for varname in varnames:
      variable = settings[varname]
      for bkgmodename, bkgmode in variable['bkgmodes'].items():
        for normname, norm in variable['normalization'].items():
          for binname, bins in variable['bins'].items():
            # define output directory
            subfolder = '{}_{}_{}_{}'.format(varname, bkgmodename, normname, binname)
            thisvardir = os.path.join(thiseradir, subfolder)
            if not os.path.exists(thisvardir): os.makedirs(thisvardir)
            # handle cases of 1D or 2D binning
            if 'yvariablename' in variable.keys():
              ybins = bins['ybins']
              bins = bins['xbins']
            # write main variable
            variabledict = ({
              'name': varname,
              'label': variable['xaxtitle'],
              'variable': variable['variablename'],
              'bins': list(bins)
            })
            varjson = os.path.join(thisvardir, 'variable.json')
            with open(varjson, 'w') as f:
              json.dump(variabledict, f)
            # write secondary variable
            if 'yvariablename' in variable.keys():
              yvariabledict = ({
                'name': varname,
                'label': variable['yaxtitle'],
                'variable': variable['yvariablename'],
                'bins': list(ybins)
              })
              yvarjson = os.path.join(thisvardir, 'yvariable.json')
              with open(yvarjson, 'w') as f:
                json.dump(yvariabledict, f)
            # write normalization variable
            if norm['type']=='range':
              normvariabledict = ({
                'name': norm['normvariable'],
                'label': norm['normvariable'],
                'variable': norm['normvariable'],
                'bins': list(norm['normrange'])
              })
              normvarjson = os.path.join(thisvardir, 'normvariable.json')
              with open(normvarjson, 'w') as f:
                json.dump(normvariabledict, f)
            # write sideband variable
            if bkgmode['type']=='sideband':
              sidevariabledict = ({
                'name': bkgmode['sidevariable'],
                'label': bkgmode['sidevariable'],
                'variable': bkgmode['sidevariable'],
                'bins': list(bkgmode['sidebins'])
              })
              sidevarjson = os.path.join(thisvardir, 'sidevariable.json')
              with open(sidevarjson, 'w') as f:
                json.dump(sidevariabledict, f)
            # make extra info to display on plot
            extrainfos = []
            if 'extrainfos' in variable.keys(): extrainfos = variable['extrainfos'][:]
            if 'info' in bkgmode.keys(): extrainfos.append(bkgmode['info'])
            if 'info' in norm.keys(): extrainfos.append(norm['info'])
            doextrainfos = True if len(extrainfos)>0 else False
            # make command for filling
            cmds = []
            histfile = os.path.join(thisvardir, 'histograms.root')
            outputfile = os.path.join(thisvardir, '{}.png'.format(varname))
            cmd = 'python3 mcvsdata_fill.py'
            cmd += ' -i {}'.format(configjson)
            cmd += ' -t {}'.format(variable['treename'])
            cmd += ' -v {}'.format(varjson)
            cmd += ' -o {}'.format(histfile)
            if args.nprocess>0: cmd += ' -n {}'.format(args.nprocess)
            # add args for normalization
            if norm['type'] is not None: cmd += ' --normmode {}'.format(norm['type'])
            if norm['type']=='range': cmd += ' --normvariable {}'.format(normvarjson)
            if norm['type']=='eventyield': cmd += ' --eventtreename nimloth'
            # (hard-coded for now, maybe extend later)
            # add args for background subtraction
            if bkgmode['type'] is not None: cmd += ' --bkgmode {}'.format(bkgmode['type'])
            if bkgmode['type']=='sideband':
              cmd += ' --sidevariable {}'.format(sidevarjson)
              cmd += ' --sideplotdir {}'.format(os.path.join(thisvardir, 'sideband'))
            # add args for secondary variable
            if 'yvariablename' in variable.keys(): cmd += ' --yvariable {}'.format(yvarjson)
            cmds.append(cmd)
            # make basic command for plotting
            exe = 'mcvsdataplotter.py'
            if 'yvariablename' in variable.keys(): exe = 'mcvsdataplotter2d.py'
            cmd = 'python3 ../plotting/{}'.format(exe)
            cmd += ' -i {}'.format(histfile)
            cmd += ' --xaxtitle \'{}\''.format(variable['xaxtitle'])
            cmd += ' --extracmstext Preliminary'
            # special cases for plotting command
            # note: bin width is added to y-axis title (on request),
            #       this assumes all bins have equal width...
            #       it will give nonsense on non-equal binnings,
            #       but some people have very strong feelings about this,
            #       so temporarily implemented this comment anyway,
            #       comment out if not needed.
            yaxtitle = variable['yaxtitle']
            #yaxtitle += ' (/ {:.1f} cm)'.format(bins[1]-bins[0])
            cmd += ' --yaxtitle \'{}\''.format(yaxtitle)
            if args.version=='run2ul': cmd += ' --extralumitext Legacy'
            if args.version=='run2preul': cmd += ' --extralumitext Pre-legacy'
            if args.dodetector:
              if '2016' in era['label']: cmd += ' --do2016pixel'
              if '2017' in era['label']: cmd += ' --do20172018pixel'
              if '2018' in era['label']: cmd += ' --do20172018pixel'
            if exe=='mcvsdataplotter2d.py':
              eratxt = era['label']
              if eratxt=='run2': eratxt = 'Run-II'
              eratxt = eratxt.replace('PreVFP', ' (old APV)')
              eratxt = eratxt.replace('PostVFP', ' (new APV)')
              extrainfos = ['{} data / sim.'.format(eratxt)] + extrainfos
              doextrafinos = True
            if doextrainfos:
              cmd += ' --doextrainfos'
              cmd += ' --extrainfos \'{}\''.format(','.join(extrainfos))
            # first variation: default
            cmd1 = cmd + ' -o {}'.format(outputfile)
            cmds.append(cmd1)
            # second variation: y-axis in log scale (only for 1D plots)
            if exe=='mcvsdataplotter.py':
              cmd2 = cmd + ' -o {}'.format(outputfile.replace('.png','_log.png'))
              cmd2 += ' --logy'
              cmds.append(cmd2)
            # run or submit commands
            scriptname = 'cjob_mcvsdata_submit.sh'
            if args.runmode=='local':
              for cmd in cmds: os.system(cmd)
            else:
              ct.submitCommandsAsCondorJob(scriptname, cmds, cmssw_version=CMSSW)
