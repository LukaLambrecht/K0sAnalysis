##########################################################
# make invariant pass plots and fits of kshort or lambda #
##########################################################

import sys 
import os
import ROOT
import numpy as np
import array
sys.path.append('../tools')
import fittools as ft
import histtools as ht
sys.path.append('../plotting')
import plotfit as pf

if __name__=='__main__':
    
    # initialization of intput files
    finloc = '/storage_mnt/storage/user/llambrec/K0sAnalysis/files/'
    finloc += 'examples/DoubleMuon_Run2017B/skimmed_1_selected.root'
    treename = 'laurelin' # choose from laurelin or telperion  (or nimloth or celeborn)

    # initialization of histogram settings
    nmax = -1
    xlow = 0.42
    xhigh = 0.58
    binwidth = 0.01
    fitrange = [xlow,xhigh]
    xcenter = (xhigh+xlow)/2.
    xwidth = (xhigh-xlow)/4.
    varname = '_mass'
    xaxtitle = 'invariant mass (GeV)'
    title = r'reconstructed K^{0}_{S} invariant mass'
    label = 'Run2017B data'

    # possibility to make a histogram per bin in another variable
    # (to disable: use empty string for divvarname)
    divvarname = ''
    divbins = array.array('f',[0.,100.])
    show_divinfo = True
    nhists = len(divbins)-1
    if divvarname=='': 
	divvarname = varname
	divbins = array.array('f',[xlow,xhigh])
	show_divinfo = False
	nhists = 1
	
    # other program settings
    do_fill = True
    tempfilename = 'temp_ks.root'
    do_fit = True
    polydegree = 1 # degree of background polynomial fit

    # fill the histograms
    if do_fill:
	nfilled = 0
	histlist = []
	for j in range(nhists):
	    histlist.append(ROOT.TH1F('hist'+str(j),'',int((xhigh-xlow)/binwidth),xlow,xhigh))
	    histlist[j].SetDirectory(0)
	infilelist = []
	if(finloc[-5:] == '.root'): # in case of single file.
	    infilelist = [finloc]
	# (in case of folder: not yet implemented)
	# loop over entries in tree and fill histograms
	for j,infile in enumerate(infilelist):
	    fin = ROOT.TFile.Open(infile)
	    tree = fin.Get(treename)
	    nevents = tree.GetEntries()
	    nprocess = nevents
	    if nmax>0: nprocess = int(min(nmax,nevents))
	    print('file '+str(j+1)+' of '+str(len(infilelist)))
	    print(str(nprocess)+' events out of '+str(nevents)+' will be processed.')
	    nfilled += nprocess
	    for i in range(nprocess):
		if(i>1 and (i+1)%10000==0):
		    print('number of processed events: '+str(i+1)) 
		tree.GetEntry(i)
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
	    histlist = ht.loadallhistograms( tempfilename )
	    fin = ROOT.TFile.Open(tempfilename)
	    divbins = fin.Get("divbins_w")
	    divvarname = str(fin.Get("divvarname_w").GetTitle())
	    fin.Close()
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
	    extrainfo = ' << <<HACK_KS'
	    pf.plot_fit(hist,'test.png',fitfunc=totfit,backfit=backfit,
			label=label,paramdict=paramdict,
			xaxtitle=xaxtitle,yaxtitle='number of reconstructed vertices',
	    		extrainfo=extrainfo)
