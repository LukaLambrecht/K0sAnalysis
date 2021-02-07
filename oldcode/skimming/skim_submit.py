#######################################################################
### Prepares and submits jobs that process multilep.py output files ###
### and skims them with a skimmer python file			    ###
#######################################################################
# Read carefully before running as it may remove existing files!
import os
import glob
import math

### Choose skimmer
skimmer = 'skim_ztomumu'

### Choose correct folder structure (either 'crab' or 'custom')
fstruct = 'crab'
# in case of 'crab', input folders should be defined until just before the /000x/noskim_*.root level.
# in case of 'custom', input folders should be defined until just before the /jobx/jobx.root level.

### Choose number of files per job (not applicable to 'custom' folder structure; always 1)
nfilesperjob = 50

### Set input folders
MCdirs = []
'''
MCdirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/crab_MiniAOD2016v3_ext2-v1_sim_RunIISummer16_DYJetsToLL/191213_102817',
	    'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIISummer16_DYJetsToLL'})
'''
#MCdirs.append('/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/crab_MiniAOD2017v2_ext1-v1_sim_RunIIFall17_DYJetsToLL/191213_095706')
#MCdirs.append('/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/crab_MiniAOD2018_ext2-v1_sim_RunIIAutumn18_DYJetsToLL/191213_101232')
#MCdirs = []
datadirs = []

datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016B-17Jul2018_ver2-v1_data_Run2016B_DoubleMuon/191219_164629',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016B_DoubleMuon'})
datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016C-17Jul2018-v1_data_Run2016C_DoubleMuon/191219_164752',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016C_DoubleMuon'})
datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016D-17Jul2018-v1_data_Run2016D_DoubleMuon/191219_164816',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016D_DoubleMuon'})
datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016E-17Jul2018-v1_data_Run2016E_DoubleMuon/191219_164910',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016E_DoubleMuon'})
datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016F-17Jul2018-v1_data_Run2016F_DoubleMuon/191219_164954',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016F_DoubleMuon'})
datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016G-17Jul2018-v1_data_Run2016G_DoubleMuon/191219_165016',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016G_DoubleMuon'})
datadirs.append({'inputfolder':'/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2016H-17Jul2018-v1_data_Run2016H_DoubleMuon/191219_165306',
		'outputfolder':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016H_DoubleMuon'})

containsbuiltin = True

### Load input files
if(fstruct=='custom'):
	print('ERROR: fstruct=custom is no longer supported')
	sys.exit()
elif(fstruct=='crab'):
	appendix = '/*/noskim_*.root'
else:
	print('ERROR: value of parameter "fstruct" not recognized.')
	sys.exit()

nmc = 0
ndata = 0
for f in MCdirs:
	folder = f['inputfolder']
	f['inputfiles'] = []
	for files in glob.glob(folder+appendix):
		f['inputfiles'].append(files)
		nmc += 1
for f in datadirs:
	folder = f['inputfolder']
	f['inputfiles'] = []
	for files in glob.glob(folder+appendix):
		f['inputfiles'].append(files)
		ndata += 1

nfiles = nmc+ndata
print('Total number of .root files found in input directories: '+str(nfiles))
print('Submit '+str(nfiles)+' files for processing (y/n)?')
go = raw_input()
if(go != 'y'):
	exit()

### Loop over files and submit jobs
workdir = os.getcwd()

# define common function for data and simulation:
'''def loop_and_submit_custom(inputfiles,isdata):
    for k,inputfile in enumerate(inputfiles):
        inputdir = inputfile[:inputfile.rfind('/')]
        os.chdir(inputdir)
        # remove files from previous runs if present.
        anyshfile = [f for f in os.listdir(inputdir) if skimmer+'_local' in f]
        anyrootfile = [f for f in os.listdir(inputdir) if (skimmer in f and '.root' in f)]
        for f in anyshfile:
            os.system("rm "+f)
        for f in anyrootfile:
            os.system("rm "+f)
        with open(skimmer+"_local.sh", "w") as localsh:
            localsh.write('#source $VO_CMS_SW_DIR/cmsset_default.sh\n')
            localsh.write('cd /user/llambrec/CMSSW_10_2_16_patch1/src\n')
            localsh.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
            localsh.write('eval `scram runtime -sh`\n')
            localsh.write('cd '+workdir+'\n')
            outf = str(inputdir)+'/'+skimmer+'.root'
            # core command:
            localsh.write('python '+skimmer+'.py '+inputfile+' '+outf)
            # extra options:
            localsh.write(' '+str(isdata)+' '+str(containsbuiltin)+'\n')
            os.system("qsub "+skimmer+"_local.sh")
        print('job nr '+str(k+1)+' of '+str(len(inputfiles))+' submitted')'''

def loop_and_submit_crab(inputfiles,nfilesperjob,isdata):
	# loop over input and output folders
	for io in inputfiles:
	    # get input and output folder and files
	    inputfolder = io['inputfolder']
	    outputfolder = io['outputfolder']
	    files = io['inputfiles']
	    if not os.path.exists(outputfolder):
		os.system('mkdir '+outputfolder)
	    os.chdir(outputfolder)
	    # remove files from previous runs if present.
	    anyshfile = [f for f in os.listdir(outputfolder) if skimmer+'_local' in f]
	    anyrootfile = [f for f in os.listdir(outputfolder) if (skimmer in f and '.root' in f)]
	    for f in anyshfile:
		os.system("rm "+f)
	    for f in anyrootfile:
		os.system("rm "+f)
	    # loop over files for this folder
	    listel=0
	    counter=0
	    njobs = int(math.ceil(len(files)/float(nfilesperjob)))
	    while listel<len(files):
		jobinputfiles = files[listel:min(listel+nfilesperjob,len(files))]
		with open(skimmer+"_local_"+str(counter)+".sh", "w") as localsh:
			localsh.write('#source $VO_CMS_SW_DIR/cmsset_default.sh\n')
			localsh.write('cd /user/llambrec/CMSSW_10_2_16_patch1/src\n')
			localsh.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
			localsh.write('eval `scram runtime -sh`\n')
			localsh.write('cd '+outputfolder+'\n')
			skimmerloc = '/storage_mnt/storage/user/llambrec/Kshort/python/skimming/'+skimmer+'.py'
			outf = outputfolder+'/'+skimmer+str(counter)+'.root'
			# core commands:
			for i,f in enumerate(jobinputfiles):
				localsh.write('python '+skimmerloc+' '+f)
				localsh.write(' temp_'+str(counter)+'_'+str(i)+'.root')
				localsh.write(' '+str(isdata)+' '+str(containsbuiltin)+'\n')
			localsh.write('hadd '+outf+' '+'temp_'+str(counter)+'_*.root\n')
			localsh.write('rm temp_'+str(counter)+'_*.root\n')
		os.system("qsub "+skimmer+"_local_"+str(counter)+".sh")
		print('job nr '+str(counter+1)+' of '+str(njobs)+' submitted')
		listel = listel+nfilesperjob
		counter += 1		

if(fstruct=='custom'):
	#print('WARNING: a temporary hack has been implemented. Check the source code. Continue?')
	#go = raw_input()
	#if(go != 'y'):
        #	exit()
	#loop_and_submit_crab(MCinputfiles,outfolder,nfilesperjob,False)
	#loop_and_submit_crab(datainputfiles,outfolder,nfilesperjob,True)
	print('Submitting MC jobs:')
	loop_and_submit_custom(MCinputfiles,False)
	print('Submitting data jobs:')
	loop_and_submit_custom(datainputfiles,True)

if(fstruct=='crab'):
	print('Submitting MC jobs:')
	loop_and_submit_crab(MCdirs,nfilesperjob,False)
	print('Submitting data jobs:')
	loop_and_submit_crab(datadirs,nfilesperjob,True)

### Finish by printing job status  
print('job status:')
os.system("qstat -u llambrec")
