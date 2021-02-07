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

### fill plotlist with properties of plots to make
plotlist = []
varnamedict = ({
	    'rpv':{'variablename':'_RPV','xaxtitle':'radial displacement (cm)','histtitle':'K^{0}_{S} vertex radial distance'}
		})
bckmodedict = {'bckdefault':'default','bcksideband':'sideband'}
extracut = 'bool(abs(getattr(tree,"_mass")-0.49761)<0.01)'
# note: extracut only applied in case of no background subtraction and mainly for testing,
#	not recommended to be used.
binsdict = ({
	#'finebins':json.dumps(list(np.linspace(0,20,num=50,endpoint=True)),separators=(',',':')),
	'defaultbins':json.dumps([0.,0.5,1.5,4.5,20.],separators=(',',':'))
	    })
normdict = ({
	#'norm1':{'type':1,'normrange':''},
	'norm4':{'type':4,'normrange':''},
	'norm3small':{'type':3,'normrange':json.dumps([0.,0.5],separators=(',',':'))},
	#'norm3med':{'type':3,'normrange':json.dumps([0.5,1.5],separators=(',',':'))}
	    })

for varname in varnamedict:
    for bckmode in bckmodedict:
	for norm in normdict:
	    for bins in binsdict:
		subfolder = os.path.join(varname,bckmode,norm,bins)
		optionsdict = ({ 'varname': varnamedict[varname]['variablename'],
                            'treename': 'laurelin',
                            'bck_mode': bckmodedict[bckmode],
                            'extracut': '',
                            'normalization': normdict[norm]['type'],
                            'xaxistitle': varnamedict[varname]['xaxtitle'],
                            'yaxistitle': 'number of events',
                            'bins': binsdict[bins],
                            'histtitle': varnamedict[varname]['histtitle'],
			    'sidevarname': '_mass',
			    'sidexlow': 0.44,
			    'sidexhigh': 0.56,
			    'sidenbins': 30,
			    'normrange': normdict[norm]['normrange'],
			    'eventtreename': 'nimloth'
			    })
		if bckmodedict[bckmode]=='default':
		    optionsdict['extracut']=extracut
		if testing: 
		    optionsdict['reductionfactor'] = 100

		for era in eralist:
		    # make a job submission script for this era with these plot options

		    thishistdir = os.path.join(filedir,'histograms',era['label'],
						'kshort',subfolder)
		    if testing: thishistdir = 'test'
		    if os.path.exists(thishistdir):
			os.system('rm -r '+thishistdir)
		    os.makedirs(thishistdir)
		    thismcin = era['mcin']
		    thisdatain = era['datain']
		    thislumi = era['lumi']

		    optionstring = " 'histfile="+os.path.join(thishistdir,'histograms.root')+"'"
		    optionstring += " 'helpdir="+os.path.join(thishistdir,'temp')+"'"
		    optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
		    optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
		    optionstring += " 'lumi="+str(thislumi)+"'"
		    optionstring += " 'outfile="+os.path.join(thishistdir,'figure.png')+"'"
		    for option in optionsdict.keys():
			optionstring += " '"+option+"="+str(optionsdict[option])+"'"
		    

		    scriptname = 'mcvsdata_submit.sh'
		    with open(scriptname,'w') as script:
			jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
			script.write('python '+fillscript+optionstring+'\n')
			script.write('python '+plotscript+optionstring+'\n')
		    if testing:
			os.system('bash '+scriptname)
		    else:
			jobsub.submitQsubJob(scriptname)
