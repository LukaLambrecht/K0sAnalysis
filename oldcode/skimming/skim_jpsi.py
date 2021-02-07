################################################################################
# Reading a noskim root file, perform DY-skimming and make flat trees for V0's #
################################################################################
import sys
import ROOT
import math
import numpy as np
from array import array

# some constants
jpsimass = 3.097

# for testing:
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_MINIAOD_test/job0/job0.root'
finloc = '/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2018C-17Sep2018-v1_data_Run2018C_DoubleMuon/191213_100528/0000/noskim_1.root'
#foutloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/skimmed.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/noskim3.root'
foutloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/skimmed.root'
isdata = True
containsbuiltin = False # not yet implemented for JPsi, keep to false!
neventsmax = 1e3

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
jpsivarlist = (['_JPInvMass','_JPRPos','_JPSumPt','_JPPt','_JPEta','_JPEtaPos','_JPEtaNeg',
		'_JPNHitsPos','_JPNHitsNeg','_JPIsoPos','_JPIsoNeg'])
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
def hasJPmass(tree,ind1,ind2):
	pt1 = getattr(tree,'_lPt')[ind1]
	eta1 = getattr(tree,'_lEta')[ind1]
	phi1 = getattr(tree,'_lPhi')[ind1]
	E1 = getattr(tree,'_lE')[ind1]
	pt2 = getattr(tree,'_lPt')[ind2]
	eta2 = getattr(tree,'_lEta')[ind2]
	phi2 = getattr(tree,'_lPhi')[ind2]
	E2 = getattr(tree,'_lE')[ind2]
	vec1 = ROOT.Math.PtEtaPhiEVector(pt1,eta1,phi1,E1)
	vec2 = ROOT.Math.PtEtaPhiEVector(pt2,eta2,phi2,E2)
	invmass = (vec1+vec2).M()
	if(abs(invmass - jpsimass) < 0.3):
		return True
	return False

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
	nL = int(getattr(tree,'_nL'))
	nLight = int(getattr(tree,'_nLight'))

	# find number of muons
	nMu = int(getattr(tree,'_nMu'))
	#if(nMu < 2):
	#	continue
	
	# find the indices of those muons in list of leptons
	muoninds = []
	for k in range(nL):
		if(int(getattr(tree,'_lFlavor')[k]) == 1):
			muoninds.append(k)
	muoninds = np.array(muoninds)
	# find the indices of those muons in list of light leptons
	counter = 0
	muonindslight = []
	for k in range(nL):
		if(int(getattr(tree,'_lFlavor')[counter])==0):
			counter += 1
		elif(int(getattr(tree,'_lFlavor')[counter])==1):
			muonindslight.append(counter)
			counter += 1
	muonindslight = np.array(muonindslight)
	# sort according to transverse momentum
	negativemomentumarray = []
	for k in muoninds:
		negativemomentumarray.append(-getattr(tree,'_lPt')[k])
	sorted_inds = np.argsort(np.array(negativemomentumarray))
	muoninds = muoninds[sorted_inds]
	muonindslight = muonindslight[sorted_inds]	

	# optional: skim on muon id
	k = 0
	while k<len(muoninds):
		if(int(getattr(tree,'_lPOGMedium')[muoninds[k]])==0):
			muoninds = np.delete(muoninds,k)
			muonindslight = np.delete(muonindslight,k)
		else:
			k += 1
	#if(len(muoninds)!=2):
	#	continue

	# skim condition: pass trigger
	if(int(getattr(tree,'_passTrigger_relaxedmm'))==0):
		continue

	# skim condition: at least one reconstructed JPsi
	if(getattr(tree,'_nJPsis')<1):
		continue

	# skim condition: all reconstructed JPsi particles must be in momentum range
	keepevent = True
	for j in range(getattr(tree,'_nJPsis')):
		if(getattr(tree,'_JPPt')[j]<8 or getattr(tree,'_JPDCA')[j]>0.01):
			keepevent = False
	if not keepevent: 
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
	for k in range(len(muoninds)):
		for l in range(len(muvarlist)):
			varname = muvarlist[l]['var']
			if(muvarlist[l]['size']=='nL'):
				varvalue = getattr(tree,varname)[muoninds[k]]
			elif(muvarlist[l]['size']=='nLight'):
				varvalue = getattr(tree,varname)[muonindslight[k]]
			fillvalue[0] = varvalue
			celeborn.GetBranch(varname).Fill()
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
		for k in range(len(muoninds)):
			celeborn.GetBranch('_weight').Fill()
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
