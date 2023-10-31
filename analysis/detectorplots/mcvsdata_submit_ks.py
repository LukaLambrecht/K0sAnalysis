############################################################
# Fill and plot MC vs data histograms for K0s RPV variable #
############################################################
# Special case of making plots with pixel layer positions

import json
import os
import sys
import numpy as np
sys.path.append(os.path.abspath('../../tools'))
import condortools as ct
import lumitools
import optiontools as opt
sys.path.append(os.path.abspath('../'))
from mcvsdata_getfiles import getfiles

### global settings
options = []
options.append( opt.Option('filedir', vtype='path') )
options.append( opt.Option('testing', vtype='bool', default=False) )
options.append( opt.Option('includelist', vtype='list',
                    default=['2016','20172018']) )
options.append( opt.Option('outputdir', default=os.path.abspath('output_test')) )
options = opt.OptionCollection( options )
if len(sys.argv)==1:
    print('Use with following options:')
    print(options)
    sys.exit()
else:
    options.parse_options( sys.argv[1:] )
    print('Found following configuration:')
    print(options)

filemode = 'old' # hard-coded setting to run on either new or old convention

### fill eralist with files to run on and related properties
eralist = getfiles(options.filedir, options.includelist,
            filemode=filemode, check_exist=True)

### fill plotlist with properties of plots to make
plotlist = []
varnamedict = ({
	    'rpv':{'variablename':'_KsRPV',
                   'xaxtitle':'#Delta_{2D} (cm)',
		   'histtitle':''}
		})
bckmodedict = ({
            #'bckdefault':'default',
	    'bcksideband':'sideband'
		})
extracut = 'bool(2>1)'
# note: extracut will only be applied in case of no background subtraction and mainly for testing,
#	not recommended to be used.
binsdict = ({
	'finebins':json.dumps(list(np.linspace(0,20,num=40,endpoint=True)),separators=(',',':')),
	    })
normdict = ({
	'norm2':{'type':2,'normrange':''},
	'norm3small':{'type':3,'normrange':json.dumps([0.,0.5],separators=(',',':'))},
	    })

### loop over configurations
for varname in varnamedict:
    for bckmode in bckmodedict:
	for norm in normdict:
	    for bins in binsdict:
		subfolder = '{}_{}_{}_{}'.format(varname,bckmode,norm,bins)
		optionsdict = ({ 'varname': varnamedict[varname]['variablename'],
                            'treename': 'laurelin',
                            'bck_mode': bckmodedict[bckmode],
                            'extracut': '',
                            'normalization': normdict[norm]['type'],
                            'xaxistitle': varnamedict[varname]['xaxtitle'],
                            'yaxistitle': 'Reconstructed vertices',
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
		if options.testing:
                    # run on a subselection of eras only
                    #eralist = [eralist[0]]
                    # run on a subselection of events only
		    optionsdict['reductionfactor'] = 100

		for era in eralist:
		    # make a job submission script for this era with these plot options
		    thishistdir = os.path.join(options.outputdir,era['label'],subfolder)
		    if os.path.exists(thishistdir):
			os.system('rm -r '+thishistdir)
		    os.makedirs(thishistdir)
		    thismcin = era['mcin']
		    thisdatain = era['datain']
		    
		    optionstring = " 'histfile="+os.path.join(thishistdir,'histograms.root')+"'"
		    optionstring += " 'helpdir="+os.path.join(thishistdir,'temp')+"'"
		    optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
		    optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
		    optionstring += " 'outfile="+os.path.join(thishistdir,'figure.png')+"'"
		    for option in optionsdict.keys():
			optionstring += " '"+option+"="+str(optionsdict[option])+"'"
                    optionstring += " 'doextrainfos=True'"
                    if era['label']=='2016': optionstring += " 'do2016pixel=True'"
                    if era['label']=='20172018': optionstring += " 'do20172018pixel=True'"
                    optionstring += " 'logy=False'"
		    
		    # make commands
                    cmds = []
                    cmds.append('cd ../')
                    cmds.append('python mcvsdata_fill.py '+optionstring)
                    cmds.append('python ../plotting/mcvsdataplotter.py '+optionstring)
                    # run or submit commands
                    scriptname = 'cjob_mcvsdata_submit_ks.sh'
                    if options.testing: 
                        with open(scriptname,'w') as f:
                          for cmd in cmds: f.write(cmd+'\n')
                        os.system('bash {}'.format(scriptname))
                    else:
                        ct.submitCommandsAsCondorJob(scriptname, cmds,
                            cmssw_version='/user/llambrec/CMSSW_10_2_20')
