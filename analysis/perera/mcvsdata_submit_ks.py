############################################################
# Fill and plot MC vs data histograms for K0s RPV variable #
############################################################
# Special case of making plots per era

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
options.append( opt.Option('version') )
options.append( opt.Option('testing', vtype='bool', default=False) )
options.append( opt.Option('includelist', vtype='list', default=['default']) )
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

# manage input arguments to get files
includelist = options.includelist
if 'default' in includelist:
    if options.version=='run2preul':
      includelist = ['2016B','2016C','2016D','2016E','2016F','2016G','2016H']
    elif options.version=='run2ul':
      includelist = ([
        '2016PreVFPB',
        '2016PreVFPC',
        '2016PreVFPD',
        '2016PreVFPE',
        '2016PreVFPF',
        '2016PostVFPF',
        '2016PostVFPG',
        '2016PostVFPH'
      ])
kwargs = {}
if options.version=='run2preul':
    kwargs['filemode'] = 'old' # hard-coded setting to run on either new or old convention

### fill eralist with files to run on and related properties
eralist = getfiles( options.filedir, includelist, options.version,
                    check_exist=True, **kwargs)

### fill plotlist with properties of plots to make
variables = ['rpv']
settings = ({
  'rpv': {'variablename':'_RPV', 'xaxtitle':'#Delta_{2D} (cm)', 'histtitle':'',
          'bckmodes': {
            'bcksideband': {'type':'sideband', 'info': 'Background subtracted'}
          },
          'extracut': 'bool(2>1)',
          # note: extracut will only be applied in case of no background subtraction
          # and mainly for testing, not recommended to be used.
          'bins': {
            'finebins':json.dumps(list(np.linspace(0,20,num=41,endpoint=True)),separators=(',',':')),
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
                            'treename': 'laurelin',
                            'bck_mode': bckmode['type'],
                            'extracut': '',
                            'normalization': norm['type'],
                            'xaxistitle': variable['xaxtitle'],
                            'yaxistitle': 'Reconstructed vertices',
                            'bins': bins,
                            'histtitle': variable['histtitle'],
                            'sidevarname': '_mass',
                            'sidexlow': 0.44,
                            'sidexhigh': 0.56,
                            'sidenbins': 30,
                            'normvariable': norm['normvariable'],
                            'normrange': norm['normrange'],
                            'eventtreename': 'nimloth'
                            })
                if bckmode['type']=='default':
                    optionsdict['extracut'] = variable['extracut']
                if options.testing:
                    # run on a subselection of eras only
                    eralist = [eralist[0]]
                    # run on a subselection of events only
                    optionsdict['reductionfactor'] = 100

		for era in eralist:
		    # make a job submission script for this era with these plot options
		    thishistdir = os.path.join(os.path.join(options.outputdir),
                                               era['label'],subfolder)
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
                    extrainfos = 'K^{0}_{S} candidates'+',{},{}'.format(bckmode['info'],norm['info'])
                    optionstring += " 'extrainfos={}'".format(extrainfos)		   
 
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
