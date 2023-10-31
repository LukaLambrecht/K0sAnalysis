######################################################################
# Helper function to get the right files in a conventional structure #
######################################################################

import json
import os
import sys
import numpy as np
sys.path.append(os.path.abspath('../../tools'))
import lumitools

def getfiles( filedir, includelist, version, check_exist=False, **kwargs ):
    if version=='run2preul': eralist = getfiles_run2preul( filedir, includelist, **kwargs )
    elif version=='run2ul': eralist = getfiles_run2ul( filedir, includelist, **kwargs )
    else: raise Exception('ERROR: version {} not recognized'.format(version))

    if check_exist:
      # check if all files exist
      allexist = True
      for era in eralist:
        for mcfile in era['mcin']:
            if not os.path.exists(mcfile['file']):
                print('ERROR: following input file does not exist: '+mcfile['file'])
                allexist = False
        for datafile in era['datain']:
            if not os.path.exists(datafile['file']):
                print('ERROR: following input file does not exist: '+datafile['file'])
                allexist = False
      if not allexist: raise Exception('ERROR: some requested files do not exist.')

    return eralist


def getfiles_run2ul( filedir, includelist ):
    
    # initializations
    eralist = []
    mcdirdict = {}
    mcdirdict['2016PreVFP'] = 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_crab_RunIISummer20UL16MiniAODAPVv2-106X_mcRun2_asymptotic_preVFP_v11-v1_sim_dyjetstoll'
    mcdirdict['2016PostVFP'] = 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_crab_RunIISummer20UL16MiniAODv2-106X_mcRun2_asymptotic_v17-v1_sim_dyjetstoll'
    mcdirdict['2017'] = 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_sim_dyjetstoll'
    mcdirdict['2018'] = 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_sim_dyjetstoll'
    datadirdict = {}
    datadirdict['2016PreVFP'] = 'DoubleMuon_Run2016PreVFP'
    datadirdict['2016PreVFPB'] = 'DoubleMuon_crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PreVFPC'] = 'DoubleMuon_crab_Run2016C-HIPM_UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PreVFPD'] = 'DoubleMuon_crab_Run2016D-HIPM_UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PreVFPE'] = 'DoubleMuon_crab_Run2016E-HIPM_UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PreVFPF'] = 'DoubleMuon_crab_Run2016F-HIPM_UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PostVFP'] = 'DoubleMuon_Run2016PostVFP'
    datadirdict['2016PostVFPF'] = 'DoubleMuon_crab_Run2016F-UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PostVFPG'] = 'DoubleMuon_crab_Run2016G-UL2016_MiniAODv2-v1_data_doublemuon'
    datadirdict['2016PostVFPH'] = 'DoubleMuon_crab_Run2016H-UL2016_MiniAODv2-v2_data_doublemuon'
    datadirdict['2017'] = 'DoubleMuon_Run2017'
    datadirdict['2017B'] = 'DoubleMuon_crab_Run2017B-UL2017_MiniAODv2-v1_data_doublemuon'
    datadirdict['2017C'] = 'DoubleMuon_crab_Run2017C-UL2017_MiniAODv2-v1_data_doublemuon'
    datadirdict['2017D'] = 'DoubleMuon_crab_Run2017D-UL2017_MiniAODv2-v1_data_doublemuon'
    datadirdict['2017E'] = 'DoubleMuon_crab_Run2017E-UL2017_MiniAODv2-v1_data_doublemuon'
    datadirdict['2017F'] = 'DoubleMuon_crab_Run2017F-UL2017_MiniAODv2-v1_data_doublemuon'
    datadirdict['2018'] = 'DoubleMuon_Run2018'
    datadirdict['2018A'] = 'DoubleMuon_crab_Run2018A-UL2018_MiniAODv2-v1_data_doublemuon'
    datadirdict['2018B'] = 'DoubleMuon_crab_Run2018B-UL2018_MiniAODv2-v1_data_doublemuon'
    datadirdict['2018C'] = 'DoubleMuon_crab_Run2018C-UL2018_MiniAODv2-v1_data_doublemuon'
    datadirdict['2018D'] = 'DoubleMuon_crab_Run2018D-UL2018_MiniAODv2-v1_data_doublemuon'
    filename = 'selected.root'

    # loop over eras
    for era in includelist:

        # skip special cases (consider them later)
        if era=='run2': continue
        if era=='20172018': continue
        if era=='2016': continue
        # derive year from era name
        year = era.rstrip('ABCDEFGH')
        # set MC file and data file
        mcdir = mcdirdict[year]
        datadir = datadirdict[era]
        # make an entry for this era
        mcin = ([{ 'file':os.path.join(filedir, mcdir, filename),
                'label':era+' sim.', 'xsection':6077.22,
                'luminosity':lumitools.getlumi('run2ul', era)*1000}])
        datain = ([{'file':os.path.join(filedir, datadir, filename),
                'label':era+' data','luminosity':lumitools.getlumi('run2ul', era)*1000}])
        label = era
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    # special case
    if '20172018' in includelist:
        mcin = []
        datain = []
        for year in ['2017', '2018']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':'{} sim.'.format(year), 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2ul', year)*1000})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':'{} data'.format(year),
                   'luminosity':lumitools.getlumi('run2ul', year)*1000})
        label = '20172018'
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    # special case
    if '2016' in includelist:
        mcin = []
        datain = []
        for year in ['2016PreVFP', '2016PostVFP']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':'{} sim.'.format(year), 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2ul', year)*1000})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':'{} data'.format(year),
                   'luminosity':lumitools.getlumi('run2ul', year)*1000})
        label = '2016'
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    # special case
    if 'run2' in includelist:
        mcin = []
        datain = []
        for year in ['2016PreVFP', '2016PostVFP', '2017', '2018']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':'{} sim.'.format(year), 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2ul', year)*1000})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':'{} data'.format(year),
                   'luminosity':lumitools.getlumi('run2ul', year)*1000})
        label = 'run2'
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    return eralist


def getfiles_run2preul( filedir, includelist, filemode='old' ):

    eralist = []
    for era in includelist:
        # skip special cases (consider them later)
        if era=='run2': continue
        if era=='20172018': continue
        # set MC file and data file
        if filemode == 'new':
            mcdir = 'DYJetsToLL_'+era.rstrip('ABCDEFGH')
            datadir = 'DoubleMuon_Run'+era
            filename = 'merged_selected.root'
        elif filemode == 'old':
            mcdir = 'RunIISummer16_DYJetsToLL'
            if '2017' in era: mcdir = 'RunIIFall17_DYJetsToLL'
            if '2018' in era: mcdir = 'RunIIAutumn18_DYJetsToLL'
            datadir = 'Run'+era+'_DoubleMuon'
            filename = 'skim_ztomumu_all.root'
        else:
            raise Exception('ERROR: filemode "{}" not recognized.'.format(filemode))
        mcin = ([{ 'file':os.path.join(filedir,mcdir,filename), 
		'label':era+' sim.', 'xsection':6077.22,
		'luminosity':lumitools.getlumi('run2preul', era)*1000}])
        datain = ([{'file':os.path.join(filedir,datadir,filename), 
		'label':era+' data','luminosity':lumitools.getlumi('run2preul', era)*1000}])
        label = era
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if '20172018' in includelist:
        mcin = []
        datain = []
        if filemode=='old':
            filename = 'skim_ztomumu_all.root'
            # 2017
            mcin.append({ 'file':os.path.join(filedir,'RunIIFall17_DYJetsToLL',filename),
                  'label':'2017 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2preul', '2017')*1000})
            datain.append({'file':os.path.join(filedir,'Run2017_DoubleMuon',filename),
                   'label':'2017 data','luminosity':lumitools.getlumi('run2preul', '2017')*1000})
            # 2018
            mcin.append({ 'file':os.path.join(filedir,'RunIIAutumn18_DYJetsToLL',filename),
                  'label':'2018 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2preul', '2018')*1000})
            datain.append({'file':os.path.join(filedir,'Run2018_DoubleMuon',filename),
                   'label':'2018 data','luminosity':lumitools.getlumi('run2preul', '2018')*1000})
        label = '20172018'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if 'run2' in includelist:
        mcin = []
        datain = []
        if filemode == 'old':
            filename = 'skim_ztomumu_all.root'
            # 2016
            mcin.append({ 'file':os.path.join(filedir,'RunIISummer16_DYJetsToLL',filename), 
                      'label':'2016 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('run2preul', '2016')*1000})
            datain.append({'file':os.path.join(filedir,'Run2016_DoubleMuon',filename), 
                       'label':'2016 data','luminosity':lumitools.getlumi('run2preul', '2016')*1000})
            # 2017
            mcin.append({ 'file':os.path.join(filedir,'RunIIFall17_DYJetsToLL',filename), 
                      'label':'2017 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('run2preul', '2017')*1000})
            datain.append({'file':os.path.join(filedir,'Run2017_DoubleMuon',filename), 
                       'label':'2017 data','luminosity':lumitools.getlumi('run2preul', '2017')*1000})
            # 2018
            mcin.append({ 'file':os.path.join(filedir,'RunIIAutumn18_DYJetsToLL',filename), 
                      'label':'2018 sim.', 'xsection':6077.22, 'luminosity':lumitools.getlumi('run2preul', '2018')*1000})
            datain.append({'file':os.path.join(filedir,'Run2018_DoubleMuon',filename), 
                       'label':'2018 data','luminosity':lumitools.getlumi('run2preul', '2018')*1000})
        elif filemode == 'new':
            filename = 'merged_selected.root'
            # 2016
            mcin.append({ 'file':os.path.join(filedir,'DYJetsToLL_2016',filename),
                  'label':'2016 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2preul', '2016')*1000})
            datain.append({'file':os.path.join(filedir,'DoubleMuon_Run2016',filename),
                   'label':'2016 data','luminosity':lumitools.getlumi('run2preul', '2016')*1000})
            # 2017
            mcin.append({ 'file':os.path.join(filedir,'DYJetsToLL_2017',filename),
                  'label':'2017 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2preul', '2017')*1000})
            datain.append({'file':os.path.join(filedir,'DoubleMuon_Run2017',filename),
                   'label':'2017 data','luminosity':lumitools.getlumi('run2preul', '2017')*1000})
            # 2018
            mcin.append({ 'file':os.path.join(filedir,'DYJetsToLL_2018',filename),
                  'label':'2018 sim.', 'xsection':6077.22,
                  'luminosity':lumitools.getlumi('run2preul', '2018')*1000})
            datain.append({'file':os.path.join(filedir,'DoubleMuon_Run2018',filename),
                   'label':'2018 data','luminosity':lumitools.getlumi('run2preul', '2018')*1000})
        label = 'Run-II'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # return the eralist
    return eralist
