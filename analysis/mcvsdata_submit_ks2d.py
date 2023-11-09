##################################################################
# Fill and plot MC vs data histograms for K0s RPV variable in 2D #
##################################################################

import json
import os
import sys
import numpy as np
sys.path.append('../tools')
import condortools as ct
import lumitools
import optiontools as opt
from mcvsdata_getfiles import getfiles

### global settings
options = []
options.append( opt.Option('filedir', vtype='path') )
options.append( opt.Option('version') )
options.append( opt.Option('fillscript', default='mcvsdata_fill2d.py') )
options.append( opt.Option('plotscript', default='../plotting/mcvsdataplotter2d.py') )
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
variables = ['rpv_vs_pt']
settings = ({
  'rpv_vs_pt': {'xvarname': '_RPV', 'xaxtitle': '#Delta_{2D} (cm)',
		'yvarname': '_pt', 'yaxtitle': 'p_{T} (GeV)',
		'histtitle': 'Data / Simulation',
                'bckmodes': {'bcksideband': 'sideband'},
                'extracut': 'bool(2>1)',
                # note: extracut will only be applied in case of no background subtraction
                # and mainly for testing, not recommended to be used.
                'bins': {
	          'defaultbins':{ 'xbins':json.dumps([0.,0.5,1.5,4.5,20.],separators=(',',':')),
			          'ybins':json.dumps([0.,5.,10.,20.],separators=(',',':')) },
                  'finexbins':{ 'xbins':json.dumps([0.,0.5,1.,1.5,2.,5.,10.,15.,20.],separators=(',',':')),
                                'ybins':json.dumps([0.,5.,10.,20.],separators=(',',':')) },
                },
                'normalization': {
	          'norm3small':{ 'type':3,'xnormrange':json.dumps([0.,0.5],separators=(',',':')),
			         'ynormrange':json.dumps([0.,20.],separators=(',',':'))}
	        } 
  }
})

for varname in variables
    variable = settings[varname]
    for bckmodename, bckmode in variable['bckmodes'].items():
	for normname, norm in variable['normalization'].items():
	    for binname, bins in variable['bins'].items():
		subfolder = '{}_{}_{}_{}'.format(varname, bckmodename, normname, binname)
		optionsdict = ({ 'xvarname': variable['xvarname'],
			    'yvarname': variable['yvarname'],
                            'treename': 'laurelin',
                            'bck_mode': bckmode,
                            'extracut': '',
                            'normalization': norm['type'],
                            'xaxistitle': variable['xaxtitle'],
                            'yaxistitle': variable['yaxtitle'],
                            'xbins': bins['xbins'],
			    'ybins': bins['ybins'],
                            'histtitle': variable['histtitle'],
			    'sidevarname': '_mass',
			    'sidexlow': 0.44,
			    'sidexhigh': 0.56,
			    'sidenbins': 30,
			    'xnormrange': norm['xnormrange'],
			    'ynormrange': norm['ynormrange'],
			    'eventtreename': 'nimloth'
			    })
		if bckmode=='default':
		    optionsdict['extracut']=variable['extracut']
		if options.testing:
                    # run on a subset of era only
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
		    
		    optionsdict['histtitle'] = (varnamedict[varname]['histtitle']
						+' ({})'.format(era['label']))

		    optionstring = " 'histfile="+os.path.join(thishistdir,'histograms.root')+"'"
		    optionstring += " 'helpdir="+os.path.join(thishistdir,'temp')+"'"
		    optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
		    optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
		    optionstring += " 'outfile="+os.path.join(thishistdir,'figure.png')+"'"
		    optionstring += " 'outrootfile="+os.path.join(thishistdir,'scalefactors.root')+"'"
		    for option in optionsdict.keys():
			optionstring += " '"+option+"="+str(optionsdict[option])+"'"
                    optionstring += " 'doextrainfos=True'"
		    
                    # make commands
                    cmds = []
                    cmds.append('python '+options.fillscript+optionstring)
                    cmds.append('python '+options.plotscript+optionstring)
                    # run or submit commands
                    scriptname = 'cjob_mcvsdata_submit_ks2d.sh'
                    if options.testing:
                        for cmd in cmds: os.system(cmd)
                    else:
                        ct.submitCommandsAsCondorJob(scriptname, cmds,
                            cmssw_version='/user/llambrec/CMSSW_10_2_20')
