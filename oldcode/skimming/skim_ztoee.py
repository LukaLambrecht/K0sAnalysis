################################################################################
# Reading a noskim root file, perform DY-skimming and make flat trees for V0's #
################################################################################
import sys
import ROOT
import math
import numpy as np
from array import array

# some constants
ksmass = 0.49761
lambdamass = 1.1157

# for testing:
finloc = '/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleEG/crab_Run2017E-31Mar2018-v1_data_Run2017E_DoubleEG/191213_095526/0000/noskim_1.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/noskim.root'
foutloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/skimmed.root'
isdata = True
containsbuiltin = True
neventsmax = 1e4

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
laurelin = ROOT.TTree("laurelin","") # data structure for Kshort variables
telperion = ROOT.TTree("telperion","") # data structure for Lambda variables
celeborn = ROOT.TTree("celeborn","") # data structure for electron variables
nimloth = ROOT.TTree("nimloth","") # data structure for event variables
fillvalue = array('f',[0.])
# store some basic electron and event variables to check if skim works all right:
elvarlist = ([{'var':'_lPt','size':'nL'},
{'var':'_lE','size':'nL'},
{'var':'_lEta','size':'nL'},
{'var':'_ptRatio','size':'nLight'},
{'var':'_ptRel','size':'nLight'},
{'var':'_relIso','size':'nLight'},
{'var':'_selectedTrackMult','size':'nLight'}])
neweventvarlist = (['_event_njets','_event_mll'])
eventvarlist = (['_nKshorts','_nLambdas','_nVertex','_beamSpotX','_beamSpotY','_beamSpotZ',
		'_primaryVertexX','_primaryVertexY','_primaryVertexZ'])
if containsbuiltin:
	eventvarlist.append('_bi_nKshorts'); eventvarlist.append('_bi_nLambdas')
# here are the actual variables of interest for this investigation:
kshortvarlist = (['_KsInvMass','_KsX','_KsY','_KsZ','_KsRPV','_KsRBS','_KsCosPPV','_KsCosPBS',
		'_KsSumPt','_KsPt','_KsPtPos','_KsPtNeg','_KsD0Pos','_KsD0Neg','_KsDzPos','_KsDzNeg',
		'_KsEta','_KsEtaPos','_KsEtaNeg','_KsIsoPos','_KsIsoNeg'])
kshortnewvarlist = (['_passMassCut'])
lambdavarlist = (['_LaInvMass','_LaX','_LaY','_LaZ','_LaRPV','_LaRBS','_LaCosPPV','_LaCosPBS',
		'_LaSumPt','_LaPt','_LaPtPos','_LaPtNeg','_LaD0Pos','_LaD0Neg','_LaDzPos','_LaDzNeg',
		'_LaEta','_LaEtaPos','_LaEtaNeg','_LaIsoPos','_LaIsoNeg'])
lambdanewvarlist = (['_passMassCut'])
for listel in elvarlist:
	varname = listel['var']
	temp = celeborn.Branch(varname,fillvalue,str(varname+'/F'))
for varname in eventvarlist+neweventvarlist:
	temp = nimloth.Branch(varname,fillvalue,str(varname+'/F'))
for varname in kshortvarlist+kshortnewvarlist:
	temp = laurelin.Branch(varname,fillvalue,str(varname+'/F'))
for varname in lambdavarlist+lambdanewvarlist:
	temp = telperion.Branch(varname,fillvalue,str(varname+'/F'))
if not isdata: # store event weight per entry in each tree
	temp = celeborn.Branch('_weight',fillvalue,'_weight/F')
	temp = laurelin.Branch('_weight',fillvalue,'_weight/F')
	temp = telperion.Branch('_weight',fillvalue,'_weight/F')
	temp = nimloth.Branch('_weight',fillvalue,'_weight/F')
# make additional trees for built-in info
if containsbuiltin:
	laurelin2 = ROOT.TTree("laurelin2","") # built-in Kshorts
	telperion2 = ROOT.TTree("telperion2","") # built-in Lambdas
	kshort2varlist = (['_bi_KsInvMass','_bi_KsR','_bi_KsSumPt'])
	lambda2varlist = (['_bi_LaInvMass','_bi_LaR','_bi_LaSumPt'])
	for varname in kshort2varlist:
		temp = laurelin2.Branch(varname,fillvalue,str(varname+'/F'))
	for varname in lambda2varlist:
		temp = telperion2.Branch(varname,fillvalue,str(varname+'/F'))
	if not isdata:
		temp = laurelin2.Branch('_weight',fillvalue,'_weight/F')
		temp = telperion2.Branch('_weight',fillvalue,'_weight/F')
# Initialize b-tagging cut values
if('Run2016' in finloc or 'Summer16' in finloc):
	loosebtag = 0.2217
elif('Run2017' in finloc or 'Fall17' in finloc):
	loosebtag = 0.1522
elif('Run2018' in finloc or 'Autumn18' in finloc):
	loosebtag = 0.1241
else:
	print('WARNING: b-tagging value could not be initialized; check file name.')
	print('         using default value for 2017 samples...')
	loosebtag = 0.1522
print('loose b-tag value: '+str(loosebtag))

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

	# skim condition 1: at least two electrons
	nEle = int(getattr(tree,'_nEle'))
	if(nEle < 2):
		continue
	
	# find the indices of those electrons in list of leptons
	elinds = []
	for k in range(nL):
		if(int(getattr(tree,'_lFlavor')[k]) == 0):
			elinds.append(k)
	elinds = np.array(elinds)
	# find the indices of those elecrons in list of light leptons
	counter = 0
	elindslight = []
	for k in range(nL):
		if(int(getattr(tree,'_lFlavor')[counter])==1):
			counter += 1
		elif(int(getattr(tree,'_lFlavor')[counter])==0):
			elindslight.append(counter)
			counter += 1
	elindslight = np.array(elindslight)
	# sort according to transverse momentum
	negativemomentumarray = []
	for k in elinds:
		negativemomentumarray.append(-getattr(tree,'_lPt')[k])
	sorted_inds = np.argsort(np.array(negativemomentumarray))
	elinds = elinds[sorted_inds]
	elindslight = elindslight[sorted_inds]	

	# skim condition 2: electron id
	k = 0
	while k<len(elinds):
		if(int(getattr(tree,'_lElectronPassEmu')[elindslight[k]])==0):
			elinds = np.delete(elinds,k)
			elindslight = np.delete(elindslight,k)
		else:
			k += 1
	if(len(elinds)!=2):
		continue

	# skim condition 3: explicit momentum cuts
	if(getattr(tree,'_lPt')[elinds[0]]<30. or getattr(tree,'_lPt')[elinds[1]]<25.):
		continue

	# skim condition 4: pass trigger
	# to be used in conjunction with skim_ztomumu so remove possible overlap!
	if(int(getattr(tree,'_passTrigger_mm'))==1):
		continue
	if(int(getattr(tree,'_passTrigger_ee'))==0):
		continue

	# skim condition 5: electron invariant mass
	pt1 = getattr(tree,'_lPt')[elinds[0]]
	eta1 = getattr(tree,'_lEta')[elinds[0]]
	phi1 = getattr(tree,'_lPhi')[elinds[0]]
	E1 = getattr(tree,'_lE')[elinds[0]]
	pt2 = getattr(tree,'_lPt')[elinds[1]]
	eta2 = getattr(tree,'_lEta')[elinds[1]]
	phi2 = getattr(tree,'_lPhi')[elinds[1]]
	E2 = getattr(tree,'_lE')[elinds[1]]
	vec1 = ROOT.Math.PtEtaPhiEVector(pt1,eta1,phi1,E1)
	vec2 = ROOT.Math.PtEtaPhiEVector(pt2,eta2,phi2,E2)
	invmass = (vec1+vec2).M()
	if(abs(invmass - 91.19) > 10.):
		continue

	# skim condition 6: b-jet veto 
	njets = 0
	nloosebtags = 0
	for j in range(int(getattr(tree,'_nJets'))):
		count = True
		jeta = getattr(tree,'_jetEta')[j]
		jphi = getattr(tree,'_jetPhi')[j]
		for l in range(nL):
			leta = getattr(tree,'_lEta')[l]
			lphi = getattr(tree,'_lPhi')[l]
			deltaR = math.sqrt((leta-jeta)**2+(lphi-jphi)**2)
			if(deltaR < 0.4):
				count = False
		if count:
			njets += 1
		if(getattr(tree,'_jetDeepCsv_b')[j]+getattr(tree,'_jetDeepCsv_bb')[j] > loosebtag):
			nloosebtags += 1
	if(nloosebtags >= 1):
		continue

	dbgcounter += 1
	### write event variables
	fillvalue[0] = invmass
	nimloth.GetBranch('_event_mll').Fill()	
	fillvalue[0] = njets
	nimloth.GetBranch('_event_njets').Fill()
	for l in range(len(eventvarlist)):
		varname = eventvarlist[l]
		fillvalue[0] = getattr(tree,varname)
		nimloth.GetBranch(varname).Fill()
	### loop over individual electrons to write properties
	for k in range(len(elinds)):
		for l in range(len(elvarlist)):
			varname = elvarlist[l]['var']
			if(elvarlist[l]['size']=='nL'):
				varvalue = getattr(tree,varname)[elinds[k]]
			elif(elvarlist[l]['size']=='nLight'):
				varvalue = getattr(tree,varname)[elindslight[k]]
			fillvalue[0] = varvalue
			celeborn.GetBranch(varname).Fill()
	### loop over individual Kshorts to write properties
	nKshorts = int(getattr(tree,'_nKshorts'))
	for k in range(nKshorts):
		for l in range(len(kshortvarlist)):
			varname = kshortvarlist[l]
			varvalue = getattr(tree,varname)[k]
			fillvalue[0] = varvalue
			laurelin.GetBranch(varname).Fill()
		fillvalue[0] = (abs(getattr(tree,'_KsInvMass')[k]-ksmass)<0.01)
		laurelin.GetBranch('_passMassCut').Fill()
	### loop over individual Lambdas to write properties
	nLambdas = int(getattr(tree,'_nLambdas'))
	for k in range(nLambdas):
		for l in range(len(lambdavarlist)):
			varname = lambdavarlist[l]
			varvalue = getattr(tree,varname)[k]
			fillvalue[0] = varvalue
			telperion.GetBranch(varname).Fill()
		fillvalue[0] = (abs(getattr(tree,'_LaInvMass')[k]-lambdamass)<0.005)
		telperion.GetBranch('_passMassCut').Fill()
	### loop over individual built-in Kshorts to write properties
	if containsbuiltin:
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
				telperion2.GetBranch(varname).Fill()
	### write event weight to each tree
	if not isdata:
		event_weight = getattr(tree,'_weight')
		fillvalue[0] = event_weight
		nimloth.GetBranch('_weight').Fill()
		for k in range(len(elinds)):
			celeborn.GetBranch('_weight').Fill()
		for k in range(nKshorts):
			laurelin.GetBranch('_weight').Fill()
		for k in range(nLambdas):
			telperion.GetBranch('_weight').Fill()
		if containsbuiltin:
			for k in range(bi_nKshorts):
				laurelin2.GetBranch('_weight').Fill()
			for k in range(bi_nLambdas):
				telperion2.GetBranch('_weight').Fill()
	
print(dbgcounter)
nimloth.SetEntries()
celeborn.SetEntries()
laurelin.SetEntries()
telperion.SetEntries()
if containsbuiltin:
	laurelin2.SetEntries()
	telperion2.SetEntries()
fout.Write()
if not isdata:
	sumweights.Write()
fout.Close()
print('finished writing trees.')
