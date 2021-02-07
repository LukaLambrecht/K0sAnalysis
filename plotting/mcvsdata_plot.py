###############################################################################
# script reading the output of mcvsdata_fill.py and making sim vs. data plots #
###############################################################################
import ROOT
import sys
sys.path.append('../tools')
import plottools

def loadobjects(histfile):
    ### load all objects, i.e. histograms and other relevant variables
    print('loading histograms')
    f = ROOT.TFile.Open(histfile)
    res = {}
    # load normalization and related paramters
    normalization = int(f.Get("normalization")[0])
    res['normalization'] = normalization
    if(normalization==3):
        normrange = (f.Get("normrange")[0],f.Get("normrange")[1])
        res['normrange'] = normrange
    if(normalization==1):
        lumi = f.Get("lumi")[0]
        res['lumi'] = lumi
    else:
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
    # get bins
    testhist = None
    if len(mchistlist)>0:
	testhist = mchistlist[0]
    elif len(datahistlist)>0:
	testhist = datahistlist[0]
    if testhist is not None: 
	bins = testhist.GetXaxis().GetXbins()
	res['bins'] = bins
    return res

def ratiototxt(histnum,histdenom,outfilename):
    ### calculate ratio hist1/hist2 and write result to txt file
    outtxtfile = open(outfilename,'w')
    outtxtfile.write('format: bin <tab> value <tab> error'+'\n')
    histratio = histnum.Clone()
    histratio.Divide(histdenom)
    for i in range(1,histratio.GetSize()-1):
	outtxtfile.write(str(i)+'\t'+str(histratio.GetBinContent(i))
                         +'\t'+str(histratio.GetBinError(i))+'\n')
    outtxtfile.close()

def plotmcvsdata(mchistlist,datahistlist,outfile,xaxistitle='',yaxistitle='',title='',
		logy=False,drawrange=None,lumi=0.,dotxt=False):
    # optional input args:
    # - logy is a boolean whether to set y axis to log scale
    # - drawrange is a tuple of x-values  where dotted vertical lines will be drawn
    # - lumi is the luminosity value to display (ignored if zero)
    # - dotxt is a boolean whether to write the ratio to a txt file

    ### Create canvas and set parameters
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(600,600)
    pad1 = ROOT.TPad("pad1","",0.,0.3,1.,1.)
    pad1.Draw()
    pad2 = ROOT.TPad("pad2","",0.,0.,1.,0.3)
    pad2.Draw()
    titlefont = 6; titlesize = 30
    labelfont = 5; labelsize = 20
    axtitlefont = 5; axtitlesize = 25
    infofont = 6; infosize = 30
    legendfont = 4; legendsize = 15
    xlow = datahistlist[0].GetBinLowEdge(1)
    xhigh = (datahistlist[0].GetBinLowEdge(datahistlist[0].GetNbinsX())
		+ datahistlist[0].GetBinWidth(datahistlist[0].GetNbinsX()))

    ### Create pad and containers for stacked and summed histograms
    pad1.cd()
    pad1.SetBottomMargin(0.03)
    pad1.SetLeftMargin(0.15)
    pad1.SetTopMargin(0.18)
    pad1.SetTicks(1,1)
    mcstack = ROOT.THStack("mcstack","")
    mchistsum = mchistlist[0].Clone()
    mchistsum.Reset()
    mchistsum.SetStats(False)

    ### Declare legend
    leg = ROOT.TLegend(0.2,0.7,0.85,0.8)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetNColumns(2)
    leg.SetBorderSize(0)

    ### Add MC histograms
    clist = ([ROOT.kAzure-4,ROOT.kAzure+6,ROOT.kViolet,ROOT.kMagenta-9,
		ROOT.kRed,ROOT.kPink-9,ROOT.kBlue+1])
    # (shades of blue and purple)
    #clist = [ROOT.kAzure+6]
    #clist = [ROOT.kAzure]
    #clist = [ROOT.kGreen+1,ROOT.kCyan-7,ROOT.kAzure-4,ROOT.kViolet, 
    #		ROOT.kMagenta-9,ROOT.kRed-4,ROOT.kYellow] 
    # (bright, high contrast)
    #ROOT.gStyle.SetPalette(1)
    for i,hist in enumerate(mchistlist):
	hist.SetStats(False)
	hist.SetLineColor(ROOT.kBlack)
	hist.SetLineWidth(1)
	hist.SetFillColor(clist[i])
	hist.SetFillStyle(1001)
	leg.AddEntry(hist,hist.GetTitle(),"f")
	mcstack.Add(hist)
	mchistsum.Add(hist)

    ### Stacked histogram layout
    mcstack.Draw("HIST")
    # X-axis layout
    xax = mcstack.GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelSize(0)
    # Y-axis layout
    # log scale
    if logy:
	pad1.SetLogy()
	mcstack.SetMaximum(mcstack.GetMaximum()*10)
	mcstack.SetMinimum(mcstack.GetMaximum()/1e2)
    # lin scale
    else:
	mcstack.SetMaximum(mcstack.GetMaximum()*1.5)
	mcstack.SetMinimum(0.)
    yax = mcstack.GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle(yaxistitle)
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.5)
    mcstack.Draw("HIST")

    ### Summed histogram layout
    mchistsum.SetStats(False)
    mchistsum.SetLineWidth(0)
    mchistsum.SetFillColor(ROOT.kOrange)
    mchistsum.SetFillStyle(3001)
    mchistsum.Draw("SAME E2")
    leg.AddEntry(mchistsum,"simulation stat. uncertainty","f")

    ### Add data histograms
    # sum of all data
    if(len(datahistlist)>0):
	hist0 = datahistlist[0]
	for i,hist in enumerate(datahistlist[1:]):
	    hist0.Add(hist)
	hist0.SetMarkerStyle(20)
	hist0.SetMarkerSize(0.9)
	leg.AddEntry(hist0,"observed","ep")
	hist0.Draw("SAME E1")
    else:
	hist0 = mchistlist[0].Clone()
	hist0.Reset()	

    ### Draw normalization range if needed
    if( drawrange is not None ):
	lines = []
	for xval in drawrange:
	    lines.append(ROOT.TLine(xval,mcstack.GetMinimum()/10,
				    xval,mcstack.GetMaximum()*10))
	    lines[-1].SetLineStyle(9)
	    lines[-1].Draw()

    ### Title and other information displays
    leg.Draw()
    # title
    ttitle = ROOT.TLatex()	
    ttitle.SetTextFont(10*titlefont+3)
    ttitle.SetTextSize(titlesize)
    ttitle.DrawLatexNDC(0.15,0.92,title)
    if lumi>0:
	# additional info
	tinfo = ROOT.TLatex()
	tinfo.SetTextFont(10*infofont+3)
	tinfo.SetTextSize(infosize)
	info = 'luminosity: {0:.1f}'.format(lumi/1000.)+r' fb^{-1} (13 TeV)'
	tinfo.DrawLatexNDC(0.55,0.86,info)

    # temp for testing:
    #for i in range(1,mchistsum.GetNbinsX()):
    #	print('bin '+str(i)+' of '+str(mchistsum.GetNbinsX()))
    #	print(hist0.GetBinContent(i))
    #	print(mchistsum.GetBinContent(i))

    '''# TEMP: draw vertical lines
    linestyle = 9
    linewidth = 2
    linecolor = ROOT.kRed
    dl1 = ROOT.TLine(2.9,hist.GetMinimum()/10.,
	            2.9,hist.GetMaximum()*1.2)
    dl1.SetLineWidth(linewidth); dl1.SetLineColor(linecolor)
    dl1.SetLineStyle(linestyle)
    dl1.Draw()
    dl2 = ROOT.TLine(6.8,hist.GetMinimum()/10.,
	            6.8,hist.GetMaximum()*1.2)
    dl2.SetLineWidth(linewidth); dl2.SetLineColor(linecolor)
    dl2.SetLineStyle(linestyle)
    dl2.Draw()
    dl3 = ROOT.TLine(10.9,hist.GetMinimum()/10,
	            10.9,hist.GetMaximum()*1.2)
    dl3.SetLineWidth(linewidth); dl3.SetLineColor(linecolor)
    dl3.SetLineStyle(linestyle)
    dl3.Draw()
    dl4 = ROOT.TLine(16.0,hist.GetMinimum()/10,
	            16.0,hist.GetMaximum()*1.2)
    dl4.SetLineWidth(linewidth); dl4.SetLineColor(linecolor)
    dl4.SetLineStyle(linestyle)
    dl4.Draw()
    tinfo = ROOT.TLatex()
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    tinfo.SetTextColor(linecolor)
    tinfo.DrawLatexNDC(0.26,0.55,"pixel layer 1")
    tinfo.DrawLatexNDC(0.41,0.5,"pixel layer 2")
    tinfo.DrawLatexNDC(0.56,0.45,"pixel layer 3")
    tinfo.DrawLatexNDC(0.75,0.4,"pixel layer 4")'''

    ### Create pad for ratio plots
    pad2.cd()
    pad2.SetLeftMargin(0.15)
    pad2.SetBottomMargin(0.4)
    pad2.SetTopMargin(0.05)
    pad2.SetTicks(1,1)

    ### Divide simulation by itself to obtain expected uncertainty
    histratio2 = mchistsum.Clone()
    for i in range(1,histratio2.GetSize()-1):
	denom = mchistsum.GetBinContent(i)
	if not denom==0: # if zero, do nothing
	    histratio2.SetBinContent(i,histratio2.GetBinContent(i)/denom)
	    histratio2.SetBinError(i,histratio2.GetBinError(i)/denom)
    histratio2.SetStats(False)
    histratio2.SetTitle("")
    histratio2.SetLineWidth(0)
    histratio2.SetFillColor(ROOT.kOrange)
    histratio2.SetFillStyle(3001)
    histratio2.Draw("E2")
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
    histratio2.SetMinimum(0.5)
    histratio2.SetMaximum(1.5)
    #histratio2.SetMinimum(0.)
    #histratio2.SetMaximum(2.)
    yax = histratio2.GetYaxis()
    yax.SetNdivisions(4,5,0,ROOT.kFALSE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle('obs./pred.')
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.5)
    histratio2.Draw("E2")

    ### Divide data by simulation
    histratio = hist0.Clone()
    for i in range(1,histratio.GetSize()-1):
	denom = mchistsum.GetBinContent(i)
	if not denom==0: 
	    histratio.SetBinContent(i,histratio.GetBinContent(i)/denom)
	    histratio.SetBinError(i,histratio.GetBinError(i)/denom)
	else: # if zero: set numerator to zero as well as no sensible comparison can be made
	    histratio.SetBinContent(i,0)
	    histratio.SetBinError(i,0)
    histratio.SetStats(False)
    histratio.Draw("SAME E1")
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

    ### write ratio to txt file if requested
    if dotxt:
	txtoutfile = outfile.split('.')[0]+'_ratio.txt'
	ratiototxtfile(hist0,mchistsum,txtoutfile)

if __name__=='__main__':

    sys.stderr.write('### starting ###\n')
    # configure input parameters (hard-coded)
    histfile = '/storage_mnt/storage/user/llambrec/Kshort/files/skim_ztomumu/selected_legacy/'
    histfile += 'histograms/2016/kshort/rpv/bcksideband/norm3small/defaultbins/histograms.root'
    # (file to read histograms)
    outfile = 'test.png'
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
    normrange = None
    if indict['normalization'] == 3: normrange = indict['normrange']
    
    plotmcvsdata(indict['mchistlist'],indict['datahistlist'],outfile,
		    xaxistitle=xaxistitle,yaxistitle=yaxistitle,title=title,
		    logy=True,drawrange=normrange,lumi=indict['lumi'],dotxt=False)

    sys.stderr.write('### done ###\n')
