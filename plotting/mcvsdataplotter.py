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


def loadobjects(histfile):
    ### load all objects, i.e. histograms and other relevant info
    # note: depends heavily on convention for input files
    #       (usually the output of analysis/mcvsdata_fill.py),
    #       modify as needed.
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
    # load histograms
    histlist = ht.loadallhistograms(histfile, suppress_warnings=True)
    mchists = {}
    datahists = {}
    for hist in histlist:
        name = hist.GetName()
        if name.endswith('_up'):
            name = name.replace('_up','')
            [label, systematic] = name.rsplit('_',1)
            stype = 'up'
        elif name.endswith('_down'):
            name = name.replace('_down','')
            [label, systematic] = name.rsplit('_',1)
            stype = 'down'
        elif name.endswith('_nominal'):
            name = name.replace('_nominal','')
            label = name
            systematic = 'nominal'
        else:
            msg = 'WARNING: histogram type not recognized'
            msg += ' for histogram with name "{}";'.format(hist.GetName())
            msg += ' skipping it...'
            print(msg)
            continue
        if 'sim' in hist.GetName() or 'Sim' in hist.GetName(): hists = mchists
        elif 'data' in hist.GetName() or 'Data' in hist.GetName(): hists = datahists
        else:
            msg = 'WARNING: histogram type not recognized'
            msg += ' for histogram with name "{}";'.format(hist.GetName())
            msg += ' skipping it...'
            print(msg)
            continue
        if not label in hists.keys(): hists[label] = {}
        if not systematic in hists[label].keys(): hists[label][systematic] = {}
        if systematic=='nominal': hists[label]['nominal'] = hist
        elif stype=='up': hists[label][systematic]['up'] = hist
        elif stype=='down': hists[label][systematic]['down'] = hist
        else: raise Exception('ERROR: stype {} not recognized.'.format(stype))
    mchistlist = [el['nominal'] for key,el in mchists.items()]
    datahistlist = [el['nominal'] for key,el in datahists.items()]
    print('found {} data files and {} simulation files.'.format(
          len(datahistlist),len(mchistlist)))
    res['mchistlist'] = mchistlist
    res['datahistlist'] = datahistlist
    res['mchists'] = mchists
    res['datahists'] = datahists
    # printouts of histogram dicts for testing and debugging
    verbose = True
    if verbose:
        print('INFO in mcvsdataplotter.py / loadobjects:')
        print('loaded following histogram structure:')
        for dtype, ddict in [('Data', datahists), ('Sim', mchists)]:
            print('  {}:'.format(dtype))
            for label, process in ddict.items():
                print('    {}:'.format(label))
                for systematic,val in process.items():
                    valtxt = ''
                    if isinstance(val, ROOT.TH1): valtxt = 'ok'
                    if isinstance(val, dict): valtxt = sorted(list(val.keys()))
                    print('      - {}: {}'.format(systematic, valtxt))
    # get test histogram for variable and bin extraction
    testhist = None
    if len(mchistlist)>0: testhist = mchistlist[0]
    elif len(datahistlist)>0: testhist = datahistlist[0]
    if testhist is None: return res
    histdim = 1
    if testhist.GetNbinsY() > 1: histdim = 2
    # get bins
    if histdim==1:
        bins = testhist.GetXaxis().GetXbins()
        res['bins'] = bins
    elif histdim==2:
        xbins = testhist.GetXaxis().GetXbins()
        ybins = testhist.GetYaxis().GetXbins()
        res['xbins'] = xbins
        res['ybins'] = ybins
    # load meta-info
    if histdim==1:
        varname = f.Get('variable').GetTitle()
        res['varname'] = varname
    elif histdim==2:
        xvarname = f.Get('variable').GetTitle()
        res['xvarname'] = xvarname
        yvarname = f.Get('yvariable').GetTitle()
        res['yvarname'] = yvarname
    return res

def get_total(histdict):
    ### get sum of nominal histograms and total systematic
    # note: the total systematic is calculated as the root-sum-squared
    #       of all systematic histograms;
    #       this is good enough for plotting,
    #       but does not take into account correlations.
    labels = sorted(list(histdict.keys()))
    nominal = histdict[labels[0]]['nominal'].Clone()
    nominal.Reset()
    systematic = nominal.Clone()
    for label in labels:
        process = histdict[label]
        thisnominal = process['nominal']
        thisvars = []
        for syst in process.keys():
            if syst=='nominal': continue
            upvar = process[syst]['up']
            downvar = process[syst]['down']
            maxvar = ht.binperbinmaxvar([upvar, downvar], thisnominal)
            thisvars.append(maxvar)
        thissystematic = ht.rootsumsquare(thisvars)
        for i in range(0, thisnominal.GetNbinsX()+2):
            if isinstance(thisnominal, ROOT.TH2):
                for j in range(0, thisnominal.GetNbinsY()+2):
                    thissystematic.SetBinError(i, j, thissystematic.GetBinContent(i,j))
                    thissystematic.SetBinContent(i, j, thisnominal.GetBinContent(i,j))
            else:
                thissystematic.SetBinError(i, thissystematic.GetBinContent(i))
                thissystematic.SetBinContent(i, thisnominal.GetBinContent(i))
        nominal.Add(thisnominal)
        systematic.Add(thissystematic)
    return (nominal, systematic)

def ratiototxt(histnum, histdenom, outfilename):
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
                mcsysthistlist=None, datasysthistlist=None,
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
    staterrcolor = ROOT.kOrange
    toterrcolor = ROOT.kOrange - 4
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
    if legendlen > 30: legendbox_left = 0.35
    elif legendlen > 15: legendbox_left = 0.45
    else: legendbox_left = 0.6
    #elif legendlen < 30: legendbox_left = 0.6
    #else: legendbox_left = 0.35 + (50-legendlen)/30*0.25
    leg = ROOT.TLegend(legendbox_left, 0.65, 0.95, 0.85)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetNColumns(2)
    leg.SetBorderSize(0)

    ### Add MC histograms
    # sum and stack nominal histograms
    # (including statistical uncertainties)
    for i,hist in enumerate(mchistlist):
        hist.SetStats(False)
        hist.SetLineColor(ROOT.kBlack)
        hist.SetLineWidth(1)
        hist.SetMarkerSize(0)
        hist.SetFillColor(colorlist[i])
        hist.SetFillStyle(1001)
        mcstack.Add(hist)
        mchistsum.Add(hist)
    # handle systematic uncertainties (if provided)
    mcerrhistsum = None
    if mcsysthistlist is not None and len(mcsysthistlist)>0:
        mcerrhistsum = mchistsum.Clone()
        mcerrhistsum.Reset()
        for i,hist in enumerate(mcsysthistlist): mcerrhistsum.Add(hist)
        for i in range(1, mcerrhistsum.GetNbinsX()+1):
            toterror = np.sqrt( mcerrhistsum.GetBinError(i)**2 + mchistsum.GetBinError(i)**2 )
            mcerrhistsum.SetBinError(i, toterror)

    ### Add data histograms
    drawdata = True
    if(len(datahistlist)>0):
        # sum nominal histograms (including statistical uncertainties)
        datahistsum = datahistlist[0]
        for i,hist in enumerate(datahistlist[1:]): datahistsum.Add(hist)
        # handle systematic uncertainties (if provided)
        # (just add it quadratically to the statistical uncertainty)
        if datasysthistlist is not None and len(datasysthistlist)>0:
            datasysthist = datasysthistlist[0]
            for i,hist in enumerate(datasysthistlist[1:]): datasysthist.Add(hist)
            for i in range(1, datahistsum.GetNbinsX()+1):
              toterror = np.sqrt( datahistsum.GetBinError(i)**2 + datasysthist.GetBinError(i)**2 )
              datahistsum.SetBinError(i, toterror)
        datahistsum.SetMarkerStyle(20)
        datahistsum.SetMarkerSize(0.9)
    else:
        datahistsum = mchistlist[0].Clone()
        datahistsum.Reset()
        drawdata = False

    ### Stacked histogram layout
    mcstack.Draw("HIST")
    # X-axis layout
    xax = mcstack.GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelSize(0)
    # Y-axis layout
    (ymin,ymax) = getminmax(datahistsum,mchistsum,yaxlog=logy,margin=True)
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

    ### Draw uncertainties on the prediction
    # total uncertainties
    if mcerrhistsum is not None:
        mcerrhistsum.SetStats(False)
        mcerrhistsum.SetLineWidth(0)
        mcerrhistsum.SetFillColorAlpha(toterrcolor, stattransparency/2.)
        mcerrhistsum.SetFillStyle(statfillstyle)
        mcerrhistsum.Draw("SAME E2")
    # statistical uncertainties
    mchistsum.SetStats(False)
    mchistsum.SetLineWidth(0)
    mchistsum.SetFillColorAlpha(staterrcolor, stattransparency)
    mchistsum.SetFillStyle(statfillstyle)
    mchistsum.Draw("SAME E2")

    ### Fill legend entries
    legentries = []
    for hist in mchistlist:
        legentry = hist.GetTitle().replace('_nominal','')
        legentries.append({'hist': hist, 'label': legentry, 'options': 'f'})
    legentries.append({'hist': mchistsum, 'label': 'Stat. uncertainty', 'options': 'f'})
    if mcerrhistsum is not None:
        legentries.append({'hist': mcerrhistsum, 'label': 'Tot. uncertainty', 'options': 'f'})
    if drawdata:
        legentries.append({'hist': datahistsum, 'label': 'Data', 'options': 'ep'})
    # normal (row-first) filling:
    #for l in legentries: leg.AddEntry(l['hist'], l['label'], l['options'])
    # trick for column-first filling:
    indices = []
    for i in range(len(legentries)):
        if i%2==0: indices.append(int(i/2))
        else: indices.append(int((len(legentries)+1)/2) + int((i-1)/2))
    for i in indices:
        l = legentries[i]
        leg.AddEntry(l['hist'], l['label'], l['options'])

    ### Draw data histogram
    if drawdata: datahistsum.Draw("SAME E0")

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
    #        print(datahistsum.GetBinContent(i))
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
    statratio = mchistsum.Clone()
    for i in range(1, statratio.GetSize()-1):
        denom = mchistsum.GetBinContent(i)
        if not denom==0: # if zero, do nothing
            statratio.SetBinContent(i,statratio.GetBinContent(i)/denom)
            statratio.SetBinError(i,statratio.GetBinError(i)/denom)
    statratio.SetStats(False)
    statratio.SetTitle("")
    statratio.SetLineWidth(0)
    statratio.SetFillColorAlpha(staterrcolor, stattransparency)
    statratio.SetFillStyle(statfillstyle)
    statratio.Draw("E2")
    # do systematic uncertainties
    if mcerrhistsum is not None:
        errratio = mcerrhistsum.Clone()
        for i in range(1, errratio.GetSize()-1):
            denom = mcerrhistsum.GetBinContent(i)
            if not denom==0: # if zero, do nothing
                errratio.SetBinContent(i,errratio.GetBinContent(i)/denom)
                errratio.SetBinError(i,errratio.GetBinError(i)/denom)
        errratio.SetStats(False)
        errratio.SetTitle("")
        errratio.SetLineWidth(0)
        errratio.SetFillColorAlpha(toterrcolor, stattransparency/2.)
        errratio.SetFillStyle(statfillstyle)
        errratio.Draw("SAME E2")
    # X-axis layout
    xax = statratio.GetXaxis()
    xax.SetNdivisions(10,4,0,ROOT.kTRUE)
    xax.SetLabelFont(10*labelfont+3)
    xax.SetLabelSize(labelsize)
    if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(3.)
    # Y-axis layout
    #statratio.SetMinimum(0.88)
    #statratio.SetMaximum(1.12)
    statratio.SetMinimum(0.4)
    statratio.SetMaximum(1.6)
    yax = statratio.GetYaxis()
    yax.SetNdivisions(4,5,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle('Data/Sim.')
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.5)
    statratio.Draw("E2")
    if mcerrhistsum is not None: errratio.Draw("SAME E2")

    ### Divide data by simulation
    histratio = datahistsum.Clone()
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
            lines.append(ROOT.TLine(xval,statratio.GetMinimum(),
                                    xval,statratio.GetMaximum()))
            lines[-1].SetLineStyle(9)
            lines[-1].Draw()

    c1.Update()
    c1.SaveAs(outfile.split('.')[0]+'.png')
    c1.SaveAs(outfile.split('.')[0]+'.pdf')

    ## write ratio to txt file if requested
    if dotxt:
        txtoutfile = outfile.split('.')[0]+'_ratio.txt'
        ratiototxtfile(datahistsum,mchistsum,txtoutfile)

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

    # calculate total systematic error band on simulation
    # (and potentially on data, e.g. background fit uncertainties)
    (_, simsyst) = get_total(indict['mchists'])
    (_, datasyst) = get_total(indict['datahists'])
    
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
                    mcsysthistlist=[simsyst], datasysthistlist=[datasyst],
                    xaxtitle=args.xaxtitle, yaxtitle=args.yaxtitle, title=args.title,
                    colorlist=colorlist,
                    logy=args.logy, drawrange=normrange,
                    lumistr=lumistr, extracmstext=extracmstext, dotxt=False,
                    extrainfos=extrainfos, infosize=15, infoleft=0.6, infotop=0.65,
                    do2016pixel=args.do2016pixel, do20172018pixel=args.do20172018pixel )

    sys.stderr.write('###done###\n')
