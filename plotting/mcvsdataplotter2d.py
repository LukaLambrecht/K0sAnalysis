###################################
# Making sim vs. data plots in 2D #
###################################

import os
import sys
import json
import argparse
import ROOT
import numpy as np
from array import array
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import plotting.plottools as pt
import tools.histtools as ht
from mcvsdataplotter import loadobjects, get_total


def plotmcvsdata2d( mchist, datahist, outfile,
                    simsyst=None, datasyst=None,
                    xaxtitle=None, yaxtitle=None, title=None,
                    xaxtitleoffset=None, yaxtitleoffset=None,
                    axtitlesize=None, titlesize=None,
                    p1topmargin=None, p1bottommargin=None,
                    p1leftmargin=None, p1rightmargin=None,
                    drawbox=None, lumistr='', extracmstext='',
                    writebincontents=True,
                    binmode='default',
                    outrootfile=None,
                    extrainfos=None, infoleft=None, infotop=None ):
    # binmode: 'default', 'category' or 'equal'.
    # outrootfile: name of the root file to which the histogram corresponding to the figure 
    #              will be written (if None, no output root file is created, only the figure).

    ### Create canvas and set parameters
    pt.setTDRstyle()
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(1200,600)
    pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
    pad1.Draw()
    titlefont = 4
    if titlesize is None: titlesize = 25
    labelfont = 4; labelsize = 25
    axtitlefont = 4
    if axtitlesize is None: axtitlesize = 25
    infofont = 4; infosize = 20
    legendfont = 4; legendsize = 20
    if p1bottommargin is None: p1bottommargin = 0.15
    if p1topmargin is None: p1topmargin = 1.
    if p1leftmargin is None: p1leftmargin = 0.1
    if p1rightmargin is None: p1rightmargin = 0.15
    if xaxtitleoffset is None: xaxtitleoffset = 1.2
    if yaxtitleoffset is None: yaxtitleoffset = 1.2
    # extra info box parameters
    if infoleft is None: infoleft = p1leftmargin+0.05
    if infotop is None: infotop = 1-p1topmargin-0.1

    ### get bins and related properties
    nxbins = mchist.GetNbinsX()
    xbins = mchist.GetXaxis().GetXbins()
    nybins = mchist.GetNbinsY()
    ybins = mchist.GetYaxis().GetXbins()

    ### Create pad and containers summed histograms
    pad1.cd()
    pad1.SetBottomMargin(p1bottommargin)
    pad1.SetLeftMargin(p1leftmargin)
    pad1.SetTopMargin(p1topmargin)
    pad1.SetRightMargin(p1rightmargin)
    pad1.SetTicks(1,1)

    ### Add data histograms
    if datahist is None:
        datahist = mchist.Clone()
        datahist.Reset()
    datahist.SetStats(False)
    datahist.SetTitle("")

    ### create ratio histogram and get arrays of values and errors
    histratio = datahist.Clone()
    histratio.SetName('histratio')
    histratio.SetTitle('data to simulation ratio')
    histratio.Divide(mchist)
    systratio = None
    if( simsyst is not None or datasyst is not None ):
        if simsyst is None: simsyst = mchist.Clone()
        if datasyst is None: datasyst = datahist.Clone()
        systratio = datasyst.Clone()
        systratio.SetName('systratio')
        systratio.Divide(simsyst)
    # note: default error calculation of Divide is simple relative quadratic addition.
    #       this can be modified in the manual calculation below if required.
    vals = []
    stat = []
    syst = []
    for i in range(nxbins):
        vals.append([])
        stat.append([])
        syst.append([])
        for j in range(nybins):
            ndata = datahist.GetBinContent(i+1,j+1)
            nmc = mchist.GetBinContent(i+1,j+1)
            statdata = datahist.GetBinError(i+1,j+1)
            statmc = mchist.GetBinError(i+1,j+1)
            if ndata<1 or nmc<1e-12:
                vals[i].append(0.)
                stat[i].append(0.)
                syst[i].append(0.)
                histratio.SetBinContent(i+1,j+1,0.)
                histratio.SetBinError(i+1,j+1,0.)
            # option 1: take default Divide behaviour
            else:
                vals[i].append(histratio.GetBinContent(i+1,j+1))
                stat[i].append(histratio.GetBinError(i+1,j+1))
                if systratio is not None: syst[i].append(systratio.GetBinError(i+1,j+1))
                else: syst[i].append(0.)
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
        if systratio is not None: systratio.Write()
        f.Close()

    ### optional: redefine histogram as category histogram
    # to do: extend to systematic ratio (but not used for now)
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
        histratio, xbins, ybins = ht.make_equal_width_2d(histratio)
        if drawbox is not None:
            drawbox[0] = ht.transform_to_equal_width(drawbox[0],origxax)
            drawbox[2] = ht.transform_to_equal_width(drawbox[2],origxax)
            drawbox[1] = ht.transform_to_equal_width(drawbox[1],origyax)
            drawbox[3] = ht.transform_to_equal_width(drawbox[3],origyax)

    ### get min and max
    xlow = mchist.GetXaxis().GetXmin()
    xhigh = mchist.GetXaxis().GetXmax()
    ylow = histratio.GetYaxis().GetXmin()
    yhigh = histratio.GetYaxis().GetXmax()

    ### plotting and layout
    # X-axis layout
    xax = histratio.GetXaxis()
    xax.SetLabelFont(10*labelfont+3)
    xax.SetLabelSize(labelsize)
    if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(xaxtitleoffset)
    # Y-axis layout
    yax = histratio.GetYaxis()
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    if yaxtitle is not None:
        yax.SetTitle(yaxtitle)
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(yaxtitleoffset)
    # Z-axis layour
    histratio.SetMinimum(0.8)
    histratio.SetMaximum(1.2)
    ROOT.gStyle.SetPalette(ROOT.kBird)
    zax = histratio.GetZaxis()
    zax.SetLabelFont(10*labelfont+3)
    zax.SetLabelSize(labelsize)
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
                statstr = r'#pm' + '{0:.2f}'.format(stat[i][j])
                syststr = r'#pm' + '{0:.2f}'.format(syst[i][j]) if systratio is not None else ''
                txt = '#splitline{'+valstr+'}{#splitline{'+statstr+'}{'+syststr+'}}'
                tvals.DrawLatex(xcenter, ycenter, txt)

    # Write extra info
    fmtstr = 'Format:   #splitline{nominal}{#splitline{#pm stat. unc.}{#pm syst. unc.}}'
    if extrainfos is None: extrainfos = [fmtstr]
    else: extrainfos.append(fmtstr)
    if extrainfos is not None:
        tinfo = ROOT.TLatex()
        tinfo.SetTextFont(10*infofont+3)
        tinfo.SetTextSize(infosize)
        for i,info in enumerate(extrainfos):
            vspace = 0.07*(float(infosize)/20)
            tinfo.DrawLatexNDC(infoleft,infotop-(i+1)*vspace, info)
                
    # Write luminosity
    pt.drawLumi( pad1, extratext=extracmstext,
                        cms_in_grid=False,
                        cmstext_size_factor=0.5,
                        cmstext_offset=0.01,
                        lumitext=lumistr,
                        lumitext_size_factor=0.4,
                        lumitext_offset=0.02)

    c1.Update()
    c1.SaveAs(outfile)


if __name__=='__main__':

    sys.stderr.write('### starting ###\n')

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
    parser.add_argument('--outrootfile', default=None)
    parser.add_argument('--extralumitext', default=None)
    parser.add_argument('--extracmstext', default=None)
    parser.add_argument('--doextrainfos', default=False, action='store_true')
    parser.add_argument('--extrainfos', default=None)
    args = parser.parse_args()

    # load objects from input file
    indict = loadobjects(args.histfile)

    # calculate total systematic error band on simulation
    # (and potentially on data, e.g. background fit uncertainties)
    (simhist, simsyst) = get_total(indict['mchists'])
    (datahist, datasyst) = get_total(indict['datahists'])

    # configure other parameters based on input
    xvarname = indict['xvarname']
    yvarname = indict['yvarname']
    normvariable = None
    if indict['normalization'] == 'range':
      normrange = indict['normrange']
      normvariable = indict['normvariable']
      #if varname!=normvariable: normrange = None # disable drawing norm range if variables dont match
    lumistr = ''
    if indict['lumi'] > 0:
        lumistr = '{0:.3g}'.format(indict['lumi']/1000.)+' fb^{-1} (13 TeV)'
    if args.extralumitext is not None:
        lumistr += ' ' + args.extralumitext
    extracmstext = ''
    if args.extracmstext is not None: extracmstext = args.extracmstext

    # make extra info
    infoleft = None
    infotop = None
    p1rightmargin = None
    extrainfos = []
    if args.doextrainfos:
      p1rightmargin = 0.35
      infoleft = 0.77
      infotop = 0.7
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

    plotmcvsdata2d( simhist, datahist, args.outputfile,
                    simsyst=simsyst, datasyst=datasyst,
                    xaxtitle=args.xaxtitle, yaxtitle=args.yaxtitle, title=args.title,
                    lumistr=lumistr, extracmstext=extracmstext, 
                    binmode='equal', outrootfile=args.outrootfile,
                    extrainfos=extrainfos, infoleft=infoleft, infotop=infotop,
                    p1rightmargin=p1rightmargin )

    sys.stderr.write('### done ###\n')
