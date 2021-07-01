#####################################################
# python script to prepare and submit skimming jobs #
#####################################################
import os
import sys
sys.path.append('../tools')
import jobsubmission as jobsub
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

# load input files
inputfiles = []
ninputfiles = 0
ndirs = 0
samples_info = st.readsamplelist(options.samplelist)
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
    # this would correspond to multiple processeings of the same dataset,
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
    for root,dirs,files in os.walk(thisinputdir):
	for fname in files:
	    if fname[-5:]=='.root':
                thisfiles.append(os.path.join(os.path.relpath(root,thisinputdir),fname))
    inputfiles.append({})
    inputfiles[i]['inputdir'] = thisinputdir
    inputfiles[i]['files'] = thisfiles
    inputfiles[i]['outputdir'] = os.path.join('skimmed',
				    sampleinfo['sample_name']+'_'+sampleinfo['version_name'])
    ninputfiles += len(thisfiles)
    ndirs += 1

print('found a total of {} input files in {} directories'.format(ninputfiles,ndirs))
print('Summary of skimming job:')
print('- samplelist: '+options.samplelist)
print('- output folder: '+options.outputdir)
print('- skimmer: '+options.skimmer)
print('- expected number of jobs: '+str(int(ninputfiles/options.nfilesperjob)))
print('Continue (y/n)?')
go = raw_input()
if not go=='y':
    sys.exit()

# loop over directories and submit jobs
workdir = os.getcwd()
for inputstruct in inputfiles:
    thisinputdir = inputstruct['inputdir']
    thisoutputdir = os.path.join(options.outputdir,inputstruct['outputdir'])
    # check if output path exists; if so, clean it
    if os.path.exists(thisoutputdir):
	os.system('rm -r '+thisoutputdir)
    os.makedirs(thisoutputdir)
    thisinputfiles = [os.path.join(thisinputdir,f) for f in inputstruct['files']]
    thisinputfiles = lt.split(thisinputfiles,options.nfilesperjob)
    counter = 0
    for partlist in thisinputfiles:
	scriptname = 'qjob_'+options.skimmer+'.sh'
	with open(scriptname,'w') as script: 
	    jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_20')
	    for input_file_path in partlist:
		output_file_path = os.path.join(thisoutputdir,input_file_path.split('/')[-1])
		command = './'+options.skimmer+' '+input_file_path+' '+output_file_path+' -1'
		script.write(command+'\n')
	    command = 'hadd '+os.path.join(thisoutputdir,'skimmed_'+str(counter)+'.root')
	    counter += 1
	    for input_file_path in partlist:
		output_file_path = os.path.join(thisoutputdir,input_file_path.split('/')[-1])
		command += ' '+output_file_path
	    script.write(command+'\n')
	    for input_file_path in partlist:
		output_file_path = os.path.join(thisoutputdir,input_file_path.split('/')[-1])
		script.write('rm '+output_file_path+'\n')
	jobsub.submitQsubJob(scriptname)
