####################################
# submitter for filler and plotter #
####################################

import sys
import os
sys.path.append('../tools')
import jobsubmission as jobsub
import lumitools

### global settings
basedir = '/storage_mnt/storage/user/llambrec/K0sAnalysis/files'
filedir = os.path.join(basedir,'oldfiles')
includelist = []
#for era in ['2016B','2016C','2016D','2016E','2016F','2016G','2016H']: includelist.append(era)
#for era in ['2017B','2017C','2017D','2017E','2017F']: includelist.append(era)
#for era in ['2018A','2018B','2018C','2018D']: includelist.append(era)
includelist.append('2016')
includelist.append('2017')
includelist.append('2018')
# note: for full run-2 plots, one can simply hadd the file

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
    mcin = ({'file':os.path.join(filedir,mcdir,'skim_ztomumu_all.root'), 'label':'Simulation', 'xsection':6077.22,'luminosity':lumitools.getlumi(era)*1000})
    datain = ({'file':os.path.join(filedir,datadir,'skim_ztomumu_all.root'), 'label':era+' data','luminosity':lumitools.getlumi(era)*1000})
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label})

### check if all files exist
allexist = True
for era in eralist:
    if not os.path.exists(era['mcin']['file']):
        print('### ERROR ###: following input file does not exist: '+era['mcin']['file'])
        allexist = False
    if not os.path.exists(era['datain']['file']):
        print('### ERROR ###: following input file does not exist: '+era['datain']['file'])
        allexist = False
if not allexist: sys.exit()


for era in eralist:

    outfilebase = 'ksinvmass_'

    datafile = outfilebase+era['label']+'_data.root'
    datalabel = "'"+era['label']+' data'+"'"
    simfile = outfilebase+era['label']+'_sim.root'
    simlabel = 'Simulation'
    figure = outfilebase+era['label']+'_fig.png'

    # make commands for filling the histograms
    fillcmds = []
    fillcmd1 = 'python fitinvmass_fancy_fill.py {} {}'.format(era['mcin']['file'],simfile)
    fillcmd2 = 'python fitinvmass_fancy_fill.py {} {} {}'.format(era['datain']['file'],datafile,
		    era['datain']['luminosity'])
    fillcmds.append(fillcmd1)
    fillcmds.append(fillcmd2)

    # make command for fitting and plotting
    fitcmd = 'python fitinvmass_fancy_plot.py {} {} {} {} {}'.format(
		datafile,datalabel,simfile,simlabel,figure)

    scriptname = 'qsub_fitinvmass_fancy_submit.sh'
    with open(scriptname,'w') as script:
	jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
        for cmd in fillcmds: script.write(cmd+'\n')
        script.write(fitcmd+'\n')
    #os.system('bash '+scriptname)
    jobsub.submitQsubJob(scriptname)    
