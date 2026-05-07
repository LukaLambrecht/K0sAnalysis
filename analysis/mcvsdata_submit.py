#######################################
# Fill and plot MC vs data histograms #
#######################################

import os
import sys
import json
import argparse
import importlib
import numpy as np
sys.path.append('../')
import tools.condortools as ct
from mcvsdata_getfiles import getfiles
CMSSW = '/user/jbierken/CMSSW_15_0_17'


if __name__=='__main__':

    # read command-line arguments
    parser = argparse.ArgumentParser( description = 'Submit analysis' )
    # general arguments
    parser.add_argument('-i', '--filedir',    required=True,        type=os.path.abspath)
    parser.add_argument('-v', '--version',    required=True)
    parser.add_argument('-c', '--config',     required=True)
    parser.add_argument('-o', '--outputdir',  required=True)
    parser.add_argument('-e', '--eras',       default=['default'],  nargs='+')
    parser.add_argument('-n', '--nprocess',   default=-1,           type=int)
    parser.add_argument(      '--dodetector', default=False,        action='store_true')
    parser.add_argument(      '--runmode',    default='local',      choices=['local', 'condor'])
    parser.add_argument(      '--outrootfile',default=None)
    parser.add_argument(      '--fitstrategy', default='legacy',    choices=['legacy', 'adaptive'])
    args = parser.parse_args()

    # manage input arguments to get files
    includelist           = args.eras
    if 'default' in includelist:
        if args.version=='run2preul':
            includelist     = ([
                            '2016PreVFP',       # split of 2016 file based on run ranges
                            '2016PostVFP',      # split of 2016 file based on run ranges
                            '2016',
                            '2017',
                            '2018',
                            'run2'
                        ])
        elif args.version=='run2ul':
            includelist     = ([
                            #'2016PreVFP',
                            #'2016PostVFP',
                            #'2016',
                            #'2017',
                            '2018',
                            #'run2'
                        ])
        elif args.version=='run3':
            includelist     = ([
                            ## Run2022 
                            #'2022',
                            #'2022preEE',
                            #'2022postEE',
                            #'2022combined',
                            ## Run2023
                            #'2023',
                            #'2023preBPix',
                            #'2023postBPix',
                            #'2023combined',
                            ## Run2024 
                            '2024',
                            ## Run2025 
                            '2025',
                            ## Run-3 
                            'run3'
                        ])
    elif 'perera' in includelist:
        if args.version=='run2preul':
            includelist       = [
                            '2016B',
                            '2016C',
                            '2016D',
                            '2016E',
                            '2016F',
                            '2016G',
                            '2016H'
                        ]
        elif args.version=='run2ul':
            includelist       = ([
                            '2016PreVFPB',
                            '2016PreVFPC',
                            '2016PreVFPD',
                            '2016PreVFPE',
                            '2016PreVFPF',
                            '2016PostVFPF',
                            '2016PostVFPG',
                            '2016PostVFPH'
                        ])
        elif args.version=='run3':
            includelist     = ([
                            ## Run2022preEE 
                            #'2022preEEB',
                            #'2022preEEC',
                            #'2022preEED',
                            ## Run2022postEE 
                            #'2022postEEE',
                            #'2022postEEF',
                            #'2022postEEG',
                            ## Run2023preBPix
                            #'2023preBPixB',
                            #'2023preBPixC',
                            ## Run2023postBPix
                            #'2023postBPixD',
                            ## Run2024 
                            '2024C',
                            '2024D',
                            '2024E',
                            '2024F',
                            '2024G',
                            '2024H',
                            '2024I',
                            ## Run2025 
                            '2025B',
                            '2025C',
                            '2025D',
                            '2025E',
                            '2025F',
                            '2025G',
                        ])
    elif 'detector' in includelist:
        if args.version=='run2preul':
            includelist       = ([
                            '2016PreVFP',
                            '2016PostVFP',
                            '2016',
                            '2017',
                            '2018',
                            '20172018'
                        ])
        elif args.version=='run2ul':
            includelist       = ([
                            '2016PreVFP',
                            '2016PostVFP',
                            '2016',
                            '2017',
                            '2018',
                            '20172018',
                        ])
        elif args.version=='run3':
            includelist     = ([
                            '2022preEE',
                            #'2022postEE',
                            #'2022',
                            #'2023preBPix',
                            #'2023postBPix',
                            #'2023',
                            #'2024',
                            #'run3'
                        ])
    kwargs                = {}
    if args.version=='run2preul':
        kwargs['filemode']  = 'new'             # hard-coded setting to run on either new or old convention

    # fill eralist with files to run on and related properties
    eralist               = getfiles( args.filedir, includelist, args.version, 
                                check_exist=True, **kwargs)

    # read variable configuration
    if args.config.endswith('.json'):
        with open(args.config) as f:
            settings          = json.load(f)
    elif args.config.endswith('.py'):
        settings            = importlib.import_module(args.config.replace('.py','')).config
    else:
        msg = 'ERROR: file extension not recognized for config file {}'.format(args.config)
        raise Exception(msg)
    varnames              = list(settings.keys())

    # loop over eras
    for era in eralist:
        # set output directory
        thiseradir              = os.path.join(args.outputdir,era['label'])
        if not os.path.exists(thiseradir): os.makedirs(thiseradir)
    
        # write input configuration
        configjson              = os.path.join(thiseradir, 'config.json')
        with open(configjson, 'w') as f:
            json.dump(era, f)
    
        # loop over variables and corresponding settings
        for varname in varnames:
            variable              = settings[varname]
            for bkgmodename, bkgmode in variable['bkgmodes'].items():
                for normname, norm  in variable['normalization'].items():
                    for binname, bins in variable['bins'].items():
                        # define output directory
                        subfolder       = '{}_{}_{}_{}'.format(varname, bkgmodename, normname, binname)
                        thisvardir      = os.path.join(thiseradir, subfolder)
                        if not os.path.exists(thisvardir): os.makedirs(thisvardir)
                        # handle cases of 1D or 2D binning
                        if 'yvariablename' in variable.keys():
                            ybins         = bins['ybins']
                            bins          = bins['xbins']
                        # write main variable
                        variabledict    = ({
                                            'name':       varname,
                                            'label':      variable['xaxtitle'],
                                            'variable':   variable['variablename'],
                                            'bins':       list(bins)
                                        })
                        varjson         = os.path.join(thisvardir, 'variable.json')
                        with open(varjson, 'w') as f:
                            json.dump(variabledict, f)
                        # write secondary variable
                        if 'yvariablename' in variable.keys():
                            yvariabledict = ({
                                            'name':     varname,
                                            'label':    variable['yaxtitle'],
                                            'variable': variable['yvariablename'],
                                            'bins':     list(ybins)
                                        })
                            yvarjson      = os.path.join(thisvardir, 'yvariable.json')
                            with open(yvarjson, 'w') as f:
                                json.dump(yvariabledict, f)
                        # write normalization variable
                        if norm['type']=='range':
                            normvariabledict = ({
                                            'name':     norm['normvariable'],
                                            'label':    norm['normvariable'],
                                            'variable': norm['normvariable'],
                                            'bins':     list(norm['normrange'])
                                        })
                            normvarjson   = os.path.join(thisvardir, 'normvariable.json')
                            with open(normvarjson, 'w') as f:
                                json.dump(normvariabledict, f)
                        # write sideband variable
                        if bkgmode['type']=='sideband':
                            sidevariabledict = ({
                                            'name':     bkgmode['sidevariable'],
                                            'label':    bkgmode['sidevariable'],
                                            'variable': bkgmode['sidevariable'],
                                            'bins':     list(bkgmode['sidebins'])
                                        })
                            sidevarjson   = os.path.join(thisvardir, 'sidevariable.json')
                            with open(sidevarjson, 'w') as f:
                                json.dump(sidevariabledict, f)
            
                        # make extra info to display on plot
                        extrainfos      = []
                        if 'extrainfos' in variable.keys():     extrainfos = variable['extrainfos'][:]
                        if 'info' in bkgmode.keys():            extrainfos.append(bkgmode['info'])
                        if 'info' in norm.keys():               extrainfos.append(norm['info'])
                        doextrainfos    = True if len(extrainfos)>0 else False
           
                        # make command for filling
                        cmds                                        = []
                        histfile                                    = os.path.join(thisvardir, 'histograms.root')
                        outputfile                                  = os.path.join(thisvardir, '{}.png'.format(varname))
                        if args.outrootfile is not None: outroot    = os.path.join(thisvardir, '{}.root'.format(varname))
            
                        cmd = 'python3 mcvsdata_fill.py'
                        cmd += ' -i {}'.format(configjson)
                        cmd += ' -t {}'.format(variable['treename'])
                        cmd += ' -v {}'.format(varjson)
                        cmd += ' -o {}'.format(histfile)
                        if args.nprocess>0:                     cmd += ' -n {}'.format(args.nprocess)
                        cmd += ' --fitstrategy {}'.format(args.fitstrategy)
                        # add args for normalization
                        if norm['type'] is not None:            cmd += ' --normmode {}'.format(norm['type'])
                        if norm['type']=='range':               cmd += ' --normvariable {}'.format(normvarjson)
                        if norm['type']=='eventyield':          cmd += ' --eventtreename nimloth'
                        # (hard-coded for now, maybe extend later)
                        # add args for background subtraction
                        if bkgmode['type'] is not None:         cmd += ' --bkgmode {}'.format(bkgmode['type'])
                        if bkgmode['type']=='sideband':
                            cmd += ' --sidevariable {}'.format(sidevarjson)
                            cmd += ' --sideplotdir {}'.format(os.path.join(thisvardir, 'sideband'))
                        # add args for secondary variable
                        if 'yvariablename' in variable.keys():  cmd += ' --yvariable {}'.format(yvarjson)
                        cmds.append(cmd)
            
                        # ------------------------------------------------------------------------------------------
                        # make basic command for plotting data vs MC (integral)
                        # ------------------------------------------------------------------------------------------
                        exe = 'mcvsdataplotter.py'
                        if 'yvariablename' in variable.keys(): exe = 'mcvsdataplotter2d.py'
                        cmd = 'python3 ../plotting/{}'.format(exe)
                        cmd += ' -i {}'.format(histfile)
                        cmd += ' --xaxtitle \'{}\''.format(variable['xaxtitle'])
                        cmd += ' --extracmstext Preliminary'
                        # special cases for plotting command
                        # note: bin width is added to y-axis title (on request),
                        #       this assumes all bins have equal width...
                        #       it will give nonsense on non-equal binnings,
                        #       but some people have very strong feelings about this,
                        #       so temporarily implemented this comment anyway,
                        #       comment out if not needed.
                        yaxtitle = variable['yaxtitle']
                        #yaxtitle += ' (/ {:.1f} cm)'.format(bins[1]-bins[0])
                        cmd += ' --yaxtitle \'{}\''.format(yaxtitle)
                        if args.version=='run2ul':              cmd += ' --extralumitext Legacy'
                        if args.version=='run2preul':           cmd += ' --extralumitext Pre-legacy'
                        #if args.version=='run3':                cmd += ' --extralumitext '
                        if args.dodetector:
                            if '2016' in era['label']:            cmd += ' --do2016pixel'
                            if '2017' in era['label']:            cmd += ' --do20172018pixel'
                            if '2018' in era['label']:            cmd += ' --do20172018pixel'
                            if '2022' in era['label']:            cmd += ' --do20172018pixel'
                        extrainfos2 = extrainfos
                        if exe=='mcvsdataplotter2d.py':
                            cmd += ' --outrootfile {}'.format(outroot)  
                            eratxt = era['label']
                            if eratxt=='run2': 
                                eratxt = 'Run-II'
                                eratxt = eratxt.replace('PreVFP', ' (old APV)')
                                eratxt = eratxt.replace('PostVFP', ' (new APV)')
                            extrainfos = ['{} data / sim.'.format(eratxt)] + extrainfos
                            doextrafinos = True
                        if doextrainfos:
                            cmd += ' --doextrainfos'
                            cmd += ' --extrainfos \'{}\''.format(','.join(extrainfos))
            
                        # first variation: default
                        cmd1 = cmd + ' -o {}'.format(outputfile)
                        cmds.append(cmd1)
            
                        # second variation: y-axis in log scale (only for 1D plots)
                        if exe=='mcvsdataplotter.py':
                            cmd2 = cmd + ' -o {}'.format(outputfile.replace('.png','_log.png'))
                            cmd2 += ' --logy'
                            cmds.append(cmd2)
                        
                        '''
                        # ------------------------------------------------------------------------------------------
                        # make basic command for plotting data vs MC (confidence)
                        # ------------------------------------------------------------------------------------------
                        if 'yvariablename' in variable.keys(): 
                            histname = histfile.split(".")
                            histname = histname[0] + "_confidence.root"
                           
                            exe = 'mcvsdataplotter2d.py'
                            cmd = 'python3 ../plotting/{}'.format(exe)
                            cmd += ' -i {}'.format(histname)
                            cmd += ' --xaxtitle \'{}\''.format(variable['xaxtitle'])
                            cmd += ' --extracmstext Preliminary'
                            # special cases for plotting command
                            # note: bin width is added to y-axis title (on request),
                            #       this assumes all bins have equal width...
                            #       it will give nonsense on non-equal binnings,
                            #       but some people have very strong feelings about this,
                            #       so temporarily implemented this comment anyway,
                            #       comment out if not needed.
                            yaxtitle = variable['yaxtitle']
                            #yaxtitle += ' (/ {:.1f} cm)'.format(bins[1]-bins[0])
                            cmd += ' --yaxtitle \'{}\''.format(yaxtitle)
                            if args.version=='run2ul':              cmd += ' --extralumitext Legacy'
                            if args.version=='run2preul':           cmd += ' --extralumitext Pre-legacy'
                            if args.version=='run3':                cmd += ' --extralumitext Run-3'
                            if args.dodetector:
                                if '2016' in era['label']:            cmd += ' --do2016pixel'
                                if '2017' in era['label']:            cmd += ' --do20172018pixel'
                                if '2018' in era['label']:            cmd += ' --do20172018pixel'
                            outroot = outroot.split(".")
                            outroot = outroot[0] + "_confidence.root"
                            cmd += ' --outrootfile {}'.format(outroot)  
                            eratxt = era['label']
                            if eratxt=='run2': 
                                eratxt = 'Run-II'
                                eratxt = eratxt.replace('PreVFP', ' (old APV)')
                                eratxt = eratxt.replace('PostVFP', ' (new APV)')
                            #extrainfos = ['{} data / sim.'.format(eratxt)] + extrainfos
                            doextrafinos = True
                            if doextrainfos:
                                cmd += ' --doextrainfos'
                                cmd += ' --extrainfos \'{}\''.format(','.join(extrainfos))
                            
                            # first variation: default
                            outputfile = outputfile.split(".")
                            outputfile = outputfile[0] + "_confidence.png"
                            cmd1 = cmd + ' -o {}'.format(outputfile)
                            cmds.append(cmd1)
                            
                            # ------------------------------------------------------------------------------------------
                            # make basic command for plotting (data@95%MC) vs (data) 
                            # ------------------------------------------------------------------------------------------
                            histname = histfile.split(".")
                            histname = histname[0] + "_confidence.root"
                            
                            exe = 'datavsdataplotter2d.py'
                            cmd = 'python3 ../plotting/{}'.format(exe)
                            cmd += ' -i {}'.format(histname)
                            cmd += ' --xaxtitle \'{}\''.format(variable['xaxtitle'])
                            cmd += ' --extracmstext Preliminary'
                            # special cases for plotting command
                            # note: bin width is added to y-axis title (on request),
                            #       this assumes all bins have equal width...
                            #       it will give nonsense on non-equal binnings,
                            #       but some people have very strong feelings about this,
                            #       so temporarily implemented this comment anyway,
                            #       comment out if not needed.
                            yaxtitle = variable['yaxtitle']
                            #yaxtitle += ' (/ {:.1f} cm)'.format(bins[1]-bins[0])
                            cmd += ' --yaxtitle \'{}\''.format(yaxtitle)
                            if args.version=='run2ul':              cmd += ' --extralumitext Legacy'
                            if args.version=='run2preul':           cmd += ' --extralumitext Pre-legacy'
                            if args.version=='run3':                cmd += ' --extralumitext Run-3'
                            if args.dodetector:
                                if '2016' in era['label']:            cmd += ' --do2016pixel'
                                if '2017' in era['label']:            cmd += ' --do20172018pixel'
                                if '2018' in era['label']:            cmd += ' --do20172018pixel'
                            outroot = outroot.split(".")
                            outroot = outroot[0] + "_data_vs_data.root"
                            cmd += ' --outrootfile {}'.format(outroot)  
                            eratxt = era['label']
                            if eratxt=='run2': 
                                eratxt = 'Run-II'
                                eratxt = eratxt.replace('PreVFP', ' (old APV)')
                                eratxt = eratxt.replace('PostVFP', ' (new APV)')
                            extrainfos2 = [r'{} '.format(eratxt) + r'$N_{data}^{2.5\sigma_{data}} / N_{data}^{2.5\sigma_{MC}}$.'] + extrainfos2
                            #extrainfos2 = ['{} .'.format(eratxt)] + ['data@95%MC / data.'] + extrainfos2
                            doextrafinos = True
                            if doextrainfos:
                                cmd += ' --doextrainfos'
                                cmd += ' --extrainfos \'{}\''.format(','.join(extrainfos2))
                            
                            # first variation: default
                            outputfile = outputfile.split(".")
                            outputfile = outputfile[0] + "_data_vs_data.png"
                            cmd1 = cmd + ' -o {}'.format(outputfile)
                            cmds.append(cmd1)
                        '''
                        
                        # ------------------------------------------------------------------------------------------
                        # run or submit commands
                        # ------------------------------------------------------------------------------------------
                        #print(cmds)
                        scriptname = 'cjob_mcvsdata_submit.sh'
                        if args.runmode=='local':
                            for cmd in cmds: os.system(cmd)
                        else:
                            store_dir = CMSSW + '/src/K0sAnalysis/log_automatic_jobs/'
                            ct.submitCommandsAsCondorJob(store_dir + scriptname, cmds, cmssw_version=CMSSW)
