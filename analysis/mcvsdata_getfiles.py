######################################################################
# Helper function to get the right files in a conventional structure #
######################################################################

import json
import os
import sys
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import tools.lumitools as lt

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
                'luminosity':lt.getlumi('run2ul', era)*1000,
                'era': era, 'year': year, 'campaign': 'run2ul'}])
        datain = ([{'file':os.path.join(filedir, datadir, filename),
                'label':era+' data','luminosity':lt.getlumi('run2ul', era)*1000,
                'era': era, 'year': year, 'campaign': 'run2ul'}])
        label = era
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    # special case
    if '20172018' in includelist:
        mcin = []
        datain = []
        for year in ['2017', '2018']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':'{} sim.'.format(year), 'xsection':6077.22,
                  'luminosity':lt.getlumi('run2ul', year)*1000,
                  'era': year, 'year': year, 'campaign': 'run2ul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':'{} data'.format(year),
                   'luminosity':lt.getlumi('run2ul', year)*1000,
                   'era': year, 'year': year, 'campaign': 'run2ul'})
        label = '20172018'
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    # special case
    if '2016' in includelist:
        mcin = []
        datain = []
        for year in ['2016PreVFP', '2016PostVFP']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':'{} sim.'.format(year), 'xsection':6077.22,
                  'luminosity':lt.getlumi('run2ul', year)*1000,
                  'era': year, 'year': year, 'campaign': 'run2ul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':'{} data'.format(year),
                   'luminosity':lt.getlumi('run2ul', year)*1000,
                   'era': year, 'year': year, 'campaign': 'run2ul'})
        label = '2016'
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    # special case
    if 'run2' in includelist:
        mcin = []
        datain = []
        for year in ['2016PreVFP', '2016PostVFP', '2017', '2018']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':'{} sim.'.format(year), 'xsection':6077.22,
                  'luminosity':lt.getlumi('run2ul', year)*1000,
                  'era': year, 'year': year, 'campaign': 'run2ul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':'{} data'.format(year),
                   'luminosity':lt.getlumi('run2ul', year)*1000,
                   'era': year, 'year': year, 'campaign': 'run2ul'})
        label = 'run2'
        eralist.append({'mcin':mcin, 'datain':datain, 'label':label})

    return eralist


def getfiles_run2preul( filedir, includelist, filemode='old' ):

    eralist = []
    mcdirdict = {}
    datadirdict = {}
    if filemode=='new':
      mcdirdict['2016'] = 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_crab_MiniAOD2016v3_ext2-v1_sim_RunIISummer16_DYJetsToLL'
      mcdirdict['2017'] = 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_crab_MiniAOD2017v2_ext1-v1_sim_RunIIFall17_DYJetsToLL'
      mcdirdict['2018'] = 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_crab_MiniAOD2018_ext2-v1_sim_RunIIAutumn18_DYJetsToLL'
      datadirdict['2016'] = 'DoubleMuon_Run2016'
      datadirdict['2016PreVFP'] = 'DoubleMuon_Run2016PreVFP'
      datadirdict['2016PostVFP'] = 'DoubleMuon_Run2016PostVFP'
      datadirdict['2016BtoF'] = 'DoubleMuon_Run2016BtoF'
      datadirdict['2016GtoH'] = 'DoubleMuon_Run2016GtoH'
      datadirdict['2016B'] = 'DoubleMuon_crab_Run2016B-17Jul2018_ver2-v1_data_Run2016_DoubleMuon'
      datadirdict['2016C'] = 'DoubleMuon_crab_Run2016C-17Jul2018-v1_data_Run2016_DoubleMuon'
      datadirdict['2016D'] = 'DoubleMuon_crab_Run2016D-17Jul2018-v1_data_Run2016_DoubleMuon'
      datadirdict['2016E'] = 'DoubleMuon_crab_Run2016E-17Jul2018-v1_data_Run2016_DoubleMuon'
      datadirdict['2016F'] = 'DoubleMuon_crab_Run2016F-17Jul2018-v1_data_Run2016_DoubleMuon'
      datadirdict['2016G'] = 'DoubleMuon_crab_Run2016G-17Jul2018-v1_data_Run2016_DoubleMuon'
      datadirdict['2016H'] = 'DoubleMuon_crab_Run2016H-17Jul2018-v1_data_Run2016_DoubleMuon'
      datadirdict['2017'] = 'DoubleMuon_Run2017'
      datadirdict['2017B'] = 'DoubleMuon_crab_Run2017B-31Mar2018-v1_data_Run2017_DoubleMuon'
      datadirdict['2017C'] = 'DoubleMuon_crab_Run2017C-31Mar2018-v1_data_Run2017_DoubleMuon'
      datadirdict['2017D'] = 'DoubleMuon_crab_Run2017D-31Mar2018-v1_data_Run2017_DoubleMuon'
      datadirdict['2017E'] = 'DoubleMuon_crab_Run2017E-31Mar2018-v1_data_Run2017_DoubleMuon'
      datadirdict['2017F'] = 'DoubleMuon_crab_Run2017F-31Mar2018-v1_data_Run2017_DoubleMuon'
      datadirdict['2018'] = 'DoubleMuon_Run2018'
      datadirdict['2018A'] = 'DoubleMuon_crab_Run2018A-17Sep2018-v2_data_Run2018_DoubleMuon'
      datadirdict['2018B'] = 'DoubleMuon_crab_Run2018B-17Sep2018-v1_data_Run2018_DoubleMuon'
      datadirdict['2018C'] = 'DoubleMuon_crab_Run2018C-17Sep2018-v1_data_Run2018_DoubleMuon'
      datadirdict['2018D'] = 'DoubleMuon_crab_Run2018D-PromptReco-v2_data_Run2018_DoubleMuon'
      filename = 'selected.root'
    elif filemode=='old':
        allyears = ['2016', '2017', '2018']
        alleras = (['2016B', '2016C', '2016D', '2016E', '2016F', '2016G', '2016H',
                '2017B', '2017C', '2017D', '2017E', '2017F',
                '2018A', '2018B', '2018C', '2018D'])
        mcdirdict['2016'] = 'RunIISummer16_DYJetsToLL'
        mcdirdict['2017'] = 'RunIIFall17_DYJetsToLL'
        mcdirdict['2018'] = 'RunIIAutumn18_DYJetsToLL'
        for year in allyears: datadirdict[year] = 'Run'+year+'_DoubleMuon'
        for era in alleras: datadirdict[era] = 'Run'+era+'_DoubleMuon'
        for grouped in ['2016BtoF', '2016GtoH']: datadirdict[grouped] = 'Run'+grouped+'_DoubleMuon'
        filename = 'skim_ztomumu_all.root'
    else: raise Exception('ERROR: filemode "{}" not recognized.'.format(filemode))
    
    for era in includelist:
        # skip special cases (consider them later)
        if era=='run2': continue
        if era=='20172018': continue
        if era=='2016BtoF': continue
        if era=='2016GtoH': continue
        if era=='2016PreVFP': continue
        if era=='2016PostVFP': continue
        # set MC file and data file
        year = era.strip('ABCDEFGH')
        mcin = ([{ 'file':os.path.join(filedir, mcdirdict[year], filename), 
		'label':era+' sim.', 'xsection':6077.22,
		'luminosity':lt.getlumi('run2preul', era)*1000,
                'era': era, 'year': year, 'campaign': 'run2preul'}])
        datain = ([{'file':os.path.join(filedir, datadirdict[era], filename), 
		'label':era+' data','luminosity':lt.getlumi('run2preul', era)*1000,
                'era': era, 'year': year, 'campaign': 'run2preul'}])
        label = era
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if '20172018' in includelist:
        mcin = []
        datain = []
        for year in ['2017', '2018']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename),
                  'label':year+' sim.', 'xsection':6077.22,
                  'luminosity':lt.getlumi('run2preul', year)*1000,
                  'era': year, 'year': year, 'campaign': 'run2preul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                   'label':year+' data','luminosity':lt.getlumi('run2preul', year)*1000,
                   'era': year, 'year': year, 'campaign': 'run2preul'})
        label = '20172018'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if 'run2' in includelist:
        mcin = []
        datain = []
        for year in ['2016', '2017', '2018']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict[year], filename), 
                      'label':year+' sim.', 'xsection':6077.22, 'luminosity':lt.getlumi('run2preul', year)*1000,
                      'era': year, 'year': year, 'campaign': 'run2preul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename), 
                       'label':year+' data','luminosity':lt.getlumi('run2preul', year)*1000,
                       'era': year, 'year': year, 'campaign': 'run2preul'})
        label = 'run2'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if '2016BtoF' in includelist:
        mcin = []
        datain = []
        for year in ['2016BtoF']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict['2016'], filename),
                      'label':'2016PreVFP sim.', 'xsection':6077.22, 'luminosity':lt.getlumi('run2preul', year)*1000,
                      'era': year, 'year': year, 'campaign': 'run2preul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                       'label':year+' data','luminosity':lt.getlumi('run2preul', year)*1000,
                       'era': year, 'year': year, 'campaign': 'run2preul'})
        label = '2016BtoF'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if '2016GtoH' in includelist:
        mcin = []
        datain = []
        for year in ['2016GtoH']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict['2016'], filename),
                      'label':'2016PostVFP sim.', 'xsection':6077.22, 'luminosity':lt.getlumi('run2preul', year)*1000,
                      'era': year, 'year': year, 'campaign': 'run2preul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                       'label':year+' data','luminosity':lt.getlumi('run2preul', year)*1000,
                       'era': year, 'year': year, 'campaign': 'run2preul'})
        label = '2016GtoH'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if '2016PreVFP' in includelist:
        mcin = []
        datain = []
        for year in ['2016PreVFP']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict['2016'], filename),
                      'label':'2016PreVFP sim.', 'xsection':6077.22, 'luminosity':lt.getlumi('run2preul', year)*1000,
                      'era': year, 'year': year, 'campaign': 'run2preul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                       'label':year+' data','luminosity':lt.getlumi('run2preul', year)*1000,
                       'era': year, 'year': year, 'campaign': 'run2preul'})
        label = '2016PreVFP'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})

    # special case
    if '2016PostVFP' in includelist:
        mcin = []
        datain = []
        for year in ['2016PostVFP']:
            mcin.append({ 'file':os.path.join(filedir, mcdirdict['2016'], filename),
                      'label':'2016PostVFP sim.', 'xsection':6077.22, 'luminosity':lt.getlumi('run2preul', year)*1000,
                      'era': year, 'year': year, 'campaign': 'run2preul'})
            datain.append({'file':os.path.join(filedir, datadirdict[year], filename),
                       'label':year+' data','luminosity':lt.getlumi('run2preul', year)*1000,
                       'era': year, 'year': year, 'campaign': 'run2preul'})
        label = '2016PostVFP'
        eralist.append({'mcin':mcin,'datain':datain,'label':label})


    # return the eralist
    return eralist
