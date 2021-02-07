###############################################################################
# Simple script to count number of events in a folder containing root ntuples #
###############################################################################
import ROOT
import glob
import sys
import os

if(len(sys.argv)==3):
	inputfolder = sys.argv[1]
	fstruct = sys.argv[2]
else:
	print('WARNING: using hard-coded input folder!')
	inputfolder = ''
	fstruct = ''

if(fstruct=='custom'):
	struct = '/job*/job*.root'
elif(fstruct=='crab'):
	struct = '/*/noskim_*.root'
else:
	print('ERROR: value for fstruct parameter not recognized.')
	exit()

### find number of entries in tuplizer output files
inputfiles = []
for subfolder in glob.glob(inputfolder+struct):
	inputfiles.append(subfolder)

totalentries = 0
for i,inputfile in enumerate(inputfiles):
	fin = ROOT.TFile.Open(inputfile)
	tree = fin.Get("blackJackAndHookers/blackJackAndHookersTree")
	try:
		entries = tree.GetEntries()
		totalentries += entries
		print('file '+str(i+1)+' of '+str(len(inputfiles))+': '+str(entries)+' entries')
	except:
		print('WARNING: the folowing file raised an error and was not taken into account:')
		print(inputfile)
print('Total number of entries in this folder: '+str(totalentries))

### find tuplizer output files whose skimming job failed to submit
'''totalentries = 0
for inputfile in inputfiles:
	jobfolder = inputfile[:inputfile.rfind('/')+1]
	hasoutput = False
	if len(glob.glob(jobfolder+'skim_ztomumu_local.sh.o*'))>0:
		hasoutput = True
	if not hasoutput:
		try:
			fin = ROOT.TFile.Open(inputfile)
			tree = fin.Get("blackJackAndHookers/blackJackAndHookersTree")
			totalentries += tree.GetEntries()
		except:
			print()
print('Total number of entries whose skim job failed: '+str(totalentries))'''
