###########################################
# Submit mcvsdata fillrd and plot methods #
###########################################
import json
import os
import sys
import numpy as np
sys.path.append('../tools')
import jobsubmission as jobsub
import lumitools
import optiontools as opt

filllist = []
plotlist = []

### global settings
options = []
options.append( opt.Option('filedir', vtype='path') )
options.append( opt.Option('fillscript', default='mcvsdata_fill.py') )
options.append( opt.Option('plotscript', default='mcvsdata_plot.py') )
options.append( opt.Option('testing', vtype='bool', default=False) )
options.append( opt.Option('includelist', vtype='list', 
		    default=['2016','2017','2018','run2']) )
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
    if era=='run2': continue
    #mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
    mcdir = 'RunIISummer16_DYJetsToLL' # temp for running on old files
    if '2017' in era: mcdir = 'RunIIFall17_DYJetsToLL' # temp for running on old files
    if '2018' in era: mcdir = 'RunIIAutumn18_DYJetsToLL' # temp for running on old files
    #datadir = 'DoubleMuon_Run'+era
    datadir = 'Run'+era+'_DoubleMuon' # temp for running on old files
    #filename = 'merged_selected.root'
    filename = 'skim_ztomumu_all.root' # temp for running on old files
    mcin = ([{ 'file':os.path.join(options.filedir,mcdir,filename), 
		'label':'simulation', 'xsection':6077.22,
		'luminosity':lumitools.getlumi(era)*1000}])
    datain = ([{'file':os.path.join(options.filedir,datadir,filename), 
		'label':era+' data','luminosity':lumitools.getlumi(era)*1000}])
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label})
# special cases:
if 'run2' in options.includelist:
    mcin = []
    datain = []
    # 2016
    mcin.append({ 'file':os.path.join(options.filedir,'RunIISummer16_DYJetsToLL','skim_ztomumu_all.root'), 'label':'2016 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2016')*1000})
    datain.append({'file':os.path.join(options.filedir,'Run2016_DoubleMuon','skim_ztomumu_all.root'), 'label':'2016 data','luminosity':lumitools.getlumi('2016')*1000})
    # 2017
    mcin.append({ 'file':os.path.join(options.filedir,'RunIIFall17_DYJetsToLL','skim_ztomumu_all.root'), 'label':'2017 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2017')*1000})
    datain.append({'file':os.path.join(options.filedir,'Run2017_DoubleMuon','skim_ztomumu_all.root'), 'label':'2017 data','luminosity':lumitools.getlumi('2017')*1000})
    # 2018
    mcin.append({ 'file':os.path.join(options.filedir,'RunIIAutumn18_DYJetsToLL','skim_ztomumu_all.root'), 'label':'2018 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2018')*1000})
    datain.append({'file':os.path.join(options.filedir,'Run2018_DoubleMuon','skim_ztomumu_all.root'), 'label':'2018 data','luminosity':lumitools.getlumi('2018')*1000})
    label = 'Run-II'
    eralist.append({'mcin':mcin,'datain':datain,'label':label})

### check if all files exist
allexist = True
for era in eralist:
    for mcfile in era['mcin']:
        if not os.path.exists(mcfile['file']):
            print('### ERROR ###: following input file does not exist: '+mcfile['file'])
            allexist = False
    for datafile in era['datain']:
        if not os.path.exists(datafile['file']):
            print('### ERROR ###: following input file does not exist: '+datafile['file'])
            allexist = False
if not allexist: sys.exit()

### fill varlist with variables to run on and related properties
varlist = []
#varnamelist = ['_nimloth_Mll','_celeborn_lPt']
varnamelist = ['_event_mll','_lPt'] # temp for running on old files

for varname in varnamelist:

    if( varname=='_nimloth_Mll' or varname=='_event_mll' ):
	varlist.append({    'varname': varname,
			    'treename': 'nimloth',
			    'bck_mode': 'default',
			    'extracut': '',
			    'normalization': 1,
			    'xaxistitle': 'invariant mass (GeV)',
			    'yaxistitle': 'number of events',
			    'bins': json.dumps(list(np.linspace(85,97,num=50,endpoint=True)),
					separators=(',',':')),
			    'histtitle': 'dilepton invariant mass',
			})

    elif( varname=='_celeborn_lPt' or varname=='_lPt' ):
	varlist.append({    'varname': varname,
                            'treename': 'celeborn',
                            'bck_mode': 'default',
                            'extracut': '',
                            'normalization': 1,
                            'xaxistitle': 'transverse momentum (GeV)',
                            'yaxistitle': 'number of leptons',
                            'bins': json.dumps(list(np.linspace(25,125,num=50,endpoint=True)),
					separators=(',',':')),
                            'histtitle': 'lepton transverse momentum',
                        })
    else:
	print('### WARNING ###: variable name '+varname+' not recognized, skipping...')

if options.testing:
    # run on a subselection of eras only
    eralist = [eralist[0]]
    # run on a subselection of variables only
    varlist = [varlist[0]]
    # run on a subselection of events only
    for i in range(len(varlist)): varlist[i]['reductionfactor'] = 100

for era in eralist:

    thishistdir = os.path.join(options.filedir,'histograms',era['label'],'controlvariables')
    if not os.path.exists(thishistdir):
	os.makedirs(thishistdir)
    thismcin = era['mcin']
    thisdatain = era['datain']

    for var in varlist:

	thistitle = var['histtitle']+' ({})'.format(era['label'])

	optionstring = " 'histfile="+os.path.join(thishistdir,var['varname']+'.root')+"'"
	optionstring += " 'helpdir="+os.path.join(thishistdir,var['varname']+'_temp')+"'"
	optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
	optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
	optionstring += " 'outfile="+os.path.join(thishistdir,var['varname']+'.png')+"'"
	for option in var.keys():
	    if option=='histtitle': continue
	    optionstring += " '"+option+"="+str(var[option])+"'"
	optionstring += " 'histtitle="+thistitle+"'"

	scriptname = 'qjob_mcvsdata_submit.sh'
	with open(scriptname,'w') as script:
	    jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_20')
	    script.write('python '+options.fillscript+optionstring+'\n')
	    script.write('python '+options.plotscript+optionstring+'\n')
	if options.testing:
	    os.system('bash '+scriptname)
	else:
	    jobsub.submitQsubJob(scriptname)
