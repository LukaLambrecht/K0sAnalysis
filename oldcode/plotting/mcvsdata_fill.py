############################################################################
# Script to read variable from ntuples or trees and make MC vs. data plots #
############################################################################
# This scripts fills and saves the histograms.
# To be used in conjunction with mcvsdata_plot that contains the plotting code.
import ROOT
from array import array
import sys

### Configure input parameters
histfile = '~/Kshort/histograms/lpt2017'
varname = '_lPt'
inputtype = 'tree' # choose from 'tree' (output from skimmer) or 'tuple' (output from ntuplizer)
#limit = '_nLambdas' # ignored if inputtype is 'tree'
treename = 'celeborn' # set name of the tree within the root files used as input
bintype = 'fixed' # choose from 'fixed' (fixed bin size) or 'variable'
xlow = 25.; xhigh = 125.; nbins = 50 # ignored if bintype is 'variable'
bins = array('f',[15.,20.,30.,50.,90.,170.]) # ignored if bintype is 'fixed'
normalization = 1
# normalization parameter:	0 = no normalization, weights, xsection and lumi set to 1.
#				1 = normalize using weights, xsection and lumi.
#				2 = same as before but apply normalization to data afterwards.
#				3 = same as before but normalize in specified range only.
lumi = 41500 # automatically set to 1 if normalization != 1
normrange = [0.,3.] # ignored if normalization != 3
outerflow = False # whether or not to include under- and overflow bins.

### Configure variable and histogram settings
binwidth = float((xhigh-xlow))/nbins
if(not bintype=='fixed' and not bintype=='variable'):
	print('ERROR: bintype not recognized!')
	exit()
if(normalization != 1):
	lumi = 1.

### Configure MC files
mcin = []
'''mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_JPsiToMuMu_MINIAODSIM_test/job0/skim_jpsi_met.root',
		'label':r'J/#Psi #rightarrow #mu#mu',
		'xsection':70900.,'luminosity':lumi})
mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_BToJPsi_MINIAODSIM_test/skim_jpsi_met_1t20.root',
		'label':r'B #rightarrow J/#Psi #rightarrow #mu#mu',
		'xsection':26000.,'luminosity':lumi})'''
mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL_1215/skim_ztomumu_all.root',
		'label':r'simlation',
		'xsection':6225.,'luminosity':lumi})

### Configure data files
datain = []
#datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_MINIAOD_test/skim_jpsi_1t50.root'})
datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_1215/skim_ztomumu_all.root'})
for era in ['B','C','D','F']:
	datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017'+era+'_DoubleMuon/skim_ztomumu_all.root'})

### Fill histograms
def addhistogram(histlist,inlist,index,datatype):
	if(not datatype=='mc' and not datatype=='data'):
		print('ERROR: datatype not recognized!')
		exit()
	isdata = (datatype=='data')
	f = ROOT.TFile.Open(inlist[index]['file'])
	tree = f.Get(treename)
	if isdata:
		label = ''
	else:
		label = inlist[index]['label']
	if(outerflow):
		if(bintype == 'fixed'):
			histlist.append(ROOT.TH1F(datatype+"histn"+str(index),label,
				nbins+2,xlow-binwidth,xhigh+binwidth))
		elif(bintype == 'variable'):
			newfirstedge = 2*bins[0]-bins[1]
			newlastedge = 2*bins[-1]-bins[-2]
			binlist = bins.tolist()
			binlist.insert(0,newfirstedge)
			binlist.append(newlastedge)
			newbins = array('f',binlist)
			histlist.append(ROOT.TH1F(datatype+"histn"+str(index),label,
				len(newbins)-1,newbins))
	else:
		if(bintype == 'fixed'):
			histlist.append(ROOT.TH1F(datatype+"histn"+str(index),label,
				nbins,xlow,xhigh))
		elif(bintype == 'variable'):
			histlist.append(ROOT.TH1F(datatype+"histn"+str(index),label,
				len(bins)-1,bins))
	hist = histlist[index]
	hist.Sumw2()
	sumweights=1; xsection=1; lumi=1
	if(not isdata and not normalization==0):	
		sumweights = f.Get("hCounter").GetSumOfWeights()
		xsection = inlist[index]['xsection']
		lumi = inlist[index]['luminosity']
	nwinrange = 0.
	# for testing purposes: use only a fracion of the data !!!
	for j in range(int(tree.GetEntries()/1.)):
		if(j%5000==0):
                        percent = j*100/tree.GetEntries()
                        sys.stdout.write("\r"+str(percent)+'%')
                        sys.stdout.flush()
		tree.GetEntry(j)
		weight = 1.
		if(not isdata and not normalization==0):
			weight = getattr(tree,'_weight')
		if(inputtype=='tuple'):
			print('Running on tuples has been switched off for safety!')
			print('This section is deprecated and should be adapted before running again!')
			exit()
			'''nV0 = getattr(tree,limit)
			if nV0==0:
				continue
			for k in range(nV0):
				# additional instance-based selections
				#if(abs(getattr(tree,'_KsInvMass')[k]-0.498)>0.01):
				#	continue
				if(abs(getattr(tree,'_LaInvMass')[k]-1.116)>0.01):
					continue
				# fill value
				varvalue = getattr(tree,varname)[k]	
				if(varvalue>xhigh): # manual overflow bin 
					varvalue = xhigh+binwidth/2. 
				if(varvalue<xlow): # manual underflow bin
					varvalue = xlow-binwidth/2.
				hist.Fill(varvalue,weight*lumi*xsection/sumweights)
				if(varvalue>normrange[0] and varvalue<normrange[1]):
					nmcwinrange += weight*lumi*xsection/sumweights'''
		elif(inputtype=='tree'):
			varvalue = getattr(tree,varname)
			if(bintype == 'fixed'):
				if(varvalue>xhigh): # manual overflow bin 
					varvalue = xhigh+binwidth/2. 
				if(varvalue<xlow): # manual underflow bin
					varvalue = xlow-binwidth/2.
				hist.Fill(varvalue,weight*lumi*xsection/sumweights)
			elif(bintype == 'variable'):
				if(varvalue>bins[-1] and outerflow): # manual overflow bin 
					varvalue = 0.5*(bins[-1]+newbins[-1]) 
				if(varvalue<bins[0] and outerflow): # manual underflow bin
					varvalue = 0.5*(bins[0]+newbins[0])
				hist.Fill(varvalue,weight*lumi*xsection/sumweights)
			if(varvalue>normrange[0] and varvalue<normrange[1]):
				nwinrange += 1.
	hist.SetDirectory(0)
	nw = hist.GetSumOfWeights()
	nentries = hist.GetEntries()
	f.Close()
	return (nentries,nw,nwinrange)

mchistlist = []
nmcw = 0.
nmcwinrange = 0.
nmcentries = 0
print('adding simulation files...')
for i in range(len(mcin)):
	print('file '+str(i+1)+' of '+str(len(mcin)))
	temp = addhistogram(mchistlist,mcin,i,'mc')
	nmcentries += temp[0]
	nmcw += temp[1]
	nmcwinrange += temp[2]
datahistlist = []
ndataw = 0.
ndatawinrange = 0.
ndataentries = 0
print('adding data files...')
for i in range(len(datain)):
	print('file '+str(i+1)+' of '+str(len(datain)))
	temp = addhistogram(datahistlist,datain,i,'data')
	ndataentries += temp[0]
	ndataw += temp[1]
	ndatawinrange += temp[2]

print('Raw MC entries: '+str(nmcentries))
print('Weighted MC entries: '+str(nmcw))
print('Raw data entries: '+str(ndataentries))
print('Data entries: '+str(ndataw))

# Normalize MC histograms to data if needed
if(normalization==2):
	print('post-processing simulation files...')
	scale = ndataw/nmcw
	for hist in mchistlist:
		hist.Scale(scale)
if(normalization==3):
	print('post-processing simulation files...')
	scale = ndatawinrange/nmcwinrange
	for hist in mchistlist:
		hist.Scale(scale)

# Write histograms to file
print('writing histograms to file...')
histfile = histfile+'.root'
f = ROOT.TFile.Open(histfile,"recreate")
for hist in mchistlist:
	hist.Write(hist.GetName())
for hist in datahistlist:
	hist.Write(hist.GetName())
normalization_st = ROOT.TVectorD(1); normalization_st[0] = normalization
normalization_st.Write("normalization")
if(normalization==3):
	normrange_st = ROOT.TVectorD(2)
	normrange_st[0] = normrange[0]; normrange_st[1] = normrange[1]
	normrange_st.Write("normrange")
if(normalization==1):
	lumi_st = ROOT.TVectorD(1)
	lumi_st[0] = lumi
	lumi_st.Write("lumi")
f.Close()
print('done')
