##########################################################
# make invariant pass plots and fits of kshort or lambda #
##########################################################
# extension: more fancy plots (data and simulation together)

import sys 
import os
import ROOT
import numpy as np
import array
sys.path.append('../tools')
import fittools as ft
import histtools as ht
sys.path.append('../plotting')
from plotfitmcvsdata import plot_fit_mcvsdata

if __name__=='__main__':
    
    # initialization of intput files
    datafinloc = sys.argv[1] # input data file
    datalabel = sys.argv[2] # legend entry for data
    simfinloc = sys.argv[3] # simlation input file
    simlabel = sys.argv[4] # legend entry for simulation
    outfile = sys.argv[5] # output file

    # load all objects from input files
    datahistlist = ht.loadallhistograms( datafinloc )
    datafin = ROOT.TFile.Open( datafinloc )
    divbins = datafin.Get("divbins_w")
    divbins = [divbins[j] for j in range(len(datahistlist)+1)]
    divvarname = str(datafin.Get("divvarname_w").GetTitle())
    divvarlabel = str(datafin.Get("divvarlabel_w").GetTitle())
    lumi = float(datafin.Get("lumi_w")[0])
    datafin.Close()
    simhistlist = ht.loadallhistograms( simfinloc )
    simfin = ROOT.TFile.Open( simfinloc )
    simdivbins = simfin.Get("divbins_w")
    simdivbins = [simdivbins[j] for j in range(len(simhistlist)+1)]
    if simdivbins != divbins:
	raise Exception('ERROR: divbins in data and simulation file do not agree;'
			+' found {} and {}'.format(divbins,simdivbins))
    if str(simfin.Get("divvarname_w").GetTitle())!= divvarname:
	raise Exception('ERROR: divvarname in data and simulation file do not agree;'
                        +' found {} and {}'.format(divvarname,
			str(simfin.Get("divvarname_w").GetTitle())))
    simfin.Close()

    # initialization of fit settings
    polydegree = 1 # degree of background polynomial fit 
    xlow = datahistlist[0].GetBinLowEdge(1)
    xhigh = (datahistlist[0].GetBinLowEdge(datahistlist[0].GetNbinsX())
	     +datahistlist[0].GetBinWidth(datahistlist[0].GetNbinsX()))
    fitrange = [xlow,xhigh] # range to fit in
    xcenter = (xhigh+xlow)/2. # initial guess of peak center
    xwidth = (xhigh-xlow)/4. # initial guess of peak width 

    # initialization of plot settings
    xaxtitle = 'm(#pi^{+},#pi^{-}) (GeV)'
    yaxtitle = 'Number of reconstructed vertices'

    # normalization method 1: normalize each simulated histogram to data
    for j in range(len(datahistlist)):
	scale = datahistlist[j].Integral()/simhistlist[j].Integral()
	simhistlist[j].Scale(scale)
    # normalization method 2: normalize first bin
    #scale = datahistlist[0].Integral()/simhistlist[0].Integral()
    #for j in range(len(datahistlist)):
    #	simhistlist[j].Scale(scale)

    for j in range(len(datahistlist)):
	datahist = datahistlist[j]
	simhist = simhistlist[j]
	# step 1: remove middle band and fit sidebands to obtain background
	histclone = datahist.Clone()
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
	totfit,paramdict = ft.poly_plus_doublegauss_fit(datahist,fitrange,guess)
	print('Fitted parameters:')
	for el in paramdict:
	    print('    '+el+': '+str(paramdict[el]))
	# also get uncertainty on best-fit value for mass
	# not very clean version here, needed to do quickly
	idx = 0
	for i,k in enumerate(paramdict.keys()):
	    if k=='#mu': idx = i
	mu_central = totfit.GetParameter(idx)
	mu_unc = totfit.GetParError(idx)
	# step 3: plot
	lumitext = '' if lumi==0 else '{0:.3g} '.format(float(lumi)/1000.) + 'fb^{-1} (13 TeV)'
	extrainfo = str(divbins[j])+' < '+str(divvarlabel)+'  < '+str(divbins[j+1])
	extrainfo += ' << <<Fitted K_{S}^{0} mass: <<  '
	extrainfo += '{:.3f} #pm {:.3f} MeV'.format(paramdict['#mu']*1000,mu_unc*1000)
	#extrainfo += ' << <<HACK_KS'
	thisoutfile = outfile
	if len(datahistlist)>1:
	    thisoutfile = outfile.split('.')[0]+'_{}.png'.format(j)
	plot_fit_mcvsdata(datahist.Clone(),simhist.Clone(),thisoutfile,
			    fitfunc=totfit,backfit=backfit,
			    simlabel=simlabel,datalabel=datalabel,paramdict=None,
			    xaxtitle=xaxtitle,yaxtitle=yaxtitle,
			    extrainfo=extrainfo,lumitext=lumitext)
	plot_fit_mcvsdata(datahist.Clone(),simhist.Clone(),thisoutfile.replace('.png','.pdf'),
			    fitfunc=totfit,backfit=backfit,
                            simlabel=simlabel,datalabel=datalabel,paramdict=None,
                            xaxtitle=xaxtitle,yaxtitle=yaxtitle,
                            extrainfo=extrainfo,lumitext=lumitext)
