########################################################
# Python script to prepare and submit V0 building jobs #
########################################################
# note: the entire folder structure in inputdir will be copied to output dir.
# note: can be used with both v0builder.py and v0builder2.py, see command line args.

import os
import sys
sys.path.append('../tools')
import condortools as ct
import listtools as lt
import sampletools as st
import optiontools as opt


# parse input arguments
options = []
options.append( opt.Option('inputdir', vtype='path') )
options.append( opt.Option('outputdir', vtype='path') )
options.append( opt.Option('selection_name', default='legacy') )
options.append( opt.Option('v0builder', default='v0builder2.py') )
options.append( opt.Option('runmode', default='condor') )
options = opt.OptionCollection( options )
if len(sys.argv)==1:
    print('Use with following options:')
    print(options)
    sys.exit()
else:
    options.parse_options( sys.argv[1:] )
    print('Found following configuration:')
    print(options)

# check v0builder
python = 'python'
v0builder = 'v0builder.py'
cmssw = '/user/llambrec/CMSSW_10_2_20'
if options.v0builder=='v0builder.py': pass
elif options.v0builder=='v0builder2.py':
    python = 'python3'
    v0builder = 'v0builder2.py'
    cmssw = '/user/llambrec/CMSSW_12_4_6'
else: raise Exception('ERROR: v0builder {} not recognized.'.format(options.v0builder))

# check selection_name
allowed_selections = [
  'legacy',
  'legacy_loosenhits',
  'legacy_nonhits',
  'legacy_highpt',
  'ivf'
]
if options.selection_name not in allowed_selections:
    print('### ERROR ###: selection '+options.selection_name+' not recognized.')
    sys.exit()

# check if input directory exists
if not os.path.exists(options.inputdir):
    print('### ERROR ###: input directory '+options.inputdir+' does not seem to exist')
    sys.exit()

inputfiles = {}
ninputfiles = 0
# loop over input files
for root,dirs,files in os.walk(options.inputdir):
    for dirname in dirs:
	dirname = os.path.join(root,dirname)
	#if 'MiniAOD' in dirname: continue # temp to do only sim or only data
	#if(not '2016' in dirname or 'Summer' in dirname): continue # temp
	flist = [f for f in os.listdir(dirname) if f[-5:]=='.root']
	if len(flist)>0: 
	    inputfiles[os.path.relpath(dirname,options.inputdir)] = sorted(flist)
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

workdir = os.getcwd()
cmds = []
# loop over input directories
for indirname in inputfiles.keys():
    outdirname = os.path.join(options.outputdir, indirname)
    # clean outputdir if it exists, else create it
    if os.path.exists(outdirname):
	os.system('rm -r '+outdirname)
    os.makedirs(outdirname)
    # loop over input files
    for inputfile in inputfiles[indirname]:
	outputfile = os.path.join(outdirname,inputfile.replace('.root','_selected.root'))
	inputfile = os.path.join(options.inputdir,indirname,inputfile)
        # make command
        cmd = python + ' ' + v0builder
	cmd += ' '+inputfile+' '+outputfile+' -1 '+options.selection_name
        cmds.append(cmd)

# submit jobs
if options.runmode=='local':
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
elif options.runmode=='condor':
    ct.submitCommandsAsCondorCluster('cjob_v0builder', cmds, cmssw_version=cmssw)
