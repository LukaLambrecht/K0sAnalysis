#####################################################
# Python script to prepare and submit skimming jobs #
#####################################################
import os
import sys
sys.path.append('../tools')
import jobsubmission as jobsub
import listtools as lt
import sampletools as st

def reducedfoldername(foldername):
    # return a simplified folder name for the output to allow easier access in later stages
    # the foldername is assumed to be in crab format with <samplename>_<versionname>
    foldername = foldername.rstrip('/')
    basename = ''
    if '/' in foldername:
	[basename,foldername] = foldername.rsplit('/',1)
    isdata = False if 'MiniAOD' in foldername else True
    if isdata:
	foldername = foldername.replace('-','_').split('_')
	reducedname = foldername[0]+'_'+foldername[2]
    else:
	reducedname = foldername.replace('-','_').split('_')[0]
	if 'MiniAOD2016' in foldername:
	    reducedname += '_2016'
	elif 'MiniAOD2017' in foldername:
	    reducedname += '_2017'
	elif 'MiniAOD18' in foldername:
	    reducedname += '_2018'
    return os.path.join(basename,reducedname)

# parse input arguments
if len(sys.argv)!=4:
    print('### ERROR ###: wrong number of command line arguments')
    print('		  normal usage: python v0builder_submit <input_directory> <output_directory>')
    print('                             <selection_name>')
    sys.exit()
inputdir = os.path.abspath(sys.argv[1])
outputdir = os.path.abspath(sys.argv[2])
# the entire folder structure in inputdir will be copied to output dir
# (apart from renaming of sample folders)
selection_name = sys.argv[3]

# check selection_name
if selection_name not in ['legacy','legacy_loosenhits','legacy_nonhits']:
    print('### ERROR ###: selection '+selection_name+' not recognized')
    sys.exit()

# check if input directory exists
if not os.path.exists(inputdir):
    print('### ERROR ###: input directory '+inputdir+' does not seem to exist')
    sys.exit()

inputfiles = {}
ninputfiles = 0
# loop over input files
for root,dirs,files in os.walk(inputdir):
    for dirname in dirs:
	dirname = os.path.join(root,dirname)
	#if 'MiniAOD' in dirname: continue # temp to do only sim or only data
	flist = [f for f in os.listdir(dirname) if f[-5:]=='.root']
	if len(flist)>0: 
	    inputfiles[os.path.relpath(dirname,inputdir)] = flist
	    ninputfiles += len(flist)

print('found following input files:')
for dirname in inputfiles.keys():
    print('    '+dirname)
    for f in inputfiles[dirname]:
	print('        '+f)
print('total number of files: {}'.format(ninputfiles))
print('Continue (y/n)?')
go = raw_input()
if not go=='y':
    sys.exit()

# loop over input files and submit jobs
workdir = os.getcwd()
for indirname in inputfiles.keys():
    outdirname = os.path.join(outputdir,reducedfoldername(indirname))
    if os.path.exists(outdirname):
	os.system('rm -r '+outdirname)
    os.makedirs(outdirname)
    for inputfile in inputfiles[indirname]:
	outputfile = os.path.join(outdirname,inputfile.replace('.root','_selected.root'))
	inputfile = os.path.join(inputdir,indirname,inputfile)
	scriptname = 'v0builder.sh'
	with open(scriptname,'w') as script: 
	    jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_16_patch1')
	    command = 'python v0builder.py '+inputfile+' '+outputfile+' -1 '+selection_name
	    script.write(command+'\n')
	jobsub.submitQsubJob(scriptname)
