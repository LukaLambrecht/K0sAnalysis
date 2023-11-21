########################################################
# Python script to prepare and submit V0 building jobs #
########################################################
# note: the entire folder structure in inputdir will be copied to output dir.


# import external modules
import os
import sys
import argparse
# import framework modules
sys.path.append('../tools')
import condortools as ct
CMSSW = '/user/llambrec/CMSSW_12_4_6'
import listtools as lt
import sampletools as st


# read command line arguments
parser = argparse.ArgumentParser( description = 'Perform V0 candidate selection' )
parser.add_argument('-i', '--inputdir', required=True, type=os.path.abspath)
parser.add_argument('-o', '--outputdir', required=True, type=os.path.abspath)
parser.add_argument('-s', '--selection', default='legacy')
parser.add_argument('--runmode', default='condor', choices=['local', 'condor'])
args = parser.parse_args()

# check selection_name
allowed_selections = [
  'legacy',
]
if args.selection_name not in allowed_selections:
    raise Exception('ERROR: selection '+args.selection_name+' not recognized.')

# check if input directory exists
if not os.path.exists(args.inputdir):
    print('### ERROR ###: input directory '+args.inputdir+' does not seem to exist')
    sys.exit()

# gather input files
inputfiles = {}
ninputfiles = 0
# loop over input directory
for root,dirs,files in os.walk(args.inputdir):
    for dirname in dirs:
	dirname = os.path.join(root,dirname)
	flist = [f for f in os.listdir(dirname) if f[-5:]=='.root']
	if len(flist)>0: 
	    inputfiles[os.path.relpath(dirname,args.inputdir)] = sorted(flist)
	    ninputfiles += len(flist)

# print input files and ask for confirmation
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
    outdirname = os.path.join(args.outputdir, indirname)
    # clean outputdir if it exists, else create it
    if os.path.exists(outdirname):
	os.system('rm -r '+outdirname)
    os.makedirs(outdirname)
    # loop over input files
    for inputfile in inputfiles[indirname]:
	outputfile = os.path.join(outdirname,inputfile.replace('.root','_selected.root'))
	inputfile = os.path.join(args.inputdir,indirname,inputfile)
        # make command
        cmd = 'python3 v0builder.py'
	cmd += ' -i {}'.format(inputfile)
        cmd += ' -o {}'.format(outputfile)
        cmd += ' -s {}'.format(args.selection)
        cmds.append(cmd)

# submit jobs
if args.runmode=='local':
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
elif args.runmode=='condor':
    ct.submitCommandsAsCondorCluster('cjob_v0builder', cmds, cmssw_version=cmssw)
