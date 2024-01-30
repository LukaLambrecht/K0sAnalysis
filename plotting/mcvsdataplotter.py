#############################
# Making sim vs. data plots #
#############################

import ROOT
import sys
import os
import numpy as np
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import plotting.plottools as pt
import tools.histtools as ht


def loadobjects(histfile, histdim=1):
    ### load all objects, i.e. histograms and other relevant info
    print('loading histograms')
    f = ROOT.TFile.Open(histfile)
    res = {}
    # load normalization
    normalization = f.Get("normalization").GetTitle()
    res['normalization'] = normalization
    if(normalization in ['range']):
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
        bkgmode = f.Get("bkgmode").GetTitle()
        res['bkgmode'] = bkgmode
    except:
        print('WARNING: could not find bkgmode value...')
        res['bkgmode'] = None
    # load treename
    try:
        treename = f.Get("treename").GetTitle()
        res['treename'] = treename
    except:
        print('WARNING: could not find treename value...')
        res['treename'] = None
    # load meta-info
    if histdim==1:
        varname = f.Get('variable').GetTitle()
        res['varname'] = varname
    elif histdim==2:
        xvarname = f.Get('variable').GetTitle()
        res['xvarname'] = xvarname
        yvarname = f.Get('yvariable').GetTitle()
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
                xaxtitle='', yaxtitle='', title='',
                colorlist=None,
                logy=False, drawrange=None,
                extracmstext='', lumistr='',
                dotxt=False,
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
    stattransparency = 0.9
    if colorlist is None: 
        colorlist = ([ROOT.kAzure-4,ROOT.kAzure+6,ROOT.kViolet,ROOT.kMagenta-9,
                      ROOT.kRed,ROOT.kPink-9,ROOT.kBlue+1])
        # (shades of blue and purple)
        #colorlist = ([ROOT.kGreen+1,ROOT.kCyan-7,ROOT.kAzure-4,ROOT.kViolet, 
        #         ROOT.kMagenta-9,ROOT.kRed-4,ROOT.kYellow])
        # (bright, high contrast)

    ### Create pad and containers for stacked and summed histograms
    pad1.cd()
    pad1.SetBottomMargin(0.02)
    pad1.SetLeftMargin(0.15)
    pad1.SetTopMargin(0.12)
    pad1.SetTicks(1,1)
    pad1.SetFrameLineWidth(2)
    pad1.Draw()
    mcstack = ROOT.THStack("mcstack","")
    mchistsum = mchistlist[0].Clone()
    mchistsum.Reset()
    mchistsum.SetStats(False)
    mchistsum.SetMarkerSize(0)

    ### Declare legend
    # find sum of number of characters in legend entries
    legendlen = 0
    for hist in mchistlist:
        legendlen += len(hist.GetTitle())
    if legendlen > 50: legendbox_left = 0.4
    elif legendlen < 10: legendbox_left = 0.6
    else: legendbox_left = 0.4 + (50-legendlen)/40*0.2
    leg = ROOT.TLegend(legendbox_left, 0.65, 0.95, 0.85)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetNColumns(2)
    leg.SetBorderSize(0)

    ### Add MC histograms
    for i,hist in enumerate(mchistlist):
        hist.SetStats(False)
        hist.SetLineColor(ROOT.kBlack)
        hist.SetLineWidth(1)
        hist.SetMarkerSize(0)
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
        drawdata = False

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
    if yaxtitle is not None:
        yax.SetTitle(yaxtitle)
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
    if drawdata: hist0.Draw("SAME E0")

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
    if title is not None:
        ttitle = ROOT.TLatex()        
        ttitle.SetTextFont(10*titlefont+3)
        ttitle.SetTextSize(titlesize)
        ttitle.DrawLatexNDC(0.15,0.92,title)
    pt.drawLumi(pad1, cmstext_size_factor=0.5,
                extratext=extracmstext, extratext_newline=True,
                lumitext=lumistr, lumitext_size_factor=0.4, lumitext_offset=0.02)

    ### Draw extra info
    tinfo = ROOT.TLatex()
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    for i,info in enumerate(extrainfos):
        vspace = 0.07*(float(infosize)/20)
        tinfo.DrawLatexNDC(infoleft,infotop-(i+1)*vspace, info)

    # temp for testing:
    #for i in range(1,mchistsum.GetNbinsX()):
    #        print('bin '+str(i)+' of '+str(mchistsum.GetNbinsX()))
    #        print(hist0.GetBinContent(i))
    #        print(mchistsum.GetBinContent(i))

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
      tinfo.DrawLatexNDC(0.33,0.52,"BPIX1")
      tinfo.DrawLatexNDC(0.45,0.47,"BPIX2")
      tinfo.DrawLatexNDC(0.57,0.42,"BPIX3")

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
      tinfo.DrawLatexNDC(0.27,0.55,"BPIX1")
      tinfo.DrawLatexNDC(0.43,0.50,"BPIX2")
      tinfo.DrawLatexNDC(0.60,0.40,"BPIX3")
      tinfo.DrawLatexNDC(0.80,0.30,"BPIX4")

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
    if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
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
    yax.SetTitle('Data/Sim.')
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
    histratio.Draw("SAME E0")
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

    # read command-line arguments
    parser = argparse.ArgumentParser( description = 'Plot histograms' )
    # general arguments
    parser.add_argument('-i', '--histfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', required=True)
    # arguments for axes formatting
    parser.add_argument('--title', default=None)
    parser.add_argument('--xaxtitle', default=None)
    parser.add_argument('--yaxtitle', default=None)
    # other arguments
    parser.add_argument('--logy', default=False, action='store_true')
    parser.add_argument('--extralumitext', default=None)
    parser.add_argument('--extracmstext', default=None)
    parser.add_argument('--doextrainfos', default=False, action='store_true')
    parser.add_argument('--extrainfos', default=None)
    parser.add_argument('--do2016pixel', default=False, action='store_true')
    parser.add_argument('--do20172018pixel', default=False, action='store_true')
    args = parser.parse_args()

    # load objects from input file   
    indict = loadobjects(args.histfile)
    
    # configure other parameters based on input
    varname = indict['varname']
    normrange = None
    normvariable = None
    if indict['normalization'] == 'range':
      normrange = indict['normrange']
      normvariable = indict['normvariable']
      if varname!=normvariable: normrange = None # disable drawing norm range if variables dont match
    lumistr = ''
    if indict['lumi'] > 0: 
        lumistr = '{0:.3g}'.format(indict['lumi']/1000.)+' fb^{-1} (13 TeV)'
    if args.extralumitext is not None:
        lumistr += ' ' + args.extralumitext
    extracmstext = ''
    if args.extracmstext is not None: extracmstext = args.extracmstext
    colorlist = []
    for hist in indict['mchistlist']:
        if '2016' in hist.GetTitle():
          if '2016B' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016C' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016D' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016E' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016F' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016PreVFP' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016 (old APV)' in hist.GetTitle(): colorlist.append(ROOT.kAzure-2)
          elif '2016G' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          elif '2016H' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          elif '2016PostVFP' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          elif '2016 (new APV)' in hist.GetTitle(): colorlist.append(ROOT.kAzure-9)
          else: colorlist.append(ROOT.kAzure-4)
        elif '2017' in hist.GetTitle(): colorlist.append(ROOT.kAzure+6)
        elif '2018' in hist.GetTitle(): colorlist.append(ROOT.kViolet)
        else:
            print('WARNING: histogram title could not be associated with a color')
            colorlist.append(ROOT.kBlack)

    # make extra info
    extrainfos = []
    if args.doextrainfos:
      if args.extrainfos is None:
        extrainfos = []
        if( indict['treename'] is not None ):
          treename = indict['treename']
          if treename=='laurelin':
            extrainfos.append('K^{0}_{S} candidates')
          elif treename=='telperion':
            extrainfos.append('#Lambda^{0} candidates')
          else:
            msg = 'WARNING: unrecognized treename {}'.format(treename)
            print(msg)
        if( indict['bkgmode'] is not None ):
          bkgmode = indict['bkgmode']
          if bkgmode.lower()=='none':
            extrainfos.append('Background not subtracted')
          elif bkgmode.lower()=='sideband':
            extrainfos.append('Background subtracted')
          else:
            msg = 'WARNING: unrecognized bkgmode {}'.format(bkgmode)
            print(msg)
        if( indict['normalization'] is not None ):
          norm = indict['normalization']
          if norm.lower()=='none':
            extrainfos.append('Not normalized')
          elif norm=='lumi':
            extrainfos.append('Normalized to luminosity')
          elif norm=='yield':
            extrainfos.append('Normalized to data')
          elif norm=='range':
            extrainfos.append('Normalized in range')
          elif norm=='eventyield':
            extrainfos.append('Normalized to data events')
          else:
            msg = 'WARNING: unrecognized normalization {}'.format(norm)
            print(msg)
      else:
        extrainfos = args.extrainfos.split(',')
    
    plotmcvsdata(indict['mchistlist'], indict['datahistlist'], args.outputfile,
                    xaxtitle=args.xaxtitle, yaxtitle=args.yaxtitle, title=args.title,
                    colorlist=colorlist,
                    logy=args.logy, drawrange=normrange,
                    lumistr=lumistr, extracmstext=extracmstext, dotxt=False,
                    extrainfos=extrainfos, infosize=15, infoleft=0.6, infotop=0.65,
                    do2016pixel=args.do2016pixel, do20172018pixel=args.do20172018pixel )

    sys.stderr.write('###done###\n')
