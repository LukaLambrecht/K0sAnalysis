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
filedir = os.path.join(basedir,'oldfiles') # temp for running on old files
fillscript = 'mcvsdata_fill.py'
plotscript = 'mcvsdata_plot.py'
testing = False
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
    mcin = ([{ 'file':os.path.join(filedir,mcdir,'skim_ztomumu_all.root'), 'label':'Simulation', 'xsection':6077.22,'luminosity':lumitools.getlumi(era)*1000}])
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

### fill plotlist with properties of plots to make
plotlist = []
varnamedict = ({
	    'rpv':{'variablename':'_KsRPV','xaxtitle':'#Delta(PV-SV)_{2D} [cm]','histtitle':'K^{0}_{S} vertex radial distance'}
		})
bckmodedict = ({
	    #'bckdefault':'default',
	    'bcksideband':'sideband'
		})
extracut = 'bool(abs(getattr(tree,"_KsInvMass")-0.49761)<0.01)'
# note: extracut will only be applied in case of no background subtraction and mainly for testing,
#	not recommended to be used.
binsdict = ({
	#'finebins':json.dumps(list(np.linspace(0,20,num=50,endpoint=True)),separators=(',',':')),
	'defaultbins':json.dumps([0.,0.5,1.5,4.5,10.,20.],separators=(',',':'))
	    })
normdict = ({
	#'norm1':{'type':1,'normrange':''},
	#'norm4':{'type':4,'normrange':''},
	'norm3small':{'type':3,'normrange':json.dumps([0.,0.5],separators=(',',':'))},
	#'norm3med':{'type':3,'normrange':json.dumps([0.5,1.5],separators=(',',':'))}
	    })

for varname in varnamedict:
    for bckmode in bckmodedict:
	for norm in normdict:
	    for bins in binsdict:
		#subfolder = os.path.join(varname,bckmode,norm,bins)
		subfolder = '{}_{}_{}_{}'.format(varname,bckmode,norm,bins)
		optionsdict = ({ 'varname': varnamedict[varname]['variablename'],
                            'treename': 'laurelin',
                            'bck_mode': bckmodedict[bckmode],
                            'extracut': '',
                            'normalization': normdict[norm]['type'],
                            'xaxistitle': varnamedict[varname]['xaxtitle'],
                            'yaxistitle': 'Number of events',
                            'bins': binsdict[bins],
                            'histtitle': varnamedict[varname]['histtitle'],
			    'sidevarname': '_KsInvMass',
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
		    if os.path.exists(thishistdir):
			os.system('rm -r '+thishistdir)
		    os.makedirs(thishistdir)
		    thismcin = era['mcin']
		    thisdatain = era['datain']
		    
		    #optionsdict['histtitle'] = varnamedict[varname]['histtitle']+' ({})'.format(era['label'])
		    # asked to remove title for plot in paper
		    optionsdict['histtitle'] = ''

		    optionstring = " 'histfile="+os.path.join(thishistdir,'histograms.root')+"'"
		    optionstring += " 'helpdir="+os.path.join(thishistdir,'temp')+"'"
		    optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
		    optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
		    optionstring += " 'outfile="+os.path.join(thishistdir,'figure.png')+"'"
		    for option in optionsdict.keys():
			optionstring += " '"+option+"="+str(optionsdict[option])+"'"
		    

		    scriptname = 'qsub_mcvsdata_submit.sh'
		    with open(scriptname,'w') as script:
			jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
			script.write('python '+fillscript+optionstring+'\n')
			script.write('python '+plotscript+optionstring+'\n')
		    if testing:
			os.system('bash '+scriptname)
		    else:
			jobsub.submitQsubJob(scriptname)
