##################################################################
# function for plotting data together with is fit and simulation #
##################################################################
# similar to plotfit but with data and simulation in one plot and improved aesthetics
import ROOT
import sys
import os
sys.path.append('../tools')
import plottools as pt

def plot_fit_mcvsdata(datahist,simhist,figname,fitfunc=None,backfit=None,
			datalabel=None,simlabel=None,fitfunclabel=None,backfitlabel=None,
			paramdict=None,xaxtitle=None,yaxtitle=None,
			extrainfo='',lumitext=''):
    # args: - datahist and simhist are the histograms for data and simulation respectively
    #       - figname is the name of the output figure
    #       - fitfunc and backfit are two fitted functions 
    #         (typically total and background only, both can be None)
    #         note: up to now only one fitted function is supported,
    #               so only to data or only to simulation, not both
    #       - datalabel and simlabel are the legend entries for the histogram
    #       - paramdict is a dict containing names and values of fitted parameters of fitfunc
    #       - xaxtitle and yaxtitle are axis titles
    #       - extrainfo is a string with extra info to show, use '<<' to split lines
    #       - lumitext is the luminosity string to display in the header
    ROOT.gROOT.SetBatch(ROOT.kTRUE);
    pt.setTDRstyle()

    # initialization of canvas
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(800,800)
    #c1.SetGrid()
    titlefont = 4; titlesize = 30
    labelfont = 4; labelsize = 30
    axtitlefont = 4; axtitlesize = 35
    infofont = 4; infosize = 25
    legendfont = 4; legendsize = 25
    c1.SetBottomMargin(0.1)
    c1.SetTopMargin(0.05)
    c1.SetLeftMargin(0.15)

    # other initializations
    if simlabel is None: label = 'Simulation'
    if datalabel is None: datalabel = 'Data'
    if fitfunclabel is None: fitfunclabel = 'Total fit'
    if backfitlabel is None: backfitlabel = 'Background fit'

    # legend
    leg = ROOT.TLegend(0.65,0.7,0.93,0.9)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetBorderSize(0)

    # draw data histogram
    datahist.SetStats(False)
    datahist.SetMarkerStyle(20)
    datahist.SetMarkerSize(1.3)
    datahist.Sumw2()
    leg.AddEntry(datahist,datalabel,"pe")
    datahist.Draw('e1 x0')

    # draw simulation histogram
    simhist.SetStats(False)
    simhist.SetLineColor(ROOT.kBlue)
    simhist.SetLineWidth(2)
    simhist.Sumw2()
    leg.AddEntry(simhist,simlabel,"le")

    # X-axis layout
    xax = datahist.GetXaxis()
    xax.SetNdivisions(10,4,0,ROOT.kTRUE)
    xax.SetLabelFont(10*labelfont+3)
    xax.SetLabelSize(labelsize)
    if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)

    # Y-axis layout
    datahist.SetMaximum(datahist.GetMaximum()*1.3)
    #datahist.SetMinimum(0.)
    # shift y-axis so labels do not overlap with x-axis
    datahist.SetMinimum(-datahist.GetMaximum()*0.03)
    yax = datahist.GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    if yaxtitle is not None:
        yax.SetTitle(yaxtitle)
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(1.5)
    ROOT.gPad.SetTicks(1,1)
    datahist.Draw('e1 x0')
    tinfo = ROOT.TLatex()

    # draw fitted function
    if backfit is not None:
        backfit.SetLineColor(ROOT.kGreen+3)
        backfit.SetLineWidth(3)
        backfit.SetLineStyle(ROOT.kDashed)
        leg.AddEntry(backfit,backfitlabel,'l')

    # draw fitted function
    if fitfunc is not None:
        fitfunc.SetLineColor(ROOT.kRed)
        fitfunc.SetLineWidth(3)
        leg.AddEntry(fitfunc,fitfunclabel,'l')

    # redraw objects in correct order
    datahist.Draw('e1 x0') # to make sure axes are correct
    simhist.Draw('same hist e1')
    if backfit is not None: backfit.Draw('same')
    if fitfunc is not None: fitfunc.Draw('same')
    datahist.Draw('same e1 x0')
    leg.Draw()

    # display additional info
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    if paramdict is not None:
	for i,key in enumerate(paramdict):
	    info = key+' : {0:.4E}'.format(paramdict[key])
	    tinfo.DrawLatexNDC(0.65,0.75-i*0.035,info)

    # display extra info
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    extrainfo = extrainfo.replace('HACK_KS','PDG K^{0}_{S} mass:<<    497.614 #pm 0.024 MeV')
    extrainfo = extrainfo.replace('HACK_LA','PDG #Lambda^{0} mass:<<    1115.683 #pm 0.006 MeV')
    extrainfo = extrainfo.replace('HACK_JP','PDG J/#Psi mass:<<    3096.900 #pm 0.006 MeV')
    infolist = extrainfo.split('<<')
    for i,info in enumerate(infolist):
        tinfo.DrawLatexNDC(0.2,0.8-i*0.035,info)

    # title
    pt.drawLumi(c1,cmstext_size_factor=1.0,extratext='', lumitext=lumitext)

    c1.Update()
    c1.SaveAs(figname)
    c1.Close()
