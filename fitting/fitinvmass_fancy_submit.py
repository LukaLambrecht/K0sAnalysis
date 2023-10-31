####################################
# submitter for filler and plotter #
####################################

import sys
import os
sys.path.append('../tools')
import condortools as ct
import lumitools
import optiontools as opt

### global settings
options = []
options.append( opt.Option('filedir', vtype='path') )
options.append( opt.Option('includelist', vtype='list',
                    default=['2016','2017','2018']) )
options.append( opt.Option('v0types', vtype='list', 
                    default=['ks','la']) )
options = opt.OptionCollection( options )
if len(sys.argv)==1:
    print('Use with following options:')
    print(options)
    sys.exit()
else:
    options.parse_options( sys.argv[1:] )
    print('Found following configuration:')
    print(options)

filemode = 'old' # hard-coded setting whether to run on old or new convention

### fill eralist with files to run on and related properties
eralist = []
for era in options.includelist:
    if era=='run2':
	exc = 'ERROR: era "run2" is not a valid argument for this script.'
	exc += ' You should process 2016, 2017 and 2018 separately and then hadd them.'
	raise Exception(exc)
    if filemode=='old':
        mcdir = 'RunIISummer16_DYJetsToLL' # temp for running on old files
        if '2017' in era: mcdir = 'RunIIFall17_DYJetsToLL' # temp for running on old files
        if '2018' in era: mcdir = 'RunIIAutumn18_DYJetsToLL' # temp for running on old files
        datadir = 'Run'+era+'_DoubleMuon' # temp for running on old files
        filename = 'skim_ztomumu_all.root' # temp for running on old files
    elif filemode=='new':
        mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
        datadir = 'DoubleMuon_Run'+era
        filename = 'merged_selected.root'
    else:
        raise Exception('ERROR: filemode "{}" not recognized.'.format(filemode))
    mcin = ({'file':os.path.join(options.filedir,mcdir,filename), 'label':'Simulation', 
	     'xsection':6077.22,'luminosity':lumitools.getlumi(era)*1000})
    datain = ({'file':os.path.join(options.filedir,datadir,filename), 'label':era+' data',
	       'luminosity':lumitools.getlumi(era)*1000})
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label})

### check if all files exist
allexist = True
for era in eralist:
    if not os.path.exists(era['mcin']['file']):
        print('### ERROR ###: following input file does not exist: '+era['mcin']['file'])
        allexist = False
    if not os.path.exists(era['datain']['file']):
        print('### ERROR ###: following input file does not exist: '+era['datain']['file'])
        allexist = False
if not allexist: sys.exit()

### loop over eras and V0 types
for era in eralist:
  for v0type in options.v0types:

    outfilebase = '{}_invmass_{}'.format(v0type,era['label'])

    datafile = outfilebase+'_data.root'
    datalabel = "'"+era['label']+' data'+"'"
    simfile = outfilebase+'_sim.root'
    simlabel = 'Simulation'
    figure = outfilebase+'_fig.png'

    # make commands for filling the histograms
    fillcmds = []
    fillcmd1 = 'python fitinvmass_fancy_fill.py {} {} {}'.format(era['mcin']['file'], simfile, v0type)
    fillcmd2 = 'python fitinvmass_fancy_fill.py {} {} {} {}'.format(era['datain']['file'],datafile, v0type,
		    era['datain']['luminosity'])
    fillcmds.append(fillcmd1)
    fillcmds.append(fillcmd2)

    # make command for fitting and plotting
    fitcmd = 'python fitinvmass_fancy_plot.py {} {} {} {} {} {}'.format(
		datafile, datalabel, simfile, simlabel, v0type, figure)

    # run or submit commands
    runlocal = False
    cmds = fillcmds+[fitcmd]
    if runlocal:
        for cmd in cmds: os.system(cmd)
    else:
        scriptname = 'cjob_fitinvmass_fancy_submit.sh'
        ct.submitCommandsAsCondorJob(scriptname, cmds,
          cmssw_version='/user/llambrec/CMSSW_10_2_20')
