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
import optiontools as opt
sys.path.append('../plotting')
import plotfit as pf

if __name__=='__main__':
    
    options = []
    options.append( opt.Option('finloc', vtype='path') )
    options.append( opt.Option('treename', default='laurelin') )
    options.append( opt.Option('varname', default='_mass') )
    options.append( opt.Option('outfilename', default='test') )
    options.append( opt.Option('title', default='invariant mass (GeV)') )
    options.append( opt.Option('xaxtitle', default=r'reconstructed K^{0}_{S} invariant mass') )
    options.append( opt.Option('label', default='data'))
    options.append( opt.Option('nmxax', vtype='int', default=-1) )
    options.append( opt.Option('xlow', vtype='float', default=0.44) )
    options.append( opt.Option('xhigh', vtype='float', default=0.56) )
    options.append( opt.Option('binwidth', vtype='float', default=0.005) )
    options.append( opt.Option('divvarname') )
    options.append( opt.Option('divbins', vtype='list', default=[0.0,999.0]) )
    # (note: do not use '0.' notation, only '0.0' works in the json decoder!)
    options.append( opt.Option('polydegree', vtype='int', default=1) )
    options = opt.OptionCollection( options )
    if len(sys.argv)==1:
	print('Use with following options:')
	print(options)
	sys.exit()
    else:
	options.parse_options( sys.argv[1:] )
	print('Found following configuration:')
	print(options)

    # fit range settings
    fitrange = [options.xlow,options.xhigh]
    xcenter = (options.xhigh+options.xlow)/2.
    xwidth = (options.xhigh-options.xlow)/4.
    nbins = int((options.xhigh-options.xlow)/options.binwidth)

    # possibility to make a histogram per bin in another variable
    show_divinfo = True
    nhists = len(options.divbins)-1
    if options.divvarname is None: 
	options.divvarname = options.varname
	options.divbins = array.array('f',[options.xlow,options.xhigh])
	show_divinfo = False
	nhists = 1
	
    # other program settings
    do_fill = True
    tempfilename = os.path.splitext(options.outfilename)[0]+'_temp.root'
    figname = os.path.splitext(options.outfilename)[0]+'_fig'
    do_fit = True

    # fill the histograms
    if do_fill:
	nfilled = 0
	histlist = []
	for j in range(nhists):
	    histlist.append(ROOT.TH1F('hist'+str(j),'',nbins,options.xlow,options.xhigh))
	    histlist[j].SetDirectory(0)
	infilelist = []
	if(options.finloc[-5:] == '.root'): # in case of single file.
	    infilelist = [options.finloc]
	else:
	    # (in case of folder: not yet implemented)
	    raise Exception('ERROR: input file does not appear to be a .root file.')
	# loop over entries in tree and fill histograms
	for j,infile in enumerate(infilelist):
	    fin = ROOT.TFile.Open(infile)
	    tree = fin.Get(options.treename)
	    nevents = tree.GetEntries()
	    nprocess = nevents
	    if options.nmxax>0: nprocess = int(min(options.nmxax,nevents))
	    print('file '+str(j+1)+' of '+str(len(infilelist)))
	    print(str(nprocess)+' events out of '+str(nevents)+' will be processed.')
	    nfilled += nprocess
	    for i in range(nprocess):
		if(i>1 and (i+1)%10000==0):
		    print('number of processed events: '+str(i+1)) 
		tree.GetEntry(i)
		varvalue = getattr(tree,options.varname)
		divvalue = getattr(tree,options.divvarname)
		if(divvalue>options.divbins[0] and divvalue<options.divbins[-1]):
		    divindex = np.digitize(divvalue,options.divbins)-1
		    histlist[divindex].Fill(varvalue)
	fout = ROOT.TFile(tempfilename,"recreate")
	for hist in histlist:
	    hist.Write()
	divbins_w = ROOT.TVectorD(len(options.divbins))
	for j in range(len(options.divbins)):
	    divbins_w[j] = options.divbins[j]
	divbins_w.Write("divbins_w")
	divvarname_w = ROOT.TNamed("divvarname_w",options.divvarname)
	divvarname_w.Write()
	nfilled_w = ROOT.TVectorD(1); nfilled_w[0] = nfilled
	nfilled_w.Write()
	fout.Close()
	print(str(nfilled)+' instances were written to a histogram file.')

    if do_fit:
	if not do_fill:
	    histlist = ht.loadallhistograms( tempfilename )
	    fin = ROOT.TFile.Open(tempfilename)
	    options.divbins = fin.Get("divbins_w")
	    options.divvarname = str(fin.Get("divvarname_w").GetTitle())
	    fin.Close()
	for j,hist in enumerate(histlist):
	    # step 1: remove middle band and fit sidebands to obtain background
	    histclone = hist.Clone()
	    binlow = histclone.FindBin(xcenter-xwidth)
	    binhigh = histclone.FindBin(xcenter+xwidth)
	    for i in range(binlow,binhigh):
		    histclone.SetBinContent(i,0)
	    guess = [0.]*(options.polydegree+1)
	    backfit,paramdict = ft.poly_fit(histclone,fitrange,guess,"Q0")
	    average = backfit.Eval(xcenter)
	    # step 2: do simultaneous fit with previous fit parameters as initial guesses
	    guess = [xcenter,average*10,0.005,average*10,0.01]
	    for i in range(options.polydegree+1):
		guess.append(paramdict["a"+str(i)])
	    totfit,paramdict = ft.poly_plus_doublegauss_fit(hist,fitrange,guess)
	    print('Fitted parameters:')
	    for el in paramdict:
		print('    '+el+': '+str(paramdict[el]))
	    # step 3: plot
	    extrainfo = ''
	    if show_divinfo: 
		extrainfo = str(options.divbins[j])
		extrainfo += ' < {}  < '.format(options.divvarname)
		extrainfo += str(options.divbins[j+1])
	    extrainfo += ' << <<HACK_KS'
	    pf.plot_fit(hist,figname+'_{}.png'.format(j),fitfunc=totfit,backfit=backfit,
			label=options.label,paramdict=paramdict,
			xaxtitle=options.xaxtitle,yaxtitle='number of reconstructed vertices',
	    		extrainfo=extrainfo)
