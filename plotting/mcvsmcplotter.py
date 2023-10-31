###############################################################################
# script reading the output of mcvsdata_fill.py and making sim vs. data plots #
###############################################################################
import ROOT
import sys
from mcvsdata_plot import loadobjects,loadobjects_old
sys.path.append('../tools')
import plottools
import histtools

def plotmcvsmc(histlist,outfile,xaxistitle='',yaxistitle='',title='',
                logy=False,drawrange=None,lumistr='',
		ratiopad=False,ratiorange=None,
		normalize=False):
    
    ### Create canvas and set parameters
    plottools.setTDRstyle()
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(600,600)
    if ratiopad:
	pad1 = ROOT.TPad("pad1","",0.,0.3,1.,1.)
	pad1.Draw()
	pad2 = ROOT.TPad("pad2","",0.,0.,1.,0.3)
	pad2.Draw()
    else:
	pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
	pad1.Draw()
    titlefont = 4; titlesize = 22
    labelfont = 4; labelsize = 20
    axtitlefont = 4; axtitlesize = 25
    infofont = 4; infosize = 30
    legendfont = 4; legendsize = 20
    xlow = histlist[0].GetBinLowEdge(1)
    xhigh = (histlist[0].GetBinLowEdge(histlist[0].GetNbinsX())
                + histlist[0].GetBinWidth(histlist[0].GetNbinsX()))

    ### Create pad and containers for stacked and summed histograms
    pad1.cd()
    if ratiopad: pad1.SetBottomMargin(0.03)
    else: pad1.SetBottomMargin(0.15)
    pad1.SetLeftMargin(0.15)
    pad1.SetTopMargin(0.12)
    pad1.SetTicks(1,1)
    pad1.SetFrameLineWidth(2)
    pad1.Draw()

    ### Declare legend
    leg = ROOT.TLegend(0.4,0.65,0.9,0.85)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetNColumns(2)
    leg.SetBorderSize(0)

    ### Normalize histograms to unit surface area
    if normalize:
	for hist in histlist:
	    integral = hist.Integral("width")
	    hist.Scale(1./integral)

    ### Add histograms
    clist = ([ROOT.kAzure-4,ROOT.kAzure+6,ROOT.kViolet,ROOT.kMagenta-9,
                ROOT.kRed,ROOT.kPink-9,ROOT.kBlue+1])
    # (shades of blue and purple)
    #clist = [ROOT.kAzure+6]
    #clist = [ROOT.kAzure]
    #clist = [ROOT.kGreen+1,ROOT.kCyan-7,ROOT.kAzure-4,ROOT.kViolet, 
    #           ROOT.kMagenta-9,ROOT.kRed-4,ROOT.kYellow] 
    # (bright, high contrast)
    #ROOT.gStyle.SetPalette(1)
    for i,hist in enumerate(histlist):
        hist.SetStats(False)
        hist.SetLineWidth(3)
        hist.SetLineColor(clist[i])
        leg.AddEntry(hist,hist.GetTitle(),"l")

    ### Histogram layout
    histlist[0].Draw("HIST E1")
    # X-axis layout
    xax = histlist[0].GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelSize(0)
    # Y-axis layout
    (totmin,totmax) = histtools.getminmax( histlist )
    # log scale
    if logy:
        pad1.SetLogy()
        histlist[0].SetMaximum(totmax*1e2)
        histlist[0].SetMinimum(totmin/5)
    # lin scale
    else:
        histlist[0].SetMaximum(totmax*1.5)
        histlist[0].SetMinimum(0.)
    yax = histlist[0].GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle(yaxistitle)
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.5)
    histlist[0].Draw("HIST E1")
    for hist in histlist[1:]: hist.Draw("HIST E1 SAME")

    ### Draw normalization range if needed
    if( drawrange is not None ):
        lines = []
        for xval in drawrange:
            lines.append(ROOT.TLine(xval,totmin/10,
                                    xval,totmax*10))
            lines[-1].SetLineStyle(9)
            lines[-1].Draw()

    ### Title and other information displays
    leg.Draw()
    # title
    ttitle = ROOT.TLatex()
    ttitle.SetTextFont(10*titlefont+3)
    ttitle.SetTextSize(titlesize)
    ttitle.DrawLatexNDC(0.15,0.92,title)
    plottools.drawLumi(pad1,cmstext_size_factor=0.4,extratext="",
                        lumitext=lumistr,lumitext_size_factor=0.4,lumitext_offset=0.02)
    
    if ratiopad:

	### Create pad for ratio plots
	pad2.cd()
	pad2.SetLeftMargin(0.15)
	pad2.SetBottomMargin(0.4)
	pad2.SetTopMargin(0.05)
	pad2.SetTicks(1,1)
	pad2.SetFrameLineWidth(2)
	pad2.Draw()

	### Divide first histogram by itself
	histratiolist = []
	histratio2 = histlist[0].Clone()
	histratiolist.append(histratio2)
	for i in range(1,histratio2.GetSize()-1):
	    denom = histlist[0].GetBinContent(i)
	    if not denom==0: # if zero, do nothing
		histratio2.SetBinContent(i,histratio2.GetBinContent(i)/denom)
		histratio2.SetBinError(i,histratio2.GetBinError(i)/denom)
	histratio2.SetStats(False)
	histratio2.SetTitle("")
	#histratio2.SetLineWidth(0)
	#histratio2.SetFillColor(ROOT.kOrange)
	#histratio2.SetFillStyle(3001)
	histratio2.Draw("HIST E1")
	# X-axis layout
	xax = histratio2.GetXaxis()
	xax.SetNdivisions(10,4,0,ROOT.kTRUE)
	xax.SetLabelFont(10*labelfont+3)
	xax.SetLabelSize(labelsize)
	xax.SetTitle(xaxistitle)
	xax.SetTitleFont(10*axtitlefont+3)
	xax.SetTitleSize(axtitlesize)
	xax.SetTitleOffset(3.)
	# Y-axis layout
	if ratiorange is None: ratiorange = (0.5,1.5)
	histratio2.SetMinimum(ratiorange[0])
	histratio2.SetMaximum(ratiorange[1])
	yax = histratio2.GetYaxis()
	yax.SetNdivisions(4,5,0,ROOT.kFALSE)
	yax.SetLabelFont(10*labelfont+3)
	yax.SetLabelSize(labelsize)
	yax.SetTitle('obs./pred.')
	yax.SetTitleFont(10*axtitlefont+3)
	yax.SetTitleSize(axtitlesize)
	yax.SetTitleOffset(1.5)
	histratio2.Draw("HIST E1")

	### Divide other histograms by first one
	for hist in histlist[1:]:
	    histratio = hist.Clone()
	    histratiolist.append(histratio)
	    for i in range(1,histratio.GetSize()-1):
		denom = histlist[0].GetBinContent(i)
		if not denom==0:
		    histratio.SetBinContent(i,histratio.GetBinContent(i)/denom)
		    histratio.SetBinError(i,histratio.GetBinError(i)/denom)
		else: # if zero: set numerator to zero as well as no sensible comparison can be made
		    histratio.SetBinContent(i,0)
		    histratio.SetBinError(i,0)
	    histratio.SetStats(False)
	    histratio.Draw("HIST E1 SAME")
	    c1.Update()

	### Draw unit ratio line
	l = ROOT.TLine(xlow,1.0,xhigh,1.0)
	l.SetLineStyle(9)
	l.Draw()

	### Draw normalization range if needed
	if( drawrange is not None ):
	    for xval in drawrange:
		lines.append(ROOT.TLine(xval,histratio2.GetMinimum(),
                                    xval,histratio2.GetMaximum()))
		lines[-1].SetLineStyle(9)
		lines[-1].Draw()

    c1.Update()
    c1.SaveAs(outfile.split('.')[0]+'.png')
    c1.SaveAs(outfile.split('.')[0]+'.pdf')


if __name__=='__main__':

    sys.stderr.write('### starting ###\n')
    # configure input parameters (hard-coded)
    histfile = '/storage_mnt/storage/user/llambrec/K0sAnalysis/files/oldfiles/'
    histfile += 'histograms/Run-II/kshort/rpv_bcksideband_norm3small_defaultbins/histograms.root'
    # (file to read histograms)
    outfile = ''
    outfile += 'test.png'
    # (file to save figure to)
    title = r'K^{0}_{S} vertex radial distance'
    xaxistitle = 'radial distance (cm)' # set x axis title
    yaxistitle = 'number of vertices' # set y axis title of upper graph

    # configure input parameters (from command line for submission script)
    cmdargs = sys.argv[1:]
    if len(cmdargs)>0:
        coreargs = {'histfile':False,'histtitle':False,'xaxistitle':False,
                    'yaxistitle':False,'outfile':False}
        for arg in cmdargs:
            argname,argval = arg.split('=')
            if argname == 'histfile': histfile = argval; coreargs['histfile']=True
            elif argname == 'histtitle': title = argval; coreargs['histtitle']=True
            elif argname == 'xaxistitle': xaxistitle = argval; coreargs['xaxistitle']=True
            elif argname == 'yaxistitle': yaxistitle = argval; coreargs['yaxistitle']=True
            elif argname == 'outfile': outfile = argval; coreargs['outfile']=True
        if False in coreargs.values():
            print('### ERROR ###: the following core arguments were not defined:')
            for key in coreargs.keys():
                if(coreargs[key]==False): print(key)
            sys.exit()

    indict = loadobjects(histfile)
    #indict = loadobjects_old(histfile) # WARNING: temporarily changed to loadobjects_old!

    # configure other parameters based on input
    normrange = None
    if indict['normalization'] == 3: normrange = indict['normrange']
    lumistr = ''
    if indict['lumi'] > 0:
        lumistr = '{0:.3g}'.format(indict['lumi']/1000.)+' fb^{-1} (13 TeV)'

    plotmcvsmc(indict['mchistlist']+indict['datahistlist'],outfile,
                    xaxistitle=xaxistitle,yaxistitle=yaxistitle,title=title,
                    logy=True,
                    lumistr=lumistr,ratiopad=True,ratiorange=(0.,2.),
		    normalize=True)

    sys.stderr.write('### done ###\n')

