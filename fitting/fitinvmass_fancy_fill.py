##########################################################
# make invariant pass plots and fits of kshort or lambda #
##########################################################
# extension: more fancy plots (data and simulation together)

import sys 
import os
import ROOT
import numpy as np
import array

if __name__=='__main__':
    
    # initialization of intput files
    finloc = sys.argv[1] # input data file
    outfile = sys.argv[2] # output file
    lumi = 0.
    if len(sys.argv)>3:
	lumi = float(sys.argv[3])

    # initialization of histogram settings
    treename = 'laurelin' # tree in input root files to read variable from
    nmax = -1 # maximum number of processed instances
    xlow = 0.44
    xhigh = 0.56
    binwidth = 0.002
    fitrange = [xlow,xhigh] # range to fit in
    xcenter = (xhigh+xlow)/2. # initial guess of peak center
    xwidth = (xhigh-xlow)/4. # initial guess of peak width
    varname = '_KsInvMass'

    # possibility to make a histogram per bin in another variable
    # (to disable: use empty string for divvarname)
    divvarname = '_KsRPV'
    divvarlabel = '#Delta_{2D} (cm)'
    divbins = array.array('f',[0.,0.5,1.5,4.,20.])
    show_divinfo = True
    nhists = len(divbins)-1
    if divvarname=='': 
	divvarname = varname
	divbins = array.array('f',[xlow,xhigh])
	show_divinfo = False
	nhists = 1
	
    # fill the histograms
    nfilled = 0
    histlist = []
    for j in range(nhists):
	hist = ROOT.TH1F('hist_'+str(j),'',int((xhigh-xlow)/binwidth),xlow,xhigh)
	hist.SetDirectory(0)
	histlist.append(hist)
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

    # make output file
    fout = ROOT.TFile(outfile,"recreate")
    # write histograms
    for hist in histlist:
	hist.Write()
    # write secondary variable bins
    divbins_w = ROOT.TVectorD(len(divbins))
    for j in range(len(divbins)):
	divbins_w[j] = divbins[j]
    divbins_w.Write("divbins_w")
    # write secondary variable name and label
    divvarname_w = ROOT.TNamed("divvarname_w",divvarname)
    divvarname_w.Write()
    divvarlabel_w = ROOT.TNamed("divvarlabel_w",divvarlabel)
    divvarlabel_w.Write()
    # write luminosity and number of processed events
    nfilled_w = ROOT.TVectorD(1); nfilled_w[0] = nfilled
    nfilled_w.Write("nfilled_w")
    lumi_w = ROOT.TVectorD(1); lumi_w[0] = lumi
    lumi_w.Write("lumi_w")

    # close output file
    fout.Close()
    print(str(nfilled)+' instances were written to a histogram file.')
