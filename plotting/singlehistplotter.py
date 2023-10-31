#####################################
# Plot a single ROOT TH1D histogram #
#####################################

import ROOT
import sys
import os
import plottools as pt

def plotsinglehistogram(hist, figname, 
                title=None, xaxtitle=None, yaxtitle=None, 
	        label=None, color=None, logy=False, drawoptions='',
	        do_cms_text=False, lumitext='', extralumitext='',
	        topmargin=None, bottommargin=None,
	        leftmargin=None, rightmargin=None,
	        xaxlabelfont=None, xaxlabelsize=None,
		yaxmin=None, yaxmax=None,
	        writebincontent=False, bincontentfont=None, 
	        bincontentsize=None, bincontentfmt=None,
		extrainfos=[], infosize=None, infoleft=None, infotop=None ):
    ### drawing a single histogram
    # - label: string for the legend entry for this histogram.
    #	note: if label is 'auto', the implicit title of the TH1 will be used.
    # - drawoptions: string passed to TH1.Draw.
    #   use "HIST" for histogram style (no error bars)
    #       "E" for error bars
    #       "X0" to suppress horizontal error bars
    #       see https://root.cern/doc/master/classTHistPainter.html for a full list of options
    # - extrainfos is a list of strings with extra info to display
    # - infosize: font size of extra info
    # - infoleft: left border of extra info text (default leftmargin + 0.05)
    # - infotop: top border of extra info text (default 1 - topmargin - 0.1)

    pt.setTDRstyle()
    ROOT.gROOT.SetBatch(ROOT.kTRUE)

    ### parse arguments
    if color is None: color = ROOT.kAzure-4
    
    ### initializations
    # make canvas
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(600,600)
    pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
    pad1.SetTicks(1,1)
    pad1.SetFrameLineWidth(2)
    pad1.SetGrid()
    pad1.Draw()
    pad1.cd()
    # set fonts and text sizes
    titlefont = 4; titlesize = 22
    if xaxlabelfont is None: xaxlabelfont = 4 
    if xaxlabelsize is None: xaxlabelsize = 22
    yaxlabelfont = 4; yaxlabelsize = 22
    axtitlefont = 4; axtitlesize = 22
    legendfont = 4
    if bincontentfont is None: bincontentfont = 4
    if bincontentsize is None: bincontentsize = 12
    if bincontentfmt is None: bincontentfmt = '{:.3f}'
    infofont = 4
    if infosize is None: infosize = 20
    # margins
    if leftmargin is None: leftmargin = 0.15
    if rightmargin is None: rightmargin = 0.05
    if topmargin is None: topmargin = 0.05
    if bottommargin is None: bottommargin = 0.15
    pad1.SetBottomMargin(bottommargin)
    pad1.SetLeftMargin(leftmargin)
    pad1.SetRightMargin(rightmargin)
    pad1.SetTopMargin(topmargin)
    # extra info box parameters
    if infoleft is None: infoleft = leftmargin+0.05
    if infotop is None: infotop = 1-topmargin-0.1
    # legendbox
    pentryheight = 0.05
    plegendbox = ([leftmargin+0.3,1-topmargin-pentryheight,
                    1-rightmargin-0.03,1-topmargin-0.03])

    ### set histogram properties
    hist.SetLineColor(color)
    hist.SetLineWidth(3)
    hist.SetMarkerSize(0)
    hist.Sumw2()

    ### make the legend
    if label is not None:
	leg = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
	leg.SetTextFont(10*legendfont+3)
	leg.SetFillColor(ROOT.kWhite)
	leg.SetBorderSize(1)
	if label=='auto': label = hist.GetTitle()
	leg.AddEntry(hist,label,"l")
    hist.Draw(drawoptions)

    ### X-axis layout
    xax = hist.GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelFont(10*xaxlabelfont+3)
    xax.SetLabelSize(xaxlabelsize)
    if xaxtitle is not None: 
	xax.SetTitle(xaxtitle)
	xax.SetTitleFont(10*axtitlefont+3)
	xax.SetTitleSize(axtitlesize)
	xax.SetTitleOffset(1.2)
    ### Y-axis layout
    if not logy:
	hist.SetMaximum(hist.GetMaximum()*1.2)
	hist.SetMinimum(0.)
    else:
	c1.SetLogy()
	hist.SetMaximum(hist.GetMaximum()*10)
	hist.SetMinimum(hist.GetMaximum()/1e7)
    if yaxmin is not None: hist.SetMinimum(yaxmin)
    if yaxmax is not None: hist.SetMaximum(yaxmax)
    yax = hist.GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*yaxlabelfont+3)
    yax.SetLabelSize(yaxlabelsize)
    if yaxtitle is not None: 
	yax.SetTitle(yaxtitle)
	yax.SetTitleFont(10*axtitlefont+3)
	yax.SetTitleSize(axtitlesize)
	yax.SetTitleOffset(2.)
    hist.Draw(drawoptions)

    # title
    # note: use of title is not recommended
    if title is not None:
    	ttitle = ROOT.TLatex()	
    	ttitle.SetTextFont(10*titlefont+3)
    	ttitle.SetTextSize(titlesize)
    	titlebox = (0.15,0.95)

    # draw all objects
    hist.Draw(drawoptions)
    ROOT.gPad.RedrawAxis()
    if do_cms_text: pt.drawLumi(pad1, cmstext_size_factor=0.4, 
                      extratext=extralumitext, lumitext=lumitext)
    if label is not None: leg.Draw("same")
    if title is not None: ttitle.DrawLatexNDC(titlebox[0],titlebox[1],title)

    # draw extra info
    tinfo = ROOT.TLatex()
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    for i,info in enumerate(extrainfos):
        vspace = 0.07*(float(infosize)/20)
        tinfo.DrawLatexNDC(infoleft,infotop-(i+1)*vspace, info)

    # write bin contents
    if writebincontent:
	bintext = ROOT.TLatex()
	bintext.SetTextAlign(21)
	bintext.SetTextFont(bincontentfont)
	bintext.SetTextSize(bincontentsize)
	for i in range(1, hist.GetNbinsX()+1):
	    xcoord  = hist.GetXaxis().GetBinCenter(i)
	    ycoord  = hist.GetBinContent(i)+hist.GetBinErrorUp(i)
	    printvalue = hist.GetBinContent(i)
	    bintext.DrawLatex(xcoord, ycoord+0.05, bincontentfmt.format(printvalue))

    c1.SaveAs(figname.split('.')[0]+'.png')
    c1.SaveAs(figname.split('.')[0]+'.eps')
    c1.SaveAs(figname.split('.')[0]+'.pdf')
