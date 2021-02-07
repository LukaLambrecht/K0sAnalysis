###########################################################################
# Script to read RPos variable from flat trees and make MC vs. data plots #
###########################################################################
# This script creates a histogram with the number of Kshort decays
# as a function of the radial distance of their vertex.
# The number of Kshorts in each bin can be estimated using a background fit to the sidebands
# of the invariant mass distribution.
import ROOT
import os
import numpy as np
from array import array
import sys
import json
sys.path.append(os.path.abspath('../pureweighting'))
from addpuscale import getpuscale
sys.path.append(os.path.abspath('../fitting'))
import fit_tools as ft

### Configure input parameters (hard-coded)
histfile = '~/Kshort/histograms/test.root' # file to store RPos histograms in
helpdir = '~/Kshort/histograms/help/' # directory to store other useful objects in
bck_mode = 2
# (bck_mode parameter:	0 = count all instances of varname)
#			1 = count all instances of varname passing an additional condition)
#			2 = subtract background based on sidebands in invariant mass histogram, possibly with extra condition)
varname = '_KsRPV'
treename = 'laurelin'
#extracut = 'bool(getattr(tree,"_passMassCut"))' # ignored if bck_mode != 1 or 2
#extracut = 'bool(abs(getattr(tree,"_JPInvMass")-3.0969)<0.1)'
#extracut = 'bool(getattr(tree,"_LaPt")>15.)'
extracut = 'bool(2>1)'
# settings for RPos histgram
bintype = 'variable' # choose from 'fixed' (fixed bin size) or 'variable'
xlow = 0.; xhigh = 20.; nbins = 50 # ignored if bintype is 'variable'
bins = array('f',[0.,0.5,1.5,4.,20.]) # ignored if bintype is 'fixed'
normalization = 5
# (normalization parameter:	0 = no normalization, weights, xsection and lumi set to 1.)
# (				1 = normalize using weights, xsection and lumi.)
# (				2 = same as before but apply normalization to data afterwards.)
# (				3 = same as before but normalize in specified range only.)
# (				4 = normalize number of events to data, not number of instances)
# (             5 = normalize first histogram to unit surface area and remaining ones to first one within range)
lumi = 35900. # automatically set to 1 if normalization != 1
normrange = [0.,0.5] # ignored if normalization != 3 or 5
eventtreename = 'nimloth' # ignored if normalization != 4
# settings for InvMass histograms (ignored if bck_mode != 2)
massvarname = '_KsInvMass'
mxlow = 0.44
mxhigh = 0.56
mnbins = 30

### Configure MC files
mcin = []
#mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_BToJPsi_MINIAODSIM/skim_jpsi_1t12.root',
#		'label':r'B #rightarrow J/#Psi',
#		'xsection':3.88e5,'luminosity':lumi})
#mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_JPsiToMuMu_MINIAODSIM/skim_jpsi_1t20.root',
#		'label':r'prompt J/#Psi',
#		'xsection':8.79e5*0.0397,'luminosity':lumi})
mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIISummer16_DYJetsToLL_new/skim_ztomumu_all.root',
		'label':r'2016 sim','xsection':6529.,'luminosity':lumi}) # xsection 6529 (?)
#mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL/skim_ztomumu_all.root','label':r'2017 sim','xsection':6529.,'luminosity':lumi}) # xsection 6529 (?)
#mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIAutumn18_DYJetsToLL/skim_ztomumu_all.root','label':r'2018 sim','xsection':6529.,'luminosity':lumi}) # xsection 6529 (?)

### Configure data files
datain = []
#datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_withloosetriggers/skim_jpsi_1t200.root','label':'data'})
datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon/skim_ztomumu_all.root','label':'data'})

### Configure input parameters (command line for submission script
cmdargs = sys.argv[1:]
if len(cmdargs)>0:
 	coreargs = {'histfile':False,'helpdir':False,'bck_mode':False,'varname':False,
			'treename':False,'bintype':False,'normalization':False,
			'mcin':False,'datain':False}
	i = 0
	while(i<len(cmdargs)):
		argname,argval = cmdargs[i].split('=')
		valid = True
		if argname=='histfile': histfile = argval; coreargs['histfile']=True
		elif argname=='helpdir': helpdir = argval; coreargs['helpdir']=True
		elif argname=='bck_mode': bck_mode = int(argval); coreargs['bck_mode']=True
		elif argname=='varname': varname = argval; coreargs['varname']=True
		elif argname=='treename': treename = argval; coreargs['treename']=True
		elif argname=='bintype': bintype = argval; coreargs['bintype']=True
		elif argname=='normalization': 
			normalization = int(argval); 
			coreargs['normalization']=True
		elif argname=='mcin': mcin = json.loads(argval); coreargs['mcin']=True
		elif argname=='datain': datain = json.loads(argval); coreargs['datain']=True
		else: valid=False
		if valid:
			cmdargs.pop(i)
		else: i+=1
	if False in coreargs.values():
		print('ERROR: the following core arguments were not defined:')
		for key in coreargs.keys():
			if(coreargs[key]==False): print(key)
		exit()
	checkbtf = {'xlow':False,'xhigh':False,'nbins':False} 
	checkbtv = {'bins':False}
	checknorm1 = {'lumi':False}; checknorm3={'normrange':False}; checknorm4 = {'eventtree':False}
	checkbck1 = {'extracut':False}
	checkbck2 = {'massvar':False,'mxlow':False,'mxhigh':False,'mnbins':False,'extracut':False}
	for arg in cmdargs:
		argname,argval = arg.split('=')
		if(bintype=='fixed'):
			if argname=='xlow': xlow=float(argval); checkbtf['xlow']=True
			if argname=='xhigh': xhigh=float(argval); checkbtf['xhigh']=True
			if argname=='nbins': nbins=int(argval); checkbtf['nbins']=True
		elif(bintype=='variable'):
			if argname=='bins': bins=array('f',json.loads(argval)); checkbtv['bins']=True
		if(normalization==1):
			if argname=='lumi': lumi=float(argval); checknorm1['lumi']=True
		elif(normalization==3 or normalization==5):
			if argname=='normrange': 
				normrange=json.loads(argval) 
				checknorm3['normrange']=True
		elif(normalization==4):
			if argname=='eventtree': 
				eventtreename = argval
				checknorm4['eventtree']=True
		if(bck_mode==1):
			if argname=='extracut': 
				extracut = arg.split('=',1)[1] 
				checkbck1['extracut']=True
				# (note: extra option 1 should allow to use '=' in extracut)
		elif(bck_mode==2):
			if argname=='massvar': massvarname = argval; checkbck2['massvar']=True
			if argname=='mxlow': mxlow = float(argval); checkbck2['mxlow']=True
			if argname=='mxhigh': mxhigh = float(argval); checkbck2['mxhigh']=True
			if argname=='mnbins': mnbins = int(argval); checkbck2['mnbins']=True
			if argname=='extracut': extracut = argval; checkbck2['extracut']=True
	if(bintype=='fixed' and False in checkbtf.values()):
		print('ERROR: requested bintype "fixed" but missing arguments.')
		exit()
	if(bintype=='variable' and False in checkbtv.values()):
		print('ERROR: requested bintype "variable" but missing arguments')
		exit()
	if(normalization==1 and False in checknorm1.values()):
		print('ERROR: requested normalization to xsection and lumi but missing arguments.')
		exit()
	if((normalization==3 or normalization==5) and False in checknorm3.values()):
		print('ERROR: requested normalization in range but missing arguments.')
		exit()
	if(normalization==4 and False in checknorm4.values()):
		print('ERROR: requested normalization to events but missing arguments.')
		exit()
	if(bck_mode==1 and False in checkbck1.values()):
		print('ERROR: requested additional background cut but missing arguments.')
		exit()
	if(bck_mode==2 and False in checkbck2.values()):
		print('ERROR: requested background subtraction but missing arguments.')
		exit()

### Setting lumi to 1 unless normalization requests otherwise
if(normalization != 1):
	print('WARNING: lumi set to 1. because of normalization settings.')
	lumi = 1.
	for d in mcin:
		d['luminosity'] = 1.

### Initializations based on input parameters defined above
mbinwidth = float(mxhigh-mxlow)/mnbins # ignored if bck_mode != 2
fitrange = [mxlow,mxhigh] # ignored if bck_mode != 2
mxcenter = (mxhigh+mxlow)/2. # ignored if bck_mode != 2
mxwidth = (mxhigh-mxlow)/4. # ignored if bck_mode != 2
dataeventweights = 0. # ignored if normalization != 4
mceventweights = 0. # ignored if normalization != 4
datawinrange = 0. # ignored if normalization != 3
mcwinrange = 0. # ignored if normalization != 3
if(not bintype=='fixed' and not bintype=='variable'):
	print('ERROR: bintype not recognized!')
	exit()
if(not os.path.exists(helpdir)):
	os.system("mkdir -p "+helpdir)
if(bintype=='fixed'):
	bins = array('f',np.linspace(xlow,xhigh,num=nbins+1,endpoint=True))
	binwidth = (xhigh-xlow)/nbins
else:
	nbins = len(bins)-1
	xlow = bins[0]
	xhigh = bins[-1]
	binwidth = min(np.array(bins[1:]-np.array(bins[:-1])))
# initialize histograms for RPos
# (1D lists: dimension 1: files)
mchistlist = []
datahistlist = []
for i in range(len(mcin)):
	mchistlist.append(ROOT.TH1F("mchistn"+str(i),mcin[i]['label'],nbins,bins))
	mchistlist[i].SetDirectory(0)
for i in range(len(datain)):
	datahistlist.append(ROOT.TH1F("datahistn"+str(i),datain[i]['label'],nbins,bins))
	datahistlist[i].SetDirectory(0)
# initialize histograms for invariant mass (per bin in RPos)
# (2D lists: dimension 1: different files, dim 2: different rpos bins)
mcmasshistlist = []
datamasshistlist = []
if bck_mode==2:
	for i in range(len(datain)):
		datamasshistlist.append([])
		for j in range(nbins):
			hist = ROOT.TH1F("datamasshist_"+str(i)+'_'+str(j),"",
					mnbins,mxlow,mxhigh)
			hist.Sumw2()
			hist.SetDirectory(0)
			datamasshistlist[i].append(hist)
	for i in range(len(mcin)):
		mcmasshistlist.append([])
		for j in range(nbins):
			hist = ROOT.TH1F("mcmasshist_"+str(i)+'_'+str(j),"",
					mnbins,mxlow,mxhigh)
			hist.Sumw2()
			hist.SetDirectory(0)
			mcmasshistlist[i].append(hist)

### loop over instances
def addinputfile(masshistlist,varhist,inlist,index,isdata):
	# notes: - first argument is ignored if bck_mode!=2, pass any variable
	#        - second argument is not ignored if bck_mode==2 but only for bin-finding, not filling.
	f = ROOT.TFile.Open(inlist[index]['file'])
	eventsumweights = 0.
	sumweightsinrange = 0.
	sumweights=1; xsection=1; lumi=1
	if(not isdata and not normalization==0):	
		sumweights = f.Get("hCounter").GetSumOfWeights()
		puscale = f.Get("PUScale")
		xsection = inlist[index]['xsection']
		lumi = inlist[index]['luminosity']
	# if normalization==4: loop over events and sum weights
	if(normalization==4):
		eventtree = f.Get(eventtreename)
		if isdata:
			eventsumweights = eventtree.GetEntries()
		else:
			sumweights = f.Get("hCounter").GetSumOfWeights()
			for j in range(int(eventtree.GetEntries())):
				eventtree.GetEntry(j)
				weight = getattr(eventtree,'_weight')
				weight *= getpuscale(getattr(eventtree,'_nTrueInt'),puscale)
				eventsumweights += weight/sumweights*xsection*lumi
	# loop over V0 instances 
	tree = f.Get(treename)
	# (for testing purposes: use only a fracion of the data !!!)
	for j in range(int(tree.GetEntries()/1.)):
		if(j%5000==0):
			percent = j*100/tree.GetEntries()
			sys.stdout.write("\r"+str(percent)+'%')
			sys.stdout.flush()
		tree.GetEntry(j)
		weight = 1.
		if(not isdata and not normalization==0):
			weight = getattr(tree,'_weight')
			weight *= getpuscale(getattr(tree,'_nTrueInt'),puscale)
		varvalue = getattr(tree,varname)
		if(varvalue>xlow and varvalue<xhigh):
			if(bck_mode==0):
				varhist.Fill(varvalue,weight*lumi*xsection/sumweights)
				if(normalization==3 
				   and varvalue>normrange[0]
				   and varvalue<normrange[1]):
					sumweightsinrange += weight*lumi*xsection/sumweights
			elif(bck_mode==1):
				if(eval(extracut)):
					varhist.Fill(varvalue,weight*lumi*xsection/sumweights)
					if(normalization==3 
					   and varvalue>normrange[0]
					   and varvalue<normrange[1]):
						sumweightsinrange += weight*lumi*xsection/sumweights
			elif(bck_mode==2):
				if(eval(extracut)):
					histindex = varhist.FindBin(varvalue)-1
					massvarvalue = getattr(tree,massvarname)
					masshistlist[index][histindex].Fill(massvarvalue,weight*lumi
										*xsection/sumweights)	
	f.Close()
	sys.stdout.write("\r"+'100%'+"\n")
	sys.stdout.flush()
	return eventsumweights,sumweightsinrange

print('adding simulation files...')
for i in range(len(mcin)):
	print('file '+str(i+1)+' of '+str(len(mcin)))
	temp = addinputfile(mcmasshistlist,mchistlist[i],mcin,i,False)
	mceventweights += temp[0]
	mcwinrange += temp[1]
print('adding data files...')
for i in range(len(datain)):
	print('file '+str(i+1)+' of '+str(len(datain)))
	temp = addinputfile(datamasshistlist,datahistlist[i],datain,i,True)
	dataeventweights += temp[0]
	datawinrange += temp[1]

### Help functions to perform background fit and subtract it (only needed if bck_mode == 2)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
def subtract_background(hist,label,extrainfo):
	# only first argument is important for fit, rest is only plotting
	# note that the parameters mxcenter, mxwidth, mxlow, mxhigh, mnbins and fitrange are implied globally!
	histclone = hist.Clone()
	binlow = histclone.FindBin(mxcenter-mxwidth)
	binhigh = histclone.FindBin(mxcenter+mxwidth)
	# take into account only sidebands, not peak
	for i in range(binlow+1,binhigh+1):
		histclone.SetBinContent(i,0)
		histclone.SetBinError(i,0)
	guess = [0.,0.]
	backfit,paramdict = ft.poly_fit(histclone,fitrange,guess,"Q0")
	ft.plot_fit(hist,label,None,paramdict,backfit,'invariant mass (GeV)',
			'number of reconstructed vertices','',
			helpdir+hist.GetName()+'.png',extrainfo)
	# METHOD 1: subtract background from peak and count remaining instances
	histclone2 = hist.Clone()
	histclone2.Add(backfit,-1)
	npeak = 0.
        npeak_error2 = 0.
        for i in range(binlow+1,binhigh+1):
                npeak += histclone2.GetBinContent(i)
                npeak_error2 += np.power(histclone2.GetBinError(i),2)
	# METHOD 2: do global fit and determine integral of peak with error
	avgbck = paramdict['a0']+0.5*mxcenter*paramdict['a1']
	mxbinwidth = (mxhigh-mxlow)/mnbins
	guess = [mxcenter,avgbck*10,(mxhigh-mxlow)/45.,avgbck*10,(mxhigh-mxlow)/15.]
	guess += [paramdict['a0'],paramdict['a1']]
	globfit,paramdict = ft.poly_plus_doublegauss_fit(hist,fitrange,guess)
	intpeak = np.sqrt(2*np.pi)*(paramdict['A_{1}']*paramdict['#sigma_{1}']
					+ paramdict['A_{2}']*paramdict['#sigma_{2}'])
	intpeak /= mxbinwidth
	intpeak_error = globfit.IntegralError(fitrange[0],fitrange[1])
	intpeak_error /= mxbinwidth
	ft.plot_fit(hist,label,globfit,paramdict,backfit,'invariant mass (GeV)',
                       'number of reconstructed vertices','',
                       helpdir+hist.GetName()+'_2.png',extrainfo)
	return (npeak,np.sqrt(npeak_error2),intpeak,intpeak_error)

### Fill RPos histograms if not done so before 
if(bck_mode == 2):
	print('performing fits to background in all bins...')
	if '_Ks' in massvarname: massinfo = 'HACK_KS'
	elif '_La' in massvarname: massinfo = 'HACK_LA'
	elif '_JP' in massvarname: massinfo = 'HACK_JP'
	else: massinfo = ''
	for i in range(nbins):
		extrainfo = '{0:.2f} < '.format(bins[i])+varname+' < {0:.2f}'.format(bins[i+1])
		extrainfo += '<< <<'+massinfo
		for j in range(len(mcin)):
			res = subtract_background(mcmasshistlist[j][i],'simulation',extrainfo)
			ncandidates = res[0]
			error = res[1] # don't use peak fit results for now as they are unstable
			mchistlist[j].SetBinContent(i+1,ncandidates)
			mchistlist[j].SetBinError(i+1,error)
		# (bin 0 is underflow bin!)
		for j in range(len(datain)):
			res = subtract_background(datamasshistlist[j][i],'data',extrainfo)
			ncandidates = res[0]
			error = res[1]
			datahistlist[j].SetBinContent(i+1,ncandidates)
			datahistlist[j].SetBinError(i+1,error)
		# (bin 0 is underflow bin!)

### Normalize MC histograms to data if needed
if(normalization==2 or normalization==3):
	mchist = mchistlist[0].Clone()
	for i in range(1,len(mchistlist)):
		mchist.Add(mchistlist[i])
	datahist = datahistlist[0].Clone()
	for i in range(1,len(datahistlist)):
		datahist.Add(datahistlist[i])
if(normalization==2):
	print('post-processing simulation files...')
	ndataw = datahist.GetSumOfWeights()
	nmcw = mchist.GetSumOfWeights()
	scale = ndataw/nmcw
	for hist in mchistlist:
		hist.Scale(scale)
if(normalization==3):
	print('post-processing simulation files...')
	# need to recalculate datawinrange and mcwinrange if bck_mode==2, 
	# as they cannot be calculated in event loop
	if(bck_mode==2):
		datawinrange = datahist.Integral(datahist.FindBin(normrange[0]+0.1*binwidth),
							datahist.FindBin(normrange[1]-0.1*binwidth))
		mcwinrange = mchist.Integral(mchist.FindBin(normrange[0]+0.1*binwidth),
							mchist.FindBin(normrange[1]-0.1*binwidth))
	scale = datawinrange/mcwinrange
	for hist in mchistlist:
		hist.Scale(scale)
if(normalization==4):
	print('post-processing simulation files...')
	print(dataeventweights)
	print(mceventweights)
	scale = dataeventweights/mceventweights
	for hist in mchistlist:
		hist.Scale(scale)
if(normalization==5):
    print('post-processing simulation files...')
    histlist = mchistlist+datahistlist
    hist0 = histlist[0]
    integral = hist0.Integral("width")
    hist0.Scale(1./integral)
    num = hist0.Integral(hist0.FindBin(normrange[0]+0.001*binwidth),
                         hist0.FindBin(normrange[1]-0.001*binwidth))
    for hist in histlist[1:]:
        winrange = hist.Integral(hist.FindBin(normrange[0]+0.001*binwidth),
                                 hist.FindBin(normrange[1]-0.001*binwidth))
        hist.Scale(num/winrange)

### Write histograms to file
print('writing histograms to file...')
f = ROOT.TFile.Open(histfile,"recreate")
for hist in mchistlist+datahistlist:
	hist.Write(hist.GetName())
normalization_st = ROOT.TVectorD(1); normalization_st[0] = normalization
normalization_st.Write("normalization")
if(normalization==3 or normalization==5):
	normrange_st = ROOT.TVectorD(2)
	normrange_st[0] = normrange[0]; normrange_st[1] = normrange[1]
	normrange_st.Write("normrange")
if(normalization==1):
	lumi_st = ROOT.TVectorD(1)
	lumi_st[0] = lumi
	lumi_st.Write("lumi")
f.Close()
print('done')
