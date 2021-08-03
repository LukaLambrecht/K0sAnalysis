############################################
# Submit mcvsdata 2d fill and plot methods #
############################################
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
options.append( opt.Option('fillscript', default='mcvsdata_fill2d.py') )
options.append( opt.Option('plotscript', default='mcvsdata_plot2d.py') )
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
    mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
    #mcdir = 'RunIISummer16_DYJetsToLL' # temp for running on old files
    #if '2017' in era: mcdir = 'RunIIFall17_DYJetsToLL' # temp for running on old files
    #if '2018' in era: mcdir = 'RunIIAutumn18_DYJetsToLL' # temp for running on old files
    datadir = 'DoubleMuon_Run'+era
    #datadir = 'Run'+era+'_DoubleMuon' # temp for running on old files
    filename = 'merged_selected.root'
    #filename = 'skim_ztomumu_all.root' # temp for running on old files
    mcin = ([{ 'file':os.path.join(options.filedir,mcdir,filename), 'label':'simulation', 
		'xsection':6077.22,'luminosity':lumitools.getlumi(era)*1000}])
    datain = ([{'file':os.path.join(options.filedir,datadir,filename), 'label':era+' data',
		'luminosity':lumitools.getlumi(era)*1000}])
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label})
# special cases:
if 'run2' in options.includelist:
    mcin = []
    datain = []
    # temp for running on old files:
    '''# 2016
    mcin.append({ 'file':os.path.join(options.filedir,'RunIISummer16_DYJetsToLL',filename), 'label':'2016 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2016')*1000})
    datain.append({'file':os.path.join(options.filedir,'Run2016_DoubleMuon',filename), 'label':'2016 data','luminosity':lumitools.getlumi('2016')*1000})
    # 2017
    mcin.append({ 'file':os.path.join(options.filedir,'RunIIFall17_DYJetsToLL',filename), 'label':'2017 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2017')*1000})
    datain.append({'file':os.path.join(options.filedir,'Run2017_DoubleMuon',filename), 'label':'2017 data','luminosity':lumitools.getlumi('2017')*1000})
    # 2018
    mcin.append({ 'file':os.path.join(options.filedir,'RunIIAutumn18_DYJetsToLL',filename), 'label':'2018 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('2018')*1000})
    datain.append({'file':os.path.join(options.filedir,'Run2018_DoubleMuon',filename), 'label':'2018 data','luminosity':lumitools.getlumi('2018')*1000})'''
    # for running on new files
    # 2016
    mcin.append({ 'file':os.path.join(options.filedir,'DYJetsToLL_2016',filename),
                  'label':'2016 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('2016')*1000})
    datain.append({'file':os.path.join(options.filedir,'DoubleMuon_Run2016',filename),
                   'label':'2016 data','luminosity':lumitools.getlumi('2016')*1000})
    # 2017
    mcin.append({ 'file':os.path.join(options.filedir,'DYJetsToLL_2017',filename),
                  'label':'2017 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('2017')*1000})
    datain.append({'file':os.path.join(options.filedir,'DoubleMuon_Run2017',filename),
                   'label':'2017 data','luminosity':lumitools.getlumi('2017')*1000})
    # 2018
    mcin.append({ 'file':os.path.join(options.filedir,'DYJetsToLL_2018',filename),
                  'label':'2018 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('2018')*1000})
    datain.append({'file':os.path.join(options.filedir,'DoubleMuon_Run2018',filename),
                   'label':'2018 data','luminosity':lumitools.getlumi('2018')*1000})
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
	    'rpv_vs_pt':{'xvarname':'_RPV','xaxtitle':'radial displacement (cm)',
		    'yvarname':'_pt','yaxtitle':'p_{T} (GeV)',
		    'histtitle':'K^{0}_{S} scale factors'}
		})
bckmodedict = ({
	    #'bckdefault':'default',
	    'bcksideband':'sideband'
		})
#extracut = 'bool(abs(getattr(tree,"_KsInvMass")-0.49761)<0.01)'
extracut = 'bool(2>1)'
# note: extracut will only be applied in case of no background subtraction and mainly for testing,
#	not recommended to be used.
binsdict = ({
	'defaultbins':{'xbins':json.dumps([0.,0.5,1.5,4.5,20.],separators=(',',':')),
			'ybins':json.dumps([0.,5.,10.,20.],separators=(',',':'))}
	    })
normdict = ({
	'norm3small':{'type':3,'xnormrange':json.dumps([0.,0.5],separators=(',',':')),
				'ynormrange':json.dumps([0.,20.],separators=(',',':'))}
	    })

for varname in varnamedict:
    for bckmode in bckmodedict:
	for norm in normdict:
	    for bins in binsdict:
		subfolder = '{}_{}_{}_{}'.format(varname,bckmode,norm,bins)
		optionsdict = ({ 'xvarname': varnamedict[varname]['xvarname'],
			    'yvarname': varnamedict[varname]['yvarname'],
                            'treename': 'laurelin',
                            'bck_mode': bckmodedict[bckmode],
                            'extracut': '',
                            'normalization': normdict[norm]['type'],
                            'xaxistitle': varnamedict[varname]['xaxtitle'],
                            'yaxistitle': varnamedict[varname]['yaxtitle'],
                            'xbins': binsdict[bins]['xbins'],
			    'ybins': binsdict[bins]['ybins'],
                            'histtitle': varnamedict[varname]['histtitle'],
			    'sidevarname': '_mass',
			    'sidexlow': 0.44,
			    'sidexhigh': 0.56,
			    'sidenbins': 30,
			    'xnormrange': normdict[norm]['xnormrange'],
			    'ynormrange': normdict[norm]['ynormrange'],
			    'eventtreename': 'nimloth'
			    })
		if bckmodedict[bckmode]=='default':
		    optionsdict['extracut']=extracut
		if options.testing: 
		    optionsdict['reductionfactor'] = 100

		for era in eralist:
		    # make a job submission script for this era with these plot options
		    thishistdir = os.path.join(options.filedir,'histograms',era['label'],
						'kshort',subfolder)
		    if os.path.exists(thishistdir):
			os.system('rm -r '+thishistdir)
		    os.makedirs(thishistdir)
		    thismcin = era['mcin']
		    thisdatain = era['datain']
		    
		    optionsdict['histtitle'] = varnamedict[varname]['histtitle']+' ({})'.format(era['label'])

		    optionstring = " 'histfile="+os.path.join(thishistdir,'histograms.root')+"'"
		    optionstring += " 'helpdir="+os.path.join(thishistdir,'temp')+"'"
		    optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
		    optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
		    optionstring += " 'outfile="+os.path.join(thishistdir,'figure.png')+"'"
		    for option in optionsdict.keys():
			optionstring += " '"+option+"="+str(optionsdict[option])+"'"
		    

		    scriptname = 'qjob_mcvsdata_submit.sh'
		    with open(scriptname,'w') as script:
			jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_20')
			script.write('python '+options.fillscript+optionstring+'\n')
			script.write('python '+options.plotscript+optionstring+'\n')
		    if options.testing:
			os.system('bash '+scriptname)
		    else:
			jobsub.submitQsubJob(scriptname)
