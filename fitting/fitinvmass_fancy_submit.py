####################################
# submitter for filler and plotter #
####################################

import sys
import os
sys.path.append('../tools')
import jobsubmission as jobsub
import lumitools
import optiontools as opt

### global settings
options = []
options.append( opt.Option('filedir', vtype='path') )
options.append( opt.Option('includelist', vtype='list',
                    default=['2016','2017','2018']) )
options = opt.OptionCollection( options )
if len(sys.argv)==1:
    print('Use with following options:')
    print(options)
    sys.exit()
else:
    options.parse_options( sys.argv[1:] )
    print('Found following configuration:')
    print(options)

### fill eralist with files to run on and related properties
eralist = []
for era in options.includelist:
    if era=='run2':
	exc = 'ERROR: era "run2" is not a valid argument for this script.'
	exc += ' You should process 2016, 2017 and 2018 separately and then hadd them.'
	raise Exception(exc)
    mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
    #mcdir = 'RunIISummer16_DYJetsToLL' # temp for running on old files
    #if '2017' in era: mcdir = 'RunIIFall17_DYJetsToLL' # temp for running on old files
    #if '2018' in era: mcdir = 'RunIIAutumn18_DYJetsToLL' # temp for running on old files
    datadir = 'DoubleMuon_Run'+era
    #datadir = 'Run'+era+'_DoubleMuon' # temp for running on old files
    filename = 'merged_selected.root'
    #filename = 'skim_ztomumu_all.root' # temp for running on old files
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


for era in eralist:

    outfilebase = 'ksinvmass_'

    datafile = outfilebase+era['label']+'_data.root'
    datalabel = "'"+era['label']+' data'+"'"
    simfile = outfilebase+era['label']+'_sim.root'
    simlabel = 'Simulation'
    figure = outfilebase+era['label']+'_fig.png'

    # make commands for filling the histograms
    fillcmds = []
    fillcmd1 = 'python fitinvmass_fancy_fill.py {} {}'.format(era['mcin']['file'],simfile)
    fillcmd2 = 'python fitinvmass_fancy_fill.py {} {} {}'.format(era['datain']['file'],datafile,
		    era['datain']['luminosity'])
    fillcmds.append(fillcmd1)
    fillcmds.append(fillcmd2)

    # make command for fitting and plotting
    fitcmd = 'python fitinvmass_fancy_plot.py {} {} {} {} {}'.format(
		datafile,datalabel,simfile,simlabel,figure)

    scriptname = 'qsub_fitinvmass_fancy_submit.sh'
    with open(scriptname,'w') as script:
	jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
        for cmd in fillcmds: script.write(cmd+'\n')
        script.write(fitcmd+'\n')
    #os.system('bash '+scriptname)
    jobsub.submitQsubJob(scriptname)    
