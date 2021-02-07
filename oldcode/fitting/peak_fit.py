##################################################################
# Python script to read a noskim.root tree or flat skimmed tree, #
# extract a Kshort or Lambda vertex value, plot and fit it       #
##################################################################
import ROOT
import numpy as np
import fit_tools as ft
import glob
from array import array

### initialization of intput files
#finloc = '/pnfs/iihe/cms/store/user/llambrec/heavyNeutrino/DoubleMuon/crab_Run2017E-31Mar2018-v1_data_Run2017E_DoubleMuon/191213_095349'
finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_1215/skim_ztomumu_all.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_JPsiToMuMu_MINIAODSIM_test/skim_jpsi_met_all.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_MINIAOD_test/skim_jpsi_1t50.root'
inputtype = 'tree' # choose from 'tree' or 'ntuple'
if inputtype=='ntuple':
	treename = 'blackJackAndHookers/blackJackAndHookersTree'
elif inputtype=='tree':
	treename = 'telperion' # choose from laurelin or telperion  (or nimloth or celeborn)
### initialization of histogram settings
nmax = 1e8
xlow = 1.085
xhigh = 1.145
binwidth = 0.001
fitrange = [xlow,xhigh]
xcenter = (xhigh+xlow)/2.
xwidth = (xhigh-xlow)/4.
varname = '_LaInvMass'
limit = '_nLambdas' # ignored if inputtype is 'tree'
xaxtitle = 'invariant mass (GeV)'
title = r'reconstructed #Lambda^{0} invariant mass'
label = 'Run2017E data'
### possibility to make a histogram per bin in another variable
divvarname = '_LaInvMass'
divbins = array('f',[0.,100.])
show_divinfo = False
### global program settings
do_fill = True
tempfilename = 'temp_la.root'
do_fit = True
polydegree = 1 # degree of background polynomial fit

if do_fill:
	nfilled = 0
	nhists = len(divbins)-1
	histlist = []
	for j in range(nhists):
		histlist.append(ROOT.TH1F('hist'+str(j),'',int((xhigh-xlow)/binwidth),xlow,xhigh))
		histlist[j].SetDirectory(0)
	if(finloc[-5:] == '.root'): # in case of single file.
		infilelist = [finloc]
	else: # in case of folder. Attention: depends on naming and structuring conventions.
		infilelist = []		
		for infile in glob.glob(finloc+'/0000/noskim*.root'):
			infilelist.append(infile)
	for j,infile in enumerate(infilelist):
		fin = ROOT.TFile.Open(infile)
		tree = fin.Get(treename)
		nevents = tree.GetEntries()
		nprocess = int(min(nmax,nevents))
		print('file '+str(j+1)+' of '+str(len(infilelist)))
		print(str(nprocess)+' events out of '+str(nevents)+' will be processed.')
		if inputtype=='tree': nfilled += nprocess
		for i in range(nprocess):
			if(i>1 and (i+1)%10000==0):
				print('number of processed events: '+str(i+1)) 
			tree.GetEntry(i)
			if(inputtype=='ntuple'):
				nV0 = getattr(tree,limit)
				if nV0==0:
					continue
				nfilled += nV0
				for k in range(nV0):
					varvalue = getattr(tree,varname)[k]
					divvalue = getattr(tree,divvarname)[k]
					if(divvalue>divbins[0] and divvalue<divbins[-1]):
						divindex = np.digitize(divvalue,divbins)-1
						histlist[divindex].Fill(varvalue)
			elif(inputtype=='tree'):
				varvalue = getattr(tree,varname)
				divvalue = getattr(tree,divvarname)
				if(divvalue>divbins[0] and divvalue<divbins[-1]):
					divindex = np.digitize(divvalue,divbins)-1
					histlist[divindex].Fill(varvalue)
	fout = ROOT.TFile(tempfilename,"recreate")
	for hist in histlist:
		hist.Write()
	divbins_w = ROOT.TVectorD(len(divbins))
	for j in range(len(divbins)):
		divbins_w[j] = divbins[j]
	divbins_w.Write("divbins_w")
	divvarname_w = ROOT.TNamed("divvarname_w",divvarname)
	divvarname_w.Write()
	nfilled_w = ROOT.TVectorD(1); nfilled_w[0] = nfilled
	nfilled_w.Write()
	fout.Close()
	print(str(nfilled)+' instances were written to a histogram file.')

if do_fit:
	if not do_fill:
		fin = ROOT.TFile.Open(tempfilename)
		histlist = []
		i = 0
		while True:
			if(fin.Get("hist"+str(i)) == None):
				break
			histlist.append(fin.Get("hist"+str(i)))
			i += 1
		divbins = fin.Get("divbins_w")
		divvarname = str(fin.Get("divvarname_w").GetTitle())
	for j,hist in enumerate(histlist):
		# step 1: remove middle band and fit sidebands to obtain background
		histclone = hist.Clone()
		binlow = histclone.FindBin(xcenter-xwidth)
		binhigh = histclone.FindBin(xcenter+xwidth)
		for i in range(binlow,binhigh):
			histclone.SetBinContent(i,0)
		guess = [0.]*(polydegree+1)
		backfit,paramdict = ft.poly_fit(histclone,fitrange,guess,"Q0")
		average = backfit.Eval(xcenter)
		# step 2: do simultaneous fit with previous fit parameters as initial guesses
		guess = [xcenter,average*10,0.005,average*10,0.01]
		for i in range(polydegree+1):
			guess.append(paramdict["a"+str(i)])
		totfit,paramdict = ft.poly_plus_doublegauss_fit(hist,fitrange,guess)
		print('Fitted parameters:')
		for el in paramdict:
			print('    '+el+': '+str(paramdict[el]))
		# step 3: plot
		#extrainfo = str(divbins[j])+' < something  < '+str(divbins[j+1])
		extrainfo = ' << <<HACK_LA'
		ft.plot_fit(hist,label,totfit,paramdict,backfit,xaxtitle,
			'number of reconstructed vertices',
			title,'figure'+str(j)+'.png',extrainfo)
