###################################
# Making sim vs. data plots in 2D #
###################################

import ROOT
import numpy as np
import os
import sys
import json
from array import array
sys.path.append(os.path.abspath('../tools'))
import plottools
import histtools
from mcvsdataplotter import loadobjects

def plotmcvsdata2d( mchistlist, datahistlist, outfile,
                    xaxistitle=None, yaxistitle=None, title=None,
                    xaxtitleoffset=None, yaxtitleoffset=None,
                    axtitlesize=None, titlesize=None,
                    p1topmargin=None, p1bottommargin=None,
                    p1leftmargin=None, p1rightmargin=None,
		    drawbox=None, lumistr='', writebincontents=True,
                    binmode='default',
		    outrootfile=None,
                    extrainfos=None, infoleft=None, infotop=None ):
    # binmode: 'default', 'category' or 'equal'.
    # outrootfile: name of the root file to which the histogram corresponding to the figure 
    #              will be written (if None, no output root file is created, only the figure).

    ### Create canvas and set parameters
    plottools.setTDRstyle()
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(1200,600)
    pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
    pad1.Draw()
    titlefont = 4
    if titlesize is None: titlesize = 25
    labelfont = 4; labelsize = 20
    axtitlefont = 4
    if axtitlesize is None: axtitlesize = 25
    infofont = 4; infosize = 20
    legendfont = 4; legendsize = 20
    if p1bottommargin is None: p1bottommargin = 0.15
    if p1topmargin is None: p1topmargin = 0.07
    if p1leftmargin is None: p1leftmargin = 0.1
    if p1rightmargin is None: p1rightmargin = 0.15
    if xaxtitleoffset is None: xaxtitleoffset = 1.2
    if yaxtitleoffset is None: yaxtitleoffset = 1.2
    # extra info box parameters
    if infoleft is None: infoleft = p1leftmargin+0.05
    if infotop is None: infotop = 1-p1topmargin-0.1

    ### get bins and related properties
    nxbins = mchistlist[0].GetNbinsX()
    xbins = mchistlist[0].GetXaxis().GetXbins()
    nybins = mchistlist[0].GetNbinsY()
    ybins = mchistlist[0].GetYaxis().GetXbins()
    # printouts for testing
    #print('Bins:')
    #print(nxbins)
    #print([xbins)
    #print(nybins)
    #print(ybins)

    ### Create pad and containers summed histograms
    pad1.cd()
    pad1.SetBottomMargin(p1bottommargin)
    pad1.SetLeftMargin(p1leftmargin)
    pad1.SetTopMargin(p1topmargin)
    pad1.SetRightMargin(p1rightmargin)
    pad1.SetTicks(1,1)
    mchistsum = mchistlist[0].Clone()
    mchistsum.Reset()
    mchistsum.SetStats(False)

    ### Add MC histograms
    for i,hist in enumerate(mchistlist):
	mchistsum.Add(hist)

    ### Add data histograms
    if(len(datahistlist)>0):
	hist0 = datahistlist[0]
	for i,hist in enumerate(datahistlist[1:]):
	    hist0.Add(hist)
    else:
	hist0 = mchistlist[0].Clone()
	hist0.Reset()
    hist0.SetStats(False)
    hist0.SetTitle("")

    ### create ratio histogram and get arrays of values and errors
    histratio = hist0.Clone()
    histratio.SetName('histratio')
    histratio.SetTitle('data to simulation ratio')
    histratio.Divide(mchistsum)
    # note: default error calculation of Divide is simple relative quadratic addition.
    #       this can be modified in the manual calculation below if required.
    vals = []
    ers = []
    for i in range(nxbins):
	vals.append([])
	ers.append([])
	for j in range(nybins):
	    ndata = hist0.GetBinContent(i+1,j+1)
	    nmc = mchistsum.GetBinContent(i+1,j+1)
	    edata = hist0.GetBinError(i+1,j+1)
	    emc = mchistsum.GetBinError(i+1,j+1)
	    if ndata<1 or nmc<1e-12:
		vals[i].append(0.)
		ers[i].append(0.)
		histratio.SetBinContent(i+1,j+1,0.)
		histratio.SetBinError(i+1,j+1,0.)
	    # option 1: take default Divide behaviour
	    else:
		vals[i].append(histratio.GetBinContent(i+1,j+1))
		ers[i].append(histratio.GetBinError(i+1,j+1))
	    # option 2: modify default Divide behaviour
	    '''else:
		val = ndata/nmc
		vals[i].append(val)
		#error = np.sqrt(ndata/nmc**2+ndata**2/nmc**3)
		error = val*np.sqrt((edata/ndata)**2+(emc/nmc)**2)
		ers[i].append(error)
		histratio.SetBinContent(i+1,j+1,val)
		histratio.SetBinError(i+1,j+1,error)'''
            # printouts for testing
	    #print('bin {}/{}:'.format(i+1,j+1))
	    #print('histratio bincontent: {}'.format(histratio.GetBinContent(i+1,j+1)))
	    #print('histratio binerror: {}'.format(histratio.GetBinError(i+1,j+1)))
	    #print('manual ratio: {}'.format(vals[i][j]))
	    #print('manual error: {}'.format(ers[i][j]))

    ### write the output root file if requested
    # (do this before further transformations to the ratio histogram for plotting)
    if outrootfile is not None:
	f = ROOT.TFile.Open(outrootfile,'recreate')
	histratio.Write()
	f.Close()

    ### optional: redefine histogram as category histogram
    if binmode=='category':
	xbinsnew = array('f',range(len(xbins)))
	ybinsnew = array('f',range(len(ybins)))
	histnew = ROOT.TH2F("histnew",histratio.GetTitle(),nxbins,xbinsnew,nybins,ybinsnew)
	histnew.SetStats(False)
	xlabelsnew = []
	ylabelsnew = []
	for i in range(nxbins):
	    xlabelsnew.append('[{0:.1f},{1:.1f}]'.format(xbins[i],xbins[i+1]))
	for i in range(nybins):
	    ylabelsnew.append('[{0:.1f},{1:.1f}]'.format(ybins[i],ybins[i+1]))
	for i in range(nxbins):
	    for j in range(nybins):
		histnew.Fill(xlabelsnew[i],ylabelsnew[j],vals[i][j])
	if drawbox is not None:
	    drawboxnew = [0,0,0,0]
	    for i in range(nxbins):
		bincenter = (xbins[i]+xbins[i+1])/2.
		if bincenter>drawbox[0]: 
		    drawboxnew[0] = xbinsnew[i]
		    break
	    for j in range(i+1,nxbins):
		bincenter = (xbins[j]+xbins[j+1])/2.
		if bincenter>drawbox[2]:
		    drawboxnew[2] = xbinsnew[j]
		    break
		elif j==nxbins-1: 
		    drawboxnew[2] = xbinsnew[j+1]
		    break
	    for i in range(nybins):
		bincenter = (ybins[i]+ybins[i+1])/2.
		if bincenter>drawbox[1]:
		    drawboxnew[1] = ybinsnew[i]
		    break
	    for j in range(i+1,nybins):
		bincenter = (ybins[j]+ybins[j+1])/2.
		if bincenter>drawbox[3]:
		    drawboxnew[3] = ybinsnew[j]
		    break
		elif j==nybins-1: 
		    drawboxnew[3] = ybinsnew[j+1]
		    break
	    drawbox = drawboxnew
	xbins = xbinsnew
	ybins = ybinsnew
	histratio = histnew

    if binmode=='equal':
	origxax = histratio.GetXaxis()
	origyax = histratio.GetYaxis()
	histratio,xbins,ybins = histtools.make_equal_width_2d(histratio)
	if drawbox is not None:
	    drawbox[0] = histtools.transform_to_equal_width(drawbox[0],origxax)
	    drawbox[2] = histtools.transform_to_equal_width(drawbox[2],origxax)
	    drawbox[1] = histtools.transform_to_equal_width(drawbox[1],origyax)
            drawbox[3] = histtools.transform_to_equal_width(drawbox[3],origyax)

    ### get min and max
    xlow = mchistlist[0].GetXaxis().GetXmin()
    xhigh = mchistlist[0].GetXaxis().GetXmax()
    ylow = histratio.GetYaxis().GetXmin()
    yhigh = histratio.GetYaxis().GetXmax()

    ### plotting and layout
    # X-axis layout
    xax = histratio.GetXaxis()
    xax.SetLabelFont(10*labelfont+3)
    xax.SetLabelSize(labelsize)
    if xaxistitle is not None:
        xax.SetTitle(xaxistitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(xaxtitleoffset)
    # Y-axis layout
    yax = histratio.GetYaxis()
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    if yaxistitle is not None:
        yax.SetTitle(yaxistitle)
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(yaxtitleoffset)
    histratio.SetMinimum(0.8)
    histratio.SetMaximum(1.2)
    ROOT.gStyle.SetPalette(ROOT.kBird)
    histratio.Draw("COLZ")

    ### Draw normalization range if needed
    if drawbox is not None:
	b1 = ROOT.TBox(max(drawbox[0],xlow),max(drawbox[1],ylow),
			min(drawbox[2],xhigh),min(drawbox[3],yhigh))
	b1.SetLineStyle(0)
	b1.SetLineWidth(3)
	b1.SetLineColor(ROOT.kRed)
	b1.SetFillStyle(0)
	#b1.SetFillStyle(3017)
	#b1.SetFillColorAlpha(ROOT.kRed,0.35)
	b1.Draw()

    ### Write title
    if title is not None:
        ttitle = ROOT.TLatex()	
        ttitle.SetTextFont(10*titlefont+3)
        ttitle.SetTextSize(titlesize)
        ttitle.DrawLatexNDC(p1leftmargin,1-p1topmargin+0.02,title)

    # Write values and errors
    if writebincontents:
	tvals = ROOT.TLatex()	
	tvals.SetTextFont(10*infofont+3)
	tvals.SetTextSize(infosize)
	tvals.SetTextAlign(22)
	for i in range(nxbins):
	    xcenter = (xbins[i+1]+xbins[i])/2.
	    for j in range(nybins):
		ycenter = (ybins[j+1]+ybins[j])/2.
		valstr = '{0:.2f}'.format(vals[i][j])
		erstr = '{0:.2f}'.format(ers[i][j])
		tvals.DrawLatex(xcenter,ycenter,'#splitline{'+valstr+'}{'+r'#pm'+erstr+'}')

    # Write extra info
    if extrainfos is not None:
        tinfo = ROOT.TLatex()
        tinfo.SetTextFont(10*infofont+3)
        tinfo.SetTextSize(infosize)
        for i,info in enumerate(extrainfos):
            vspace = 0.07*(float(infosize)/20)
            tinfo.DrawLatexNDC(infoleft,infotop-(i+1)*vspace, info)
		
    # Write luminosity
    plottools.drawLumi( pad1, cmstext='',extratext='',
			lumitext=lumistr,
                        lumitext_size_factor=0.4,
                        lumitext_offset=0.02)

    c1.Update()
    c1.SaveAs(outfile)

if __name__=='__main__':

    sys.stderr.write('### starting ###\n')
    # configure input parameters (hard-coded)
    histfile = '../histograms/test.root'
    # (file to read histograms)
    outfile = '../histograms/test.png'
    # (file to save figure to)
    title = r'K^{0}_{S} vertex radial distance'
    xaxistitle = 'radial distance (cm)' # set x axis title
    yaxistitle = r'ditrack p_{T} sum (GeV)' # set y axis title
    # optional arguments
    outrootfile = None
    doextrainfos = False
    extrainfos = []

    # configure input parameters (from command line for submission script)
    cmdargs = sys.argv[1:]
    if len(cmdargs)>0:
        coreargs = {'histfile':True,'histtitle':True,'xaxistitle':True,
		    'yaxistitle':True,'outfile':True}
        for arg in cmdargs:
            argname,argval = arg.split('=')
            # required arguments
            if argname == 'histfile': histfile = argval; coreargs['histfile']=True
            elif argname == 'histtitle': title = argval; coreargs['histtitle']=True
            elif argname == 'xaxistitle': xaxistitle = argval; coreargs['xaxistitle']=True
            elif argname == 'yaxistitle': yaxistitle = argval; coreargs['yaxistitle']=True
            elif argname == 'outfile': outfile = argval; coreargs['outfile']=True
            # optional arguments
	    elif argname == 'outrootfile': outrootfile = argval
            elif argname == 'doextrainfos': doextrainfos = (argval.lower()=='true')
            elif argname == 'extrainfos': extrainfos = argval
        if False in coreargs.values():
            print('ERROR: the following core arguments were not defined:')
            for key in coreargs.keys():
                if(coreargs[key]==False): print(key)
            sys.exit()

    indict = loadobjects(histfile, histdim=2)

    # configure other parameters based on input
    xvarname = indict['xvarname']
    yvarname = indict['yvarname']
    normrange = None
    if indict['normalization'] == 3: 
	normrange = indict['normrange']
	normvariable = indict['normvariable']
    lumistr = ''
    if indict['lumi'] > 0:
        lumistr = '{0:.3g}'.format(indict['lumi']/1000.)+' fb^{-1} (13 TeV)'

    # make extra info
    infoleft = None
    infotop = None
    p1rightmargin = None
    if doextrainfos:
      p1rightmargin = 0.35
      infoleft = 0.8
      infotop = 0.7
      if len(extrainfos)==0:
        if( indict['v0type'] is not None ):
          v0type = indict['v0type']
          if v0type.lower()=='ks':
            extrainfos.append('K^{0}_{S} candidates')
          elif v0type.lower()=='la':
            extrainfos.append('#Lambda^{0} candidates')
        if( indict['bckmode'] is not None ):
          bckmode = indict['bckmode']
          if bckmode.lower()=='default':
            extrainfos.append('Background not subtracted')
          elif bckmode.lower()=='sideband':
            extrainfos.append('Background subtracted')
        if( indict['normalization'] is not None ):
          norm = indict['normalization']
          if norm==1:
            extrainfos.append('Normalized to luminosity')
          if norm==2:
            extrainfos.append('Normalized to data')
          if norm==3:
            extrainfos.append('Normalized in range')
          if norm==4:
            extrainfos.append('Normalized to data events')
      else:
        extrainfos = extrainfos.split(',')

    plotmcvsdata2d( indict['mchistlist'], indict['datahistlist'], outfile,
                    xaxistitle=xaxistitle, yaxistitle=yaxistitle, title=title,
                    lumistr=lumistr, binmode='equal', outrootfile=outrootfile,
                    extrainfos=extrainfos, infoleft=infoleft, infotop=infotop,
                    p1rightmargin=p1rightmargin )

    sys.stderr.write('### done ###\n')
