#############################
# Making sim vs. data plots #
#############################

import ROOT
import sys
import os
import numpy as np
import plottools as pt
sys.path.append(os.path.abspath('../tools'))
import histtools as ht

def loadobjects(histfile, histdim=1):
    ### load all objects, i.e. histograms and other relevant variables
    print('loading histograms')
    f = ROOT.TFile.Open(histfile)
    res = {}
    # load normalization
    normalization = int(f.Get("normalization")[0])
    res['normalization'] = normalization
    if(normalization==3):
        normrange = (f.Get("normrange")[0],f.Get("normrange")[1])
        res['normrange'] = normrange
        normvariable = f.Get("normvariable").GetTitle()
        res['normvariable'] = normvariable
    # load luminosity
    try:
	lumi = f.Get("lumi")[0]
	res['lumi'] = lumi
    except:
	print('WARNING: could not find luminosity value...')
        lumi = 0
        res['lumi'] = 0
    # load background mode
    try:
        bckmode = int(f.Get("bckmode")[0])
        res['bckmode'] = None
        if bckmode==1: res['bckmode'] = 'default'
        if bckmode==2: res['bckmode'] = 'sideband'
    except:
        print('WARNING: could not find bckmode value...')
        res['bckmode'] = None
    # load v0type
    try:
        v0type = int(f.Get("v0type")[0])
        res['v0type'] = None
        if v0type==1: res['v0type'] = 'ks'
        if v0type==2: res['v0type'] = 'la'
    except:
        print('WARNING: could not find v0type value...')
        res['v0type'] = None
    # load meta-info
    if histdim==1:
        varname = f.Get('varname').GetTitle()
        res['varname'] = varname
    elif histdim==2:
        xvarname = f.Get('xvarname').GetTitle()
        res['xvarname'] = xvarname
        yvarname = f.Get('yvarname').GetTitle()
        res['yvarname'] = yvarname
    # load histograms
    histlist = ht.loadallhistograms(histfile)
    mchistlist = []
    datahistlist = []
    for hist in histlist:
        if 'sim' in hist.GetName() or 'Sim' in hist.GetName():
            mchistlist.append(hist)
        elif 'data' in hist.GetName() or 'Data' in hist.GetName():
            datahistlist.append(hist)
        else:
            msg = 'WARNING: histogram type not recognized'
            msg += ' for histogram with name "{}";'.format(hist.GetName())
            msg += ' skipping it...'
            print(msg)
    print('found {} data files and {} simulation files.'.format(
          len(datahistlist),len(mchistlist)))
    res['mchistlist'] = mchistlist
    res['datahistlist'] = datahistlist
    # get bins
    testhist = None
    if len(mchistlist)>0:
	testhist = mchistlist[0]
    elif len(datahistlist)>0:
	testhist = datahistlist[0]
    if testhist is not None:
        if histdim==1:
	    bins = testhist.GetXaxis().GetXbins()
	    res['bins'] = bins
        elif histdim==2:
            xbins = testhist.GetXaxis().GetXbins()
            ybins = testhist.GetYaxis().GetXbins()
            res['xbins'] = xbins
            res['ybins'] = ybins 
    return res

def loadobjects_old(histfile):
    ### same as above, but for older files
    # WARNING: only implemented to quickly make work for one specific file type,
    #          not guaranteed to work on all older files
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
    histlist = ht.loadallhistograms(histfile)
    mchistlist = []
    datahistlist = []
    for hist in histlist:
        if 'mc' in hist.GetName():
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

def getminmax(datahist, mchist, yaxlog, margin=True):
    # get suitable minimum and maximum values for plotting a given data hist and summed mc hist
    # find maximum:
    histmax = (mchist.GetBinContent(mchist.GetMaximumBin())
                +mchist.GetBinErrorUp(mchist.GetMaximumBin()))
    histmax = max(histmax,datahist.GetBinContent(datahist.GetMaximumBin())
                            +datahist.GetBinErrorUp(datahist.GetMaximumBin()))
    if not yaxlog:
        if margin: histmax *= 1.5
        return (0, histmax)
    # find minimum (manually to avoid zero and small dummy values)
    histmin = histmax
    for i in range(1,mchist.GetNbinsX()+1):
        if( (not mchist.GetBinContent(i)<1e-3) and mchist.GetBinContent(i)<histmin):
            histmin = mchist.GetBinContent(i)
    if margin:
      histmin = histmin/2.
      histmax = histmax*np.power(histmax/histmin,0.6)
    return (histmin, histmax)

def plotmcvsdata(mchistlist, datahistlist, outfile,
		xaxistitle='', yaxistitle='', title='',
		colorlist=None,
		logy=False, drawrange=None, lumistr='', dotxt=False,
                extrainfos=[], infosize=None, infoleft=None, infotop=None,
                do2016pixel=False, do20172018pixel=False ):
    # optional input args:
    # - colorlist: list of same length as mchistlist with root colors
    # - logy is a boolean whether to set y axis to log scale
    # - drawrange is a tuple of x-values  where dotted vertical lines will be drawn
    # - lumistr is the luminosity string to display (ignored if zero)
    # - dotxt is a boolean whether to write the ratio to a txt file

    ### Create canvas and set parameters
    pt.setTDRstyle() 
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(600,600)
    pad1 = ROOT.TPad("pad1","",0.,0.3,1.,1.)
    pad1.Draw()
    pad2 = ROOT.TPad("pad2","",0.,0.,1.,0.3)
    pad2.Draw()
    titlefont = 4; titlesize = 22
    labelfont = 4; labelsize = 20
    axtitlefont = 4; axtitlesize = 25
    infofont = 4
    if infosize is None: infosize = 20
    legendfont = 4; legendsize = 0.
    # (use 0 to automatically adjust text size to legend box)
    if infoleft is None: infoleft = 0.2
    if infotop is None: infotop = 0.8
    xlow = datahistlist[0].GetBinLowEdge(1)
    xhigh = (datahistlist[0].GetBinLowEdge(datahistlist[0].GetNbinsX())
		+ datahistlist[0].GetBinWidth(datahistlist[0].GetNbinsX()))
    statcolor = ROOT.kOrange
    statfillstyle = 1001
    stattransparency = 0.5
    if colorlist is None: 
	colorlist = ([ROOT.kAzure-4,ROOT.kAzure+6,ROOT.kViolet,ROOT.kMagenta-9,
		      ROOT.kRed,ROOT.kPink-9,ROOT.kBlue+1])
	# (shades of blue and purple)
	#colorlist = ([ROOT.kGreen+1,ROOT.kCyan-7,ROOT.kAzure-4,ROOT.kViolet, 
	#         ROOT.kMagenta-9,ROOT.kRed-4,ROOT.kYellow])
	# (bright, high contrast)

    ### Create pad and containers for stacked and summed histograms
    pad1.cd()
    pad1.SetBottomMargin(0.0)
    pad1.SetLeftMargin(0.15)
    pad1.SetTopMargin(0.12)
    pad1.SetTicks(1,1)
    pad1.SetFrameLineWidth(2)
    pad1.Draw()
    mcstack = ROOT.THStack("mcstack","")
    mchistsum = mchistlist[0].Clone()
    mchistsum.Reset()
    mchistsum.SetStats(False)

    ### Declare legend
    leg = ROOT.TLegend(0.4,0.65,0.9,0.85)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetNColumns(2)
    leg.SetBorderSize(0)

    ### Add MC histograms
    for i,hist in enumerate(mchistlist):
	hist.SetStats(False)
	hist.SetLineColor(ROOT.kBlack)
	hist.SetLineWidth(1)
	hist.SetFillColor(colorlist[i])
	hist.SetFillStyle(1001)
	leg.AddEntry(hist,hist.GetTitle(),"f")
	mcstack.Add(hist)
	mchistsum.Add(hist)

    ### Add data histograms
    # sum of all data
    drawdata = True
    if(len(datahistlist)>0):
        hist0 = datahistlist[0]
        for i,hist in enumerate(datahistlist[1:]):
            hist0.Add(hist)
        hist0.SetMarkerStyle(20)
        hist0.SetMarkerSize(0.9)
        leg.AddEntry(hist0,"Data","ep")
    else:
        hist0 = mchistlist[0].Clone()
        hist0.Reset()
        drawdaa = False

    ### Stacked histogram layout
    mcstack.Draw("HIST")
    # X-axis layout
    xax = mcstack.GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelSize(0)
    # Y-axis layout
    (ymin,ymax) = getminmax(hist0,mchistsum,yaxlog=logy,margin=True)
    if logy: pad1.SetLogy()
    mcstack.SetMaximum(ymax)
    mcstack.SetMinimum(ymin)
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
    mchistsum.SetFillColorAlpha(statcolor, stattransparency)
    mchistsum.SetFillStyle(statfillstyle)
    mchistsum.Draw("SAME E2")
    leg.AddEntry(mchistsum,"Stat. uncertainty","f")

    ### Draw data histogram
    if drawdata: hist0.Draw("SAME E1")

    ### Draw normalization range if needed
    if( drawrange is not None ):
	lines = []
	for xval in drawrange:
	    lines.append(ROOT.TLine(xval,ymin,xval,ymax))
	    lines[-1].SetLineStyle(9)
	    lines[-1].Draw()

    ### Title and other information displays
    leg.Draw()
    # title
    ttitle = ROOT.TLatex()	
    ttitle.SetTextFont(10*titlefont+3)
    ttitle.SetTextSize(titlesize)
    ttitle.DrawLatexNDC(0.15,0.92,title)
    pt.drawLumi(pad1,cmstext_size_factor=0.5,extratext="",
			lumitext=lumistr,lumitext_size_factor=0.4,lumitext_offset=0.02)

    ### Draw extra info
    tinfo = ROOT.TLatex()
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    for i,info in enumerate(extrainfos):
        vspace = 0.07*(float(infosize)/20)
        tinfo.DrawLatexNDC(infoleft,infotop-(i+1)*vspace, info)

    # temp for testing:
    #for i in range(1,mchistsum.GetNbinsX()):
    #	print('bin '+str(i)+' of '+str(mchistsum.GetNbinsX()))
    #	print(hist0.GetBinContent(i))
    #	print(mchistsum.GetBinContent(i))

    # draw vertical lines for 2016 pixel detector
    if do2016pixel:
      linestyle = 9
      linewidth = 2
      linecolor = ROOT.kRed
      adhocymin = ymin*0.4
      adhocymax = ymax*0.15
      if not logy:
        adhocymin = 0.
        adhocymax = ymax*0.7
      dl1 = ROOT.TLine(4.4,adhocymin, 4.4,adhocymax)
      dl1.SetLineWidth(linewidth); dl1.SetLineColor(linecolor)
      dl1.SetLineStyle(linestyle)
      dl1.Draw()
      dl2 = ROOT.TLine(7.3,adhocymin, 7.3,adhocymax)
      dl2.SetLineWidth(linewidth); dl2.SetLineColor(linecolor)
      dl2.SetLineStyle(linestyle)
      dl2.Draw()
      dl3 = ROOT.TLine(10.2,adhocymin, 10.2,adhocymax)
      dl3.SetLineWidth(linewidth); dl3.SetLineColor(linecolor)
      dl3.SetLineStyle(linestyle)
      dl3.Draw()
      tinfo = ROOT.TLatex()
      tinfo.SetTextFont(10*infofont+3)
      tinfo.SetTextSize(infosize)
      tinfo.SetTextColor(linecolor)
      tinfo.DrawLatexNDC(0.33,0.52,"PXL1")
      tinfo.DrawLatexNDC(0.45,0.47,"PXL2")
      tinfo.DrawLatexNDC(0.57,0.42,"PXL3")

    # draw vertical lines for 2017/2018 pixel detector
    if do20172018pixel:
      linestyle = 9
      linewidth = 2
      linecolor = ROOT.kRed
      adhocymin = ymin*0.4
      adhocymax = ymax*0.15
      adhocymaxdl4 = ymax*0.03
      if not logy:
        adhocymin = 0.
        adhocymax = ymax*0.7
        adhocymaxdl4 = ymax*0.4
      dl1 = ROOT.TLine(2.9,adhocymin,
	            2.9,adhocymax)
      dl1.SetLineWidth(linewidth); dl1.SetLineColor(linecolor)
      dl1.SetLineStyle(linestyle)
      dl1.Draw()
      dl2 = ROOT.TLine(6.8,adhocymin,
	            6.8,adhocymax)
      dl2.SetLineWidth(linewidth); dl2.SetLineColor(linecolor)
      dl2.SetLineStyle(linestyle)
      dl2.Draw()
      dl3 = ROOT.TLine(10.9,adhocymin,
	            10.9,adhocymax)
      dl3.SetLineWidth(linewidth); dl3.SetLineColor(linecolor)
      dl3.SetLineStyle(linestyle)
      dl3.Draw()
      dl4 = ROOT.TLine(16.0,adhocymin,
	            16.0,adhocymaxdl4)
      dl4.SetLineWidth(linewidth); dl4.SetLineColor(linecolor)
      dl4.SetLineStyle(linestyle)
      dl4.Draw()
      tinfo = ROOT.TLatex()
      tinfo.SetTextFont(10*infofont+3)
      tinfo.SetTextSize(infosize)
      tinfo.SetTextColor(linecolor)
      tinfo.DrawLatexNDC(0.27,0.55,"PXL1")
      tinfo.DrawLatexNDC(0.43,0.50,"PXL2")
      tinfo.DrawLatexNDC(0.60,0.40,"PXL3")
      tinfo.DrawLatexNDC(0.80,0.30,"PXL4")

    ### Create pad for ratio plots
    pad2.cd()
    pad2.SetLeftMargin(0.15)
    pad2.SetBottomMargin(0.4)
    pad2.SetTopMargin(0.01)
    pad2.SetTicks(1,1)
    pad2.SetFrameLineWidth(2)
    pad2.Draw()

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
    histratio2.SetFillColorAlpha(statcolor, stattransparency)
    histratio2.SetFillStyle(statfillstyle)
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
    #histratio2.SetMinimum(0.88)
    #histratio2.SetMaximum(1.12)
    histratio2.SetMinimum(0.4)
    histratio2.SetMaximum(1.6)
    yax = histratio2.GetYaxis()
    yax.SetNdivisions(4,5,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle('Data/Pred.')
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
    c1.SaveAs(outfile.split('.')[0]+'.pdf')

    ## write ratio to txt file if requested
    if dotxt:
	txtoutfile = outfile.split('.')[0]+'_ratio.txt'
	ratiototxtfile(hist0,mchistsum,txtoutfile)

if __name__=='__main__':

    sys.stderr.write('###starting###\n')
    # configure input parameters (hard-coded)
    histfile = '/storage_mnt/storage/user/llambrec/K0sAnalysis/histograms/'
    histfile += 'test.root'
    # (file to read histograms)
    outfile = '/storage_mnt/storage/user/llambrec/K0sAnalysis/histograms/'
    outfile += 'test.png'
    # (file to save figure to)
    title = r'K^{0}_{S} vertex radial distance'
    xaxistitle = 'radial distance (cm)' # set x axis title
    yaxistitle = 'number of vertices' # set y axis title of upper graph
    # optional arguments
    logy = True
    doextrainfos = False
    extrainfos = []
    do2016pixel = False
    do20172018pixel = False

    # configure input parameters (from command line for submission script)
    cmdargs = sys.argv[1:]
    if len(cmdargs)>0:
        coreargs = {'histfile':False, 'histtitle':False, 'xaxistitle':False,
                    'yaxistitle':False, 'outfile':False }
        for arg in cmdargs:
            argname,argval = arg.split('=')
            # required arguments
            if argname == 'histfile': histfile = argval; coreargs['histfile']=True
            elif argname == 'histtitle': title = argval; coreargs['histtitle']=True
            elif argname == 'xaxistitle': xaxistitle = argval; coreargs['xaxistitle']=True
            elif argname == 'yaxistitle': yaxistitle = argval; coreargs['yaxistitle']=True
            elif argname == 'outfile': outfile = argval; coreargs['outfile']=True
            # optional arguments
            elif argname == 'logy': logy = (argval.lower()=='true')
            elif argname == 'doextrainfos': doextrainfos = (argval.lower()=='true')
            elif argname == 'extrainfos': extrainfos = argval
            elif argname == 'do2016pixel': do2016pixel = (argval.lower()=='true')
            elif argname == 'do20172018pixel': do20172018pixel = (argval.lower()=='true')
        if False in coreargs.values():
            print('### ERROR ###: the following core arguments were not defined:')
            for key in coreargs.keys():
                if(coreargs[key]==False): print(key)
            sys.exit()

    indict = loadobjects(histfile)
    #indict = loadobjects_old(histfile) # WARNING: temporarily changed to loadobjects_old!
    
    # configure other parameters based on input
    varname = indict['varname']
    normrange = None
    normvariable = None
    if indict['normalization'] == 3:
      normrange = indict['normrange']
      normvariable = indict['normvariable']
      if varname!=normvariable: normrange = None # disable drawing norm range if variables dont match
    lumistr = ''
    if indict['lumi'] > 0: 
	lumistr = '{0:.3g}'.format(indict['lumi']/1000.)+' fb^{-1} (13 TeV)'
    colorlist = []
    for hist in indict['mchistlist']:
	if '2016' in hist.GetTitle():
          if '2016B' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016C' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016D' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016E' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016F' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016PreVFP' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016G' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          elif '2016H' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          elif '2016PostVFP' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          else: colorlist.append(ROOT.kAzure-4)
	elif '2017' in hist.GetTitle(): colorlist.append(ROOT.kAzure+6)
	elif '2018' in hist.GetTitle(): colorlist.append(ROOT.kViolet)
	else:
	    print('WARNING: histogram title could not be associated with a color')
	    colorlist.append(ROOT.kBlack)

    # make extra info
    if doextrainfos:
      if len(extrainfos)==0:
        extrainfos = []
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
    
    plotmcvsdata(indict['mchistlist'],indict['datahistlist'],outfile,
		    xaxistitle=xaxistitle,yaxistitle=yaxistitle,title=title,
		    colorlist=colorlist,
		    logy=logy,drawrange=normrange,
		    lumistr=lumistr,dotxt=False,
                    extrainfos=extrainfos, infosize=15, infoleft=0.6, infotop=0.65,
                    do2016pixel=do2016pixel, do20172018pixel=do20172018pixel )

    sys.stderr.write('###done###\n')
