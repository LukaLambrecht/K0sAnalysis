##################################################################
# Fill and plot MC vs data histograms for some control variables #
##################################################################

import json
import os
import sys
import numpy as np
sys.path.append('../../tools')
import condortools as ct
import optiontools as opt
sys.path.append('../../analysis')
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

### fill varlist with variables to run on and related properties
varlist = []
varnamelist = ['_event_mll']
#varnamelist += ['_event_njets','_lPt','_lEta']
#varnamelist = ['_nimloth_Mll', '_nimloth_nJets', '_celeborn_lPt', '_celeborn_lEta']

for varname in varnamelist:

    if( varname=='_nimloth_Mll' or varname=='_event_mll' ):
        varlist.append({    'varname': varname,
                            'treename': 'nimloth',
                            'bck_mode': 'default', # "default" for no background subtraction
                            'extracut': '', 
                            'normalization': 1, # "1" for simple xsec and lumi normalization
                            'xaxistitle': 'Dilepton invariant mass (GeV)',
                            'yaxistitle': 'Events',
                            'bins': json.dumps(list(np.linspace(85,97,num=50,endpoint=True)),
                                        separators=(',',':')),
                        })

    elif( varname=='_nimloth_nJets' or varname=='_event_njets' ):
        varlist.append({    'varname': varname,
                            'treename': 'nimloth',
                            'bck_mode': 'default', # "default" for no background subtraction
                            'extracut': '', 
                            'normalization': 1, # "1" for simple xsec and lumi normalization
                            'xaxistitle': 'Number of jets',
                            'yaxistitle': 'Events',
                            'bins': json.dumps(list(np.linspace(-0.5,6.5,num=8,endpoint=True)),
                                        separators=(',',':')),
                        })

    elif( varname=='_celeborn_lPt' or varname=='_lPt' ):
        varlist.append({    'varname': varname,
                            'treename': 'celeborn',
                            'bck_mode': 'default', # "default" for no background subtraction
                            'extracut': '',
                            'normalization': 1, # "1" for simple xsec and lumi normalization
                            'xaxistitle': 'Lepton transverse momentum (GeV)',
                            'yaxistitle': 'Leptons',
                            'bins': json.dumps(list(np.linspace(25,125,num=50,endpoint=True)),
                                        separators=(',',':')),
                        })

    elif( varname=='_celeborn_lEta' or varname=='_lEta' ):
        varlist.append({    'varname': varname,
                            'treename': 'celeborn',
                            'bck_mode': 'default', # "default" for no background subtraction
                            'extracut': '',
                            'normalization': 1, # "1" for simple xsec and lumi normalization
                            'xaxistitle': 'Lepton pseudorapidity (GeV)',
                            'yaxistitle': 'Leptons',
                            'bins': json.dumps(list(np.linspace(-2.4,2.4,num=50,endpoint=True)),
                                        separators=(',',':')),
                        })
    else:
        print('### WARNING ###: variable name '+varname+' not recognized, skipping...')

### modify configuration in case of small tests
if options.testing:
    # run on a subselection of eras only
    eralist = [eralist[0]]
    # run on a subselection of variables only
    #varlist = [varlist[0]]
    # run on a subselection of events only
    #for i in range(len(varlist)): varlist[i]['reductionfactor'] = 100

### submit the jobs
# loop over eras
for era in eralist:
    # set output directory
    thishistdir = os.path.join(options.outputdir,era['label'])
    if not os.path.exists(thishistdir):
        os.makedirs(thishistdir)
    # set input files
    thismcin = era['mcin']
    thisdatain = era['datain']
    # loop over variables
    for var in varlist:
        # set hist title
        thistitle = ''
        if 'histtitle' in var.keys():
            thistitle = var['histtitle']+' ({})'.format(era['label'])
        # make option string
        optionstring = " 'histfile="+os.path.join(thishistdir,var['varname']+'.root')+"'"
        optionstring += " 'helpdir="+os.path.join(thishistdir,var['varname']+'_temp')+"'"
        optionstring += " 'mcin="+json.dumps(thismcin,separators=(",",":"))+"'"
        optionstring += " 'datain="+json.dumps(thisdatain,separators=(",",":"))+"'"
        optionstring += " 'outfile="+os.path.join(thishistdir,var['varname']+'.png')+"'"
        for option in var.keys():
            if option=='histtitle': continue
            optionstring += " '"+option+"="+str(var[option])+"'"
        optionstring += " 'histtitle="+thistitle+"'"
        optionstring += " 'doextrainfos=False'"
        # make commands
        cmds = []
        cmds.append('python3 '+options.fillscript+optionstring)
        cmds.append('python3 '+options.plotscript+optionstring)
        # run or submit commands
        scriptname = 'cjob_mcvsdata_submit_controlvars.sh'
        if options.testing:
            for cmd in cmds: os.system(cmd)
        else:
            ct.submitCommandsAsCondorJob(scriptname, cmds,
              cmssw_version='/user/llambrec/CMSSW_10_2_20')
