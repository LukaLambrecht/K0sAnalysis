###############################################################
# Fill and plot MC vs data histograms for Lambda RPV variable #
###############################################################

import json
import os
import sys
import numpy as np
sys.path.append(os.path.abspath('../tools'))
import condortools as ct
import lumitools
import optiontools as opt
from mcvsdata_getfiles import getfiles

### global settings
options = []
options.append( opt.Option('filedir', vtype='path') )
options.append( opt.Option('version') )
options.append( opt.Option('fillscript', default='mcvsdata_fill.py') )
options.append( opt.Option('plotscript', default='../plotting/mcvsdataplotter.py') )
options.append( opt.Option('testing', vtype='bool', default=False) )
options.append( opt.Option('includelist', vtype='list', default=['default']) )
options.append( opt.Option('outputdir', default='output_test') )
options = opt.OptionCollection( options )
if len(sys.argv)==1:
    print('Use with following options:')
    print(options)
    sys.exit()
else:
    options.parse_options( sys.argv[1:] )
    print('Found following configuration:')
    print(options)

# manage input arguments to get files
includelist = options.includelist
if 'default' in includelist:
    if options.version=='run2preul': includelist = ['2016', '2017', '2018', 'run2']
    elif options.version=='run2ul':
        includelist = ([
          '2016PreVFP',
          '2016PostVFP',
          '2016',
          '2017',
          '2018',
          'run2'
        ])
kwargs = {}
if options.version=='run2preul':
    kwargs['filemode'] = 'old' # hard-coded setting to run on either new or old convention

### fill eralist with files to run on and related properties
eralist = getfiles( options.filedir, includelist, options.version,
                    check_exist=True, **kwargs)

### fill plotlist with properties of plots to make
variables = ['rpv', 'rpvsig']
settings = ({
  'rpv': {'variablename':'_RPV','xaxtitle':'#Delta_{2D} (cm)', 'histtitle':'',
          'bckmodes': {
            'bckdefault': {'type':'default', 'info':'Background not subtracted'},
            'bcksideband': {'type':'sideband', 'info': 'Background subtracted'}
          },
          'extracut': 'bool(2>1)',
          # note: extracut will only be applied in case of no background subtraction 
          # and mainly for testing, not recommended to be used.
          'bins': {
            'finebins':json.dumps(list(np.linspace(0,20,num=41,endpoint=True)),separators=(',',':')),
	    'defaultbins':json.dumps([0.,0.5,1.5,4.,10.,20.],separators=(',',':')),
	  },
          'normalization': {
	    'norm1':{'type':1, 'info':'Normalized to luminosity', 'normvariable':'','normrange':''},
            'norm4':{'type':4, 'info':'Normalized to data events', 'normvariable':'','normrange':''},
            'norm3small':{'type':3, 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                          'normvariable': '_RPV', 'normrange':json.dumps([0.,0.5],separators=(',',':'))},
            'norm3med':{'type':3, 'info': 'Normalized for #Delta_{2D} in 0.5 - 1.5 cm',
                        'normvariable': '_RPV', 'normrange':json.dumps([0.5,1.5],separators=(',',':'))}
          },
  },
  'rpvsig': {'variablename':'_RSigPV', 'xaxtitle':'#Delta_{2D} significance', 'histtitle':'',
             'bckmodes': {
               'bcksideband': {'type':'sideband', 'info': 'Background subtracted'}
             },
             'extracut': 'bool(2>1)',
             'bins': {
               'finebins':json.dumps(list(np.linspace(0,600,num=61,endpoint=True)),separators=(',',':')),
             },
             'normalization': {
               'norm3small':{'type':3, 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                             'normvariable': '_RPV', 'normrange':json.dumps([0.,0.5],separators=(',',':'))},
             },
  }
})

### loop over configurations
for varname in variables:
    variable = settings[varname]
    for bckmodename, bckmode in variable['bckmodes'].items():
	for normname, norm in variable['normalization'].items():
	    for binname, bins in variable['bins'].items():
		subfolder = '{}_{}_{}_{}'.format(varname, bckmodename, normname, binname)
		optionsdict = ({ 'varname': variable['variablename'],
                            'treename': 'telperion',
                            'bck_mode': bckmode['type'],
                            'extracut': '',
                            'normalization': norm['type'],
                            'xaxistitle': variable['xaxtitle'],
                            'yaxistitle': 'Reconstructed vertices',
                            'bins': bins,
                            'histtitle': variable['histtitle'],
			    'sidevarname': '_mass',
			    'sidexlow': 1.08,
			    'sidexhigh': 1.15,
			    'sidenbins': 30,
                            'normvariable': norm['normvariable'],
			    'normrange': norm['normrange'],
			    'eventtreename': 'nimloth'
			    })
		if bckmode=='default':
		    optionsdict['extracut'] = variable['extracut']
		if options.testing:
                    # run on a subselection of eras only
                    eralist = [eralist[0]]
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
                    optionstring += " 'doextrainfos=True'"
                    extrainfos = '#Lambda^{0} candidates'+',{},{}'.format(bckmode['info'],norm['info'])
                    optionstring += " 'extrainfos={}'".format(extrainfos)
		    
		    # make commands
                    cmds = []
                    cmds.append('python '+options.fillscript+optionstring)
                    cmds.append('python '+options.plotscript+optionstring)
                    # run or submit commands
                    scriptname = 'cjob_mcvsdata_submit_la.sh'
                    if options.testing: 
                        for cmd in cmds: os.system(cmd)
                    else:
                        ct.submitCommandsAsCondorJob(scriptname, cmds,
                            cmssw_version='/user/llambrec/CMSSW_10_2_20')
