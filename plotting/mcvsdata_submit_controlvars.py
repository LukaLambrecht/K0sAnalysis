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

filllist = []
plotlist = []

### global settings
basedir = '/storage_mnt/storage/user/llambrec/K0sAnalysis/files'
#filedir = os.path.join(basedir,'skim_ztomumu/selected_legacy_nonhits')
filedir = os.path.join(basedir,'oldfiles')
fillscript = 'mcvsdata_fill.py'
plotscript = 'mcvsdata_plot.py'
testing = True
includelist = []
#for era in ['2016B','2016C','2016D','2016E','2016F','2016G','2016H']: includelist.append(era)
#for era in ['2017B','2017C','2017D','2017E','2017F']: includelist.append(era)
#for era in ['2018A','2018B','2018C','2018D']: includelist.append(era)
includelist.append('2016')
includelist.append('2017')
includelist.append('2018')
includelist.append('run2')

### fill eralist with files to run on and related properties
eralist = []
for era in includelist:
    if era=='run2': continue
    #mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
    mcdir = 'RunIISummer16_DYJetsToLL' # temp for running on old files
    if '2017' in era: mcdir = 'RunIIFall17_DYJetsToLL' # temp for running on old files
    if '2018' in era: mcdir = 'RunIIAutumn18_DYJetsToLL' # temp for running on old files
    #datadir = 'DoubleMuon_Run'+era
    datadir = 'Run'+era+'_DoubleMuon' # temp for running on old files
    mcin = ([{ 'file':os.path.join(filedir,mcdir,'skim_ztomumu_all.root'), 'label':'simulation', 'xsection':6077.22,'luminosity':lumitools.getlumi(era)*1000}])
    datain = ([{'file':os.path.join(filedir,datadir,'skim_ztomumu_all.root'), 'label':era+' data','luminosity':lumitools.getlumi(era)*1000}])
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label})
# special cases:
if 'run2' in includelist:
    mcin = []
    datain = []
    # 2016
    mcin.append({ 'file':os.path.join(filedir,'RunIISummer16_DYJetsToLL','skim_ztomumu_all.root'), 'label':'2016 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2016')*1000})
    datain.append({'file':os.path.join(filedir,'Run2016_DoubleMuon','skim_ztomumu_all.root'), 'label':'2016 data','luminosity':lumitools.getlumi('2016')*1000})
    # 2017
    mcin.append({ 'file':os.path.join(filedir,'RunIIFall17_DYJetsToLL','skim_ztomumu_all.root'), 'label':'2017 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2017')*1000})
    datain.append({'file':os.path.join(filedir,'Run2017_DoubleMuon','skim_ztomumu_all.root'), 'label':'2017 data','luminosity':lumitools.getlumi('2017')*1000})
    # 2018
    mcin.append({ 'file':os.path.join(filedir,'RunIIAutumn18_DYJetsToLL','skim_ztomumu_all.root'), 'label':'2018 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2018')*1000})
    datain.append({'file':os.path.join(filedir,'Run2018_DoubleMuon','skim_ztomumu_all.root'), 'label':'2018 data','luminosity':lumitools.getlumi('2018')*1000})
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

if testing:
    #eralist = [eralist[0]]
    #varlist = [varlist[0]]
    for i in range(len(varlist)): varlist[i]['reductionfactor'] = 100

for era in eralist:

    thishistdir = os.path.join(filedir,'histograms',era['label'],'controlvariables')
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

	scriptname = 'mcvsdata_submit.sh'
	with open(scriptname,'w') as script:
	    jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
	    script.write('python '+fillscript+optionstring+'\n')
	    script.write('python '+plotscript+optionstring+'\n')
	if testing:
	    os.system('bash '+scriptname)
	else:
	    jobsub.submitQsubJob(scriptname)
