#####################################################
# python script to prepare and submit skimming jobs #
#####################################################

# Runs on a sample list containing an arbitrary number of samples,
# see the samplelist directory for examples.
# Within the provided output directory, a subdirectory per sample will be created.
# Output files are named 'skimmed_<index>.root' and placed within the correct subdirectory.
# The number of output files is always one per job;
# if the number of input files per job is larger than one, the outputs are hadded into one.

import os
import sys
sys.path.append('../tools')
import condortools as ct
CMSSW = '/user/llambrec/CMSSW_10_2_20'
import listtools as lt
import sampletools as st
import optiontools as opt

# input parameters
options = []
options.append( opt.Option('samplelist', vtype='path') )
options.append( opt.Option('skimmer',default='skim_ztomumu') )
options.append( opt.Option('nfilesperjob',default=5, vtype='int') )
options.append( opt.Option('outputdir', vtype='path') )
options = opt.OptionCollection( options )
if len(sys.argv)==1:
    print('Use with following options:')
    print(options)
    sys.exit()
else:
    options.parse_options( sys.argv[1:] )
    print('Found following configuration:')
    print(options)

# check if samplelist exists
if not os.path.exists(options.samplelist):
    print('### ERROR ###: sample list '+options.samplelist+' does not seem to exist')
    sys.exit()

# check if executable exists
if not os.path.exists('./'+options.skimmer):
    print('### ERROR ###: skimmer '+options.skimmer+' does not seem to exist')
    sys.exit()

# find input files for all samples
inputfiles = []
ninputfiles = 0
ndirs = 0
samples_info = st.readsamplelist(options.samplelist)
print('Found {} samples in sample list.'.format(len(samples_info)))
for i,sampleinfo in enumerate(samples_info):
    line = sampleinfo['line']
    # check if line corresponds to a valid input directory
    if not os.path.exists(line):
	print('### WARNING ###: line '+line+' does not correspond to a valid input directory;')
	print('                 continue ignoring this line? (y/n)')
	go = raw_input()
	if go=='y': continue
	else: sys.exit()
    # check if this directory has multiple subdirectories;
    # this would correspond to multiple processings of the same dataset,
    # in which case choose most recent one.
    if len(os.listdir(line))==0:
	print('### WARNING ###: directory '+line+' is empty;')
	print('                 continue ignoring this directory? (y/n)')
	go = raw_input()
	if go=='y': continue
	else: sys.exit()
    if len(os.listdir(line))>1:
	print('### WARNING ###: directory '+line+' has multiple subdirectories;')
	print('                 choosing most recent processing of this dataset.')
	subdir = sorted(os.listdir(line))[-1]
    else: subdir = os.listdir(line)[0]
    thisinputdir = os.path.join(line,subdir)
    thisfiles = []
    # list all root files in this directory
    print('Finding all files in sample {}.'.format(thisinputdir))
    for root,dirs,files in os.walk(thisinputdir):
	for fname in files:
	    if fname[-5:]=='.root':
                thisfiles.append(os.path.join(os.path.relpath(root,thisinputdir),fname))
    print('Found {} files.'.format(len(thisfiles)))
    inputfiles.append({})
    inputfiles[i]['inputdir'] = thisinputdir
    inputfiles[i]['files'] = thisfiles
    inputfiles[i]['outputdir'] = os.path.join(options.outputdir,
				    sampleinfo['sample_name']+'_'+sampleinfo['version_name'])
    ninputfiles += len(thisfiles)
    ndirs += 1

print('Found a total of {} input files in {} directories'.format(ninputfiles,ndirs))
print('Summary of skimming jobs:')
for inputstruct in inputfiles:
    print('  {} -> {}'.format(inputstruct['inputdir'], inputstruct['outputdir']))
print('- Skimmer: '+options.skimmer)
print('- Estimated total number of jobs: '+str(int(ninputfiles/options.nfilesperjob)))
print('Continue (y/n)?')
go = raw_input()
if not go=='y':
    sys.exit()

# loop over samples
workdir = os.getcwd()
for inputstruct in inputfiles:
    thisinputdir = inputstruct['inputdir']
    thisoutputdir = inputstruct['outputdir']
    # check if output directory exists; if so, clean it
    if os.path.exists(thisoutputdir):
	os.system('rm -r '+thisoutputdir)
    # make output directory
    os.makedirs(thisoutputdir)
    # get input files and split in partitions
    thisinputfiles = [os.path.join(thisinputdir,f) for f in inputstruct['files']]
    thisinputfiles = lt.split(thisinputfiles,options.nfilesperjob)
    # loop over partitions
    for counter, partlist in enumerate(thisinputfiles):
        # make skim commands for this job
        cmds = []
        tempfiles = []
	for input_file_path in partlist:
	    temp_file_path = os.path.join(thisoutputdir, input_file_path.split('/')[-1])
	    cmd = './'+options.skimmer+' '+input_file_path+' '+temp_file_path+' -1'
            cmds.append(cmd)
            tempfiles.append(temp_file_path)
        # make hadd command for this job
	cmd = 'hadd '+os.path.join(thisoutputdir, 'skimmed_'+str(counter)+'.root')
	for temp_file_path in tempfiles: cmd += ' '+temp_file_path
        cmds.append(cmd)
        # make commands to remove temporary files for this job
	for temp_file_path in tempfiles:
	    cmd = 'rm '+temp_file_path
            cmds.append(cmd)
        # submit job
	ct.submitCommandsAsCondorJob('cjob_skim', cmds, cmssw_version=CMSSW)
