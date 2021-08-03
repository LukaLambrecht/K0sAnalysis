###########################################
# python script to merge skimmed ntuples #
##########################################

import sys 
import os
sys.path.append('../tools')
import mergetools as mt

# this script will hadd all root files in a folder
# command line arguments (in sequence):
# OPTION 1: merge .root files in input directory and put result in output file
# - input directory
# - output file name
# OPTION 2: loop over subdirs in input directory and replace files by merged copy
# - (top-level) input directory

if __name__=='__main__':

    if len(sys.argv)==1:
	info = 'Use with following options (in sequence):\n'
	info += 'OPTION 1: merge .root files in input directory and put result in output file\n'
	info += ' - input directory\n'
	info += ' - output file name\n'
	info += 'OPTION 2: loop over subdirs in input directory and replace files by merged copy\n'
	info += ' - (top-level) input directory'
	print(info)

    if len(sys.argv) == 3:
	input_directory = os.path.abspath( sys.argv[1] )
	output_file_name = os.path.abspath( sys.argv[2] )
	output_directory = output_file_name.rsplit('/',1)[0]
	if not os.path.exists(output_directory):
	    os.makedirs(output_directory)
	print('searching for skimmed samples in '+input_directory)
	inputlist = ([os.path.join(input_directory,f) for f in os.listdir(input_directory)
			if f[-5:]=='.root'])
	print('found '+str(len(inputlist))+' input files')
	mt.mergefiles(inputlist,outputfile)

    if len(sys.argv)==2:
	input_directory = os.path.abspath( sys.argv[1] )
	indirs = []
        for root,dirs,files in os.walk(input_directory):
            for thisdir in dirs:
		thisdir = os.path.join(root,thisdir)
                if len([f for f in os.listdir(thisdir) if f[-5:]=='.root'])>1:
                    indirs.append(thisdir)
	sorted(indirs)
	print('found following subdirs containing root files that will be merged:')
	for indir in indirs:
	    print('  -  '+indir)
	print('coninue? (y/n)')
	go = raw_input()
	if not go=='y':
	    sys.exit()
	for indir in indirs:
	    print('--------------------')
	    print(indir)
	    mt.mergeallfiles(indir,os.path.join(indir,'merged.root'),removeinput=False)
