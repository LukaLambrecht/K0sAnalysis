####################################################################################
# script to reading the output of mcvsdata_fill2d.py and making sim vs. data plots #
####################################################################################
import ROOT
import numpy as np
import os
import sys
import json
from array import array
sys.path.append(os.path.abspath('../tools'))
import plottools
import histtools

def loadobjects(histfile):
    print('loading histograms')
    f = ROOT.TFile.Open(histfile)
    res = {}
    normalization = int(f.Get("normalization")[0])
    res['normalization'] = normalization
    if(normalization==3):
	res['xnormrange'] = [f.Get("normrange")[0],f.Get("normrange")[1]]
	res['ynormrange'] = [f.Get("normrange")[2],f.Get("normrange")[3]]
    try:
	lumi = f.Get("lumi")[0]
        res['lumi'] = lumi
    except:
        print('WARNING: could not find luminosity value...')
        lumi = 0
        res['lumi'] = 0
    # load histograms
    histlist = plottools.loadallhistograms(histfile)
    mchistlist = []
    datahistlist = []
    for hist in histlist:
        if 'sim' in hist.GetName():
            mchistlist.append(hist)
        elif 'data' in hist.GetName():
            datahistlist.append(hist)
        else:
            print('### WARNING ###: histogram type not recognized: '+hist.GetName())
            print('                 skipping it...')
    print('found '+str(len(datahistlist))+' data files and '
            +str(len(mchistlist))+' simulation files.')
    res['mchistlist'] = mchistlist
    res['datahistlist'] = datahistlist
    return res

def plotmcvsdata2d(mchistlist,datahistlist,outfile,xaxistitle='',yaxistitle='',title='',
		    drawbox=None,lumistr='',writebincontents=True,binmode='default'):
    # binmode: 'default', 'category' or 'equal'

    ### Create canvas and set parameters
    plottools.setTDRstyle()
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(600,600)
    pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
    pad1.Draw()
    titlefont = 4; titlesize = 25
    labelfont = 4; labelsize = 20
    axtitlefont = 4; axtitlesize = 25
    infofont = 4; infosize = 20
    legendfont = 4; legendsize = 20
    p1bottommargin = 0.15
    p1topmargin = 0.07
    p1leftmargin = 0.15
    p1rightmargin = 0.15
    xaxtitleoffset = 1.2
    yaxtitleoffset = 1.7

    ### get bins and related properties
    nxbins = mchistlist[0].GetNbinsX()
    xbins = mchistlist[0].GetXaxis().GetXbins()
    nybins = mchistlist[0].GetNbinsY()
    ybins = mchistlist[0].GetYaxis().GetXbins()

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
    histratio.Divide(mchistsum)
    vals = []
    ers = []
    for i in range(nxbins):
	vals.append([])
	ers.append([])
	for j in range(nybins):
	    ndata = hist0.GetBinContent(i+1,j+1)
	    nmc = mchistsum.GetBinContent(i+1,j+1)
	    if ndata<1 or nmc<0.:
		vals[i].append(0.)
		ers[i].append(0.)
	    else:
		vals[i].append(ndata/nmc)
		error = np.sqrt(ndata/nmc**2+ndata**2/nmc**3)
		ers[i].append(error)

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
    xax.SetTitle(xaxistitle)
    xax.SetTitleFont(10*axtitlefont+3)
    xax.SetTitleSize(axtitlesize)
    xax.SetTitleOffset(xaxtitleoffset)
    # Y-axis layout
    yax = histratio.GetYaxis()
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
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

    ### Title and other information displays
    # title
    ttitle = ROOT.TLatex()	
    ttitle.SetTextFont(10*titlefont+3)
    ttitle.SetTextSize(titlesize)
    ttitle.DrawLatexNDC(p1leftmargin,1-p1topmargin+0.02,title)
    # values and errors
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
		
    # luminosity
    plottools.drawLumi(pad1,cmstext='',extratext='',
			lumitext=lumistr,lumitext_size_factor=0.4,lumitext_offset=0.02)

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

    # configure input parameters (from command line for submission script)
    cmdargs = sys.argv[1:]
    if len(cmdargs)>0:
        coreargs = {'histfile':True,'histtitle':True,'xaxistitle':True,
		    'yaxistitle':True,'outfile':True}
        for arg in cmdargs:
            argname,argval = arg.split('=')
            if argname == 'histfile': histfile = argval; coreargs['histfile']=True
            elif argname == 'histtitle': title = argval; coreargs['histtitle']=True
            elif argname == 'xaxistitle': xaxistitle = argval; coreargs['xaxistitle']=True
            elif argname == 'yaxistitle': yaxistitle = argval; coreargs['yaxistitle']=True
            elif argname == 'outfile': outfile = argval; coreargs['outfile']=True
        if False in coreargs.values():
            print('ERROR: the following core arguments were not defined:')
            for key in coreargs.keys():
                if(coreargs[key]==False): print(key)
            sys.exit()

    indict = loadobjects(histfile)

    # configure other parameters based on input
    xnormrange = None
    ynormrange = None
    if indict['normalization'] == 3: 
	xnormrange = indict['xnormrange']
	ynormrange = indict['ynormrange']
    lumistr = ''
    if indict['lumi'] > 0:
        lumistr = '{0:.3g}'.format(indict['lumi']/1000.)+' fb^{-1} (13 TeV)'

    plotmcvsdata2d(indict['mchistlist'],indict['datahistlist'],outfile,
                    xaxistitle=xaxistitle,yaxistitle=yaxistitle,title=title,
                    drawbox=[xnormrange[0],ynormrange[0],xnormrange[1],ynormrange[1]],
                    lumistr=lumistr,binmode='equal')

    sys.stderr.write('### done ###\n')
