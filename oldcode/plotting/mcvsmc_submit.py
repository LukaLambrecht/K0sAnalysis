#########################################
# submit mcvsmc fillrd and plot methods #
#########################################
import json
import os
import sys
import pipes

filllist = []
plotlist = []

# global settings
histdir = '/storage_mnt/storage/user/llambrec/Kshort/histograms_mcvsmc'
fillscript = 'mcvsdata_fillrd.py'
plotscript = 'mcvsmc_plot.py'
scriptloc = os.path.abspath(os.getcwd())
includelist = (['2016','2017','2018'])
#includelist = (['2016B','2016C','2016D','2016E','2016F','2016G','2016H'])
#includelist = (['2017B','2017C','2017D','2017E','2017F'])
#includelist = (['2018A','2018B','2018C','2018D'])
datatype = 'sim' # choose from 'sim' or 'data'
tag = 'sim' # a runtime tag used to distinguish files and job scripts

# fill eralist with files to run on and related properties
inlist = []
xsec = 1.
lumi = 1.
if datatype=='sim':
    if '2016' in includelist:
        inlist.append({"file":"/storage_mnt/storage/user/llambrec/Kshort/files/RunIISummer16_DYJetsToLL/skim_ztomumu_all.root","label":r"2016 sim","xsection":xsec,"luminosity":lumi})
    if '2017' in includelist:
        inlist.append({"file":"/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL/skim_ztomumu_all.root","label":r"2017 sim","xsection":xsec,"luminosity":lumi})
    if '2018' in includelist:
        inlist.append({"file":"/storage_mnt/storage/user/llambrec/Kshort/files/RunIIAutumn18_DYJetsToLL/skim_ztomumu_all.root","label":r"2018 sim","xsection":xsec,"luminosity":lumi})
if datatype=='data':
    for era in includelist:
        inlist.append({"file":"/storage_mnt/storage/user/llambrec/Kshort/files/Run"+era+"_DoubleMuon/skim_ztomumu_all.root","label":era+" data","xsection":1.,"luminosity":1.})

# further settings
xaxistitle = 'radial distance (cm)'
yaxistitle = 'number of vertices (normalized to 1)'
ksextracut = 'bool(2>1)' # defautl if no extra cut required
# x-axis
ksvarname = '_KsRPV'
ksbins = [0.,0.5,1.5,4.,20.]
# title
kstitle = 'K^{0}_{S} vertex radial distance'

# arguments for filling and plotting script
filldict = ({'histfile':histdir+'/'+tag+'.root',
        'helpdir':histdir+'/'+tag+'_help/',
        'varname':ksvarname,'treename':'laurelin',
        'bck_mode':str(2),'extracut':ksextracut,
        'massvar':'_KsInvMass','mxlow':str(0.44),'mxhigh':str(0.56),'mnbins':str(30),
        'bintype':'variable','bins':json.dumps(ksbins,separators=(",",":")),
        'normalization':str(5),'normrange':json.dumps([0.,0.5],separators=(",",";"))})
if datatype=='sim':
    filldict['mcin'] = json.dumps(inlist,separators=(",",":"))
    filldict['datain'] = json.dumps([],separators=(",",":"))
else:
    filldict['mcin'] = json.dumps([],separators=(",",":"))
    filldict['datain'] = json.dumps(inlist,separators=(",",":"))
plotdict = ({'histfile':histdir+'/'+tag+'.root',
        'outfile':histdir+'/'+tag+'_figure.png',
        'histtitle':kstitle,'xaxistitle':xaxistitle,'yaxistitle':yaxistitle})

### Run using local submission
if os.path.exists(filldict['histfile']):
    os.system('rm '+filldict['histfile'])
if os.path.exists(filldict['helpdir']):
    os.system('rm -r '+filldict['helpdir'])
if not os.path.exists(histdir):
    os.makedirs(histdir)
os.chdir(histdir)
with open("plot_submit_"+tag+".sh", "w") as localsh:
    localsh.write('#source $VO_CMS_SW_DIR/cmsset_default.sh\n')
    localsh.write('cd /user/llambrec/CMSSW_10_2_16_patch1/src\n')
    localsh.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    localsh.write('eval `scram runtime -sh`\n')
    localsh.write('cd '+scriptloc+'\n')
    # core command for filling:
    localsh.write('python ' +fillscript)
    # extra options:
    for opt in filldict:
        localsh.write(" "+"'"+opt+"="+filldict[opt]+"'")
    localsh.write('\n')
    # core command for plot.py
    localsh.write('python '+plotscript)
    # extra options
    for opt in plotdict:
        localsh.write(" "+"'"+opt+"="+plotdict[opt]+"'")
    localsh.write('\n')
os.system("qsub plot_submit_"+tag+".sh")
