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
basedir = '/storage_mnt/storage/user/llambrec/Kshort/files'
filedir = os.path.join(basedir,'skim_ztomumu/selected_legacy_nonhits')
fillscript = 'mcvsdata_fill.py'
plotscript = 'mcvsdata_plot.py'
testing = False
includelist = []
for era in ['2016B','2016C','2016D','2016E','2016F','2016G','2016H']: includelist.append(era)
includelist.append('2016')

### fill eralist with files to run on and related properties
eralist = []
for era in includelist:
    mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
    datadir = 'DoubleMuon_Run'+era
    mcin = ([{ 'file':os.path.join(filedir,mcdir,'selected.root'), 'label':'simulation', 'xsection':6077.22}])
    datain = ([{'file':os.path.join(filedir,datadir,'selected.root'), 'label':era+' data'}])
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label,'lumi':lumitools.getlumi(era)*1000})

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
varnamelist = ['_nimloth_Mll','_celeborn_lPt']

for varname in varnamelist:

    if varname=='_nimloth_Mll':
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

    elif varname=='_celeborn_lPt':
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


testing = False
if testing:
    eralist = [eralist[0]]
    varlist = [varlist[0]]
    varlist[0]['reductionfactor'] = 100

for era in eralist:

    thishistdir = os.path.join(filedir,'histograms',era['label'],'controlvariables')
    if not os.path.exists(thishistdir):
	os.makedirs(thishistdir)
    thismcin = era['mcin']
    thisdatain = era['datain']
    thislumi = era['lumi']

    for var in varlist:
	optionstring = " 'histfile="+os.path.join(thishistdir,var['varname']+'.root')+"'"
	optionstring += " 'helpdir="+os.path.join(thishistdir,var['varname']+'_temp')+"'"
	optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
	optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
	optionstring += " 'lumi="+str(thislumi)+"'"
	optionstring += " 'outfile="+os.path.join(thishistdir,var['varname']+'.png')+"'"
	for option in var.keys():
	    optionstring += " '"+option+"="+str(var[option])+"'"

	scriptname = 'mcvsdata_submit.sh'
	with open(scriptname,'w') as script:
	    jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
	    script.write('python '+fillscript+optionstring+'\n')
	    script.write('python '+plotscript+optionstring+'\n')
	if testing:
	    os.system('bash '+scriptname)
	else:
	    jobsub.submitQsubJob(scriptname)
