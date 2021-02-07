################################################################################
# Reading a noskim root file, perform MET skimming and make flat tree for JPsi #
################################################################################
import sys
import ROOT
import math
import numpy as np
from array import array

# some constants
jpsimass = 3.097

# for testing:
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_MinimumBias_MINIAOD_test/noskim.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_BToJPsi_MINIAODSIM_test/job0/job0.root'
#finloc = '/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/ZeroBias/crab_Run2017B-31Mar2018-v1_data_Run2017full_ZeroBias/191207_181129/0000/noskim_1.root'
#foutloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/skimmed.root'
finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/noskim2.root'
foutloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/skimmed2.root'
isdata = True
containsbuiltin = False # not yet implemented for JPsi, keep to false!
neventsmax = 1e5

### Initialize files to read and write
if(len(sys.argv)==5):
	finloc = sys.argv[1]
	foutloc = sys.argv[2]
	isdata = (sys.argv[3]=='True')
	containsbuiltin = (sys.argv[4]=='True')
	neventsmax = 1e10
else:
	print('WARNING: using one of the hard-coded test files as input...')

fin = ROOT.TFile.Open(finloc)
tree = fin.Get("blackJackAndHookers/blackJackAndHookersTree")
if not isdata:
	sumweights = fin.Get("blackJackAndHookers/hCounter")
nevents = tree.GetEntries()
nprocess = int(min(nevents,neventsmax))
print(str(nprocess)+' of '+str(nevents)+' available events will be processed...')
fout = ROOT.TFile(foutloc,"recreate")
laurelin = ROOT.TTree("laurelin","") # data structure for JPsi variables
celeborn = ROOT.TTree("celeborn","") # data structure for muon variables
nimloth = ROOT.TTree("nimloth","") # data structure for event variables
fillvalue = array('f',[0.])
# store some basic muon and event variables to check if skim works all right:
muvarlist = ([{'var':'_lPt','size':'nL'},
{'var':'_lE','size':'nL'},
{'var':'_lEta','size':'nL'},
{'var':'_ptRatio','size':'nLight'},
{'var':'_ptRel','size':'nLight'},
{'var':'_relIso','size':'nLight'},
{'var':'_selectedTrackMult','size':'nLight'}])
eventvarlist = (['_nJPsis'])
if containsbuiltin:
	#eventvarlist.append('_bi_nKshorts'); eventvarlist.append('_bi_nLambdas')
	print('not yet implemented for JPsi!')
	exit()
# here are the actual variables of interest for this investigation:
jpsivarlist = (['_JPInvMass','_JPRPos','_JPSumPt','_JPPt'])
jpsinewvarlist = (['_passMassCut','_ppdl'])
for listel in muvarlist:
	varname = listel['var']
	temp = celeborn.Branch(varname,fillvalue,str(varname+'/F'))
for varname in eventvarlist:
	temp = nimloth.Branch(varname,fillvalue,str(varname+'/F'))
for varname in jpsivarlist+jpsinewvarlist:
	temp = laurelin.Branch(varname,fillvalue,str(varname+'/F'))
if not isdata: # store event weight per entry in each tree
	temp = celeborn.Branch('_weight',fillvalue,'_weight/F')
	temp = laurelin.Branch('_weight',fillvalue,'_weight/F')
	temp = nimloth.Branch('_weight',fillvalue,'_weight/F')
# make additional trees for built-in info
'''if containsbuiltin:
	laurelin2 = ROOT.TTree("laurelin2","") # built-in Kshorts
	telperion2 = ROOT.TTree("telperion2","") # built-in Lambdas
	kshort2varlist = (['_bi_KsInvMass','_bi_KsRPos','_bi_KsSumPt'])
	lambda2varlist = (['_bi_LaInvMass','_bi_LaRPos','_bi_LaSumPt'])
	for varname in kshort2varlist:
		temp = laurelin2.Branch(varname,fillvalue,str(varname+'/F'))
	for varname in lambda2varlist:
		temp = telperion2.Branch(varname,fillvalue,str(varname+'/F'))
	if not isdata:
		temp = laurelin2.Branch('_weight',fillvalue,'_weight/F')
		temp = telperion2.Branch('_weight',fillvalue,'_weight/F')'''

### Some help functions
def getppdl(tree,jpind):
	xpos = getattr(tree,'_JPXPos')[jpind]
	ypos = getattr(tree,'_JPYPos')[jpind]
	zpos = getattr(tree,'_JPZPos')[jpind]
	px = getattr(tree,'_JPPx')[jpind]
	py = getattr(tree,'_JPPy')[jpind]
	pz = getattr(tree,'_JPPz')[jpind]
	mass = getattr(tree,'_JPInvMass')[jpind]
	pt = getattr(tree,'_JPPt')[jpind]
	ppdl = (xpos*px+ypos*py)*mass/(pt*pt)
	return ppdl

### Loop over events and write properties of selected leptons and V0's 
### from events that pass skimming
dbgcounter = 0
for j in range(nprocess):
	if(j>1 and (j+1)%10000==0):
		print('number of processed events: '+str(j+1)) 
		fout.Write()
	tree.GetEntry(j)
	
	# skim condition 1: pass trigger
	if(int(getattr(tree,'_passMETFilters'))==0):
		continue

	# skim condition 2: exactly one reconstructed JPsi particle with pt in range
	if(getattr(tree,'_nJPsis')!=1):
		continue
	if(getattr(tree,'_JPPt')[0]<10):
		continue

	dbgcounter += 1 
	### write event variables	
	fillvalue[0] = getattr(tree,'_nJPsis')
	nimloth.GetBranch('_nJPsis').Fill()
	'''if containsbuiltin:
		fillvalue[0] = getattr(tree,'_bi_nKshorts')
		nimloth.GetBranch('_bi_nKshorts').Fill()
		fillvalue[0] = getattr(tree,'_bi_nLambdas')
		nimloth.GetBranch('_bi_nLambdas').Fill()'''
	### loop over individual muons to write properties
	'''for k in range(len(muoninds)):
		for l in range(len(muvarlist)):
			varname = muvarlist[l]['var']
			if(muvarlist[l]['size']=='nL'):
				varvalue = getattr(tree,varname)[muoninds[k]]
			elif(muvarlist[l]['size']=='nLight'):
				varvalue = getattr(tree,varname)[muonindslight[k]]
			fillvalue[0] = varvalue
			celeborn.GetBranch(varname).Fill()'''
	### loop over individual JPsis to write properties
	nJPsis = int(getattr(tree,'_nJPsis'))
	for k in range(nJPsis):
		for l in range(len(jpsivarlist)):
			varname = jpsivarlist[l]
			varvalue = getattr(tree,varname)[k]
			fillvalue[0] = varvalue
			laurelin.GetBranch(varname).Fill()
		fillvalue[0] = (abs(getattr(tree,'_JPInvMass')[k]-jpsimass)<0.03)
		laurelin.GetBranch('_passMassCut').Fill()
		fillvalue[0] = getppdl(tree,k)
		laurelin.GetBranch('_ppdl').Fill()
	### loop over individual built-in Kshorts to write properties
	'''if containsbuiltin:
		bi_nKshorts = int(getattr(tree,'_bi_nKshorts'))
		for k in range(bi_nKshorts):
			for l in range(len(kshort2varlist)):
				varname = kshort2varlist[l]
				varvalue = getattr(tree,varname)[k]
				fillvalue[0] = varvalue
				laurelin2.GetBranch(varname).Fill()
	### loop over individual built-in Lambdas to write properties
	if containsbuiltin:
		bi_nLambdas = int(getattr(tree,'_bi_nLambdas'))
		for k in range(bi_nLambdas):
			for l in range(len(lambda2varlist)):
				varname = lambda2varlist[l]
				varvalue = getattr(tree,varname)[k]
				fillvalue[0] = varvalue
				telperion2.GetBranch(varname).Fill()'''
	### write event weight to each tree
	if not isdata:
		event_weight = getattr(tree,'_weight')
		fillvalue[0] = event_weight
		nimloth.GetBranch('_weight').Fill()
		#for k in range(len(muoninds)):
		#	celeborn.GetBranch('_weight').Fill()
		for k in range(nJPsis):
			laurelin.GetBranch('_weight').Fill()
		'''if containsbuiltin:
			for k in range(bi_nKshorts):
				laurelin2.GetBranch('_weight').Fill()
			for k in range(bi_nLambdas):
				telperion2.GetBranch('_weight').Fill()'''

print(dbgcounter)	
nimloth.SetEntries()
celeborn.SetEntries()
laurelin.SetEntries()
'''if containsbuiltin:
	laurelin2.SetEntries()
	telperion2.SetEntries()'''
fout.Write()
if not isdata:
	sumweights.Write()
fout.Close()
print('finished writing trees.')
