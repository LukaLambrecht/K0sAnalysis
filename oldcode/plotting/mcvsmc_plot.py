################################################################# 
# script to read variable from trees and make MC vs. data plots #
#################################################################
# This script reads a set of histograms created with mcvsdata_fill and does the actual plotting.
# Instead of comparing mc to data, mc is compared to mc (or data to data).
import ROOT
import sys

### Configure input parameters (hard-coded)
histfile = '/storage_mnt/storage/user/llambrec/Kshort/histogramsTEST/data18.root' # file to read histograms
outfile = '/storage_mnt/storage/user/llambrec/Kshort/histogramsTEST/data18_figure.png' # file to save figure to
title = r'K^{0}_{S} vertex radial distance'
xaxistitle = 'radial distance (cm)' # set x axis title
yaxistitle = 'number of vertices (normalized)' # set y axis title of upper graph

### Configure input parameters (from command line for submission script)
cmdargs = sys.argv[1:]
if len(cmdargs)>0:
    coreargs = {'histfile':True,'histtitle':True,'xaxistitle':True,'yaxistitle':True,'outfile':True}
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
        exit()

### Load histograms and variables
print('loading histograms')
f = ROOT.TFile.Open(histfile)
normalization = int(f.Get("normalization")[0])
if(normalization==3 or normalization==5):
    normrange = [f.Get("normrange")[0],f.Get("normrange")[1]]
if(normalization==1):
    lumi = f.Get("lumi")[0]
else:
    lumi = 0
mchistlist = []
i = 0
while True:
    if(f.Get("mchistn"+str(i)) == None):
        break
    mchistlist.append(f.Get("mchistn"+str(i)))
    i += 1
datahistlist = []
i = 0
while True:
    if(f.Get("datahistn"+str(i)) == None):
        break
    datahistlist.append(f.Get("datahistn"+str(i)))
    i += 1
print('found '+str(len(datahistlist))+' data files and '+str(len(mchistlist))+' simulation files.')
tothistlist = mchistlist + datahistlist

# redefine bins, now including under and overflow bins
nbins = tothistlist[0].GetNbinsX()
xlow = tothistlist[0].GetXaxis().GetXmin()
xhigh = tothistlist[0].GetXaxis().GetXmax()
bins = tothistlist[0].GetXaxis().GetXbins()

### Create canvas and set parameters
ROOT.gROOT.SetBatch(ROOT.kTRUE)
print('creating canvas...')
c1 = ROOT.TCanvas("c1","c1")
c1.SetCanvasSize(1200,1200)
pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
pad1.Draw()
#pad2 = ROOT.TPad("pad2","",0.,0.,1.,0.3)
#pad2.Draw()
titlefont = 6; titlesize = 50
labelfont = 5; labelsize = 40
axtitlefont = 5; axtitlesize = 40
infofont = 6; infosize = 30
legendfont = 4; legendsize = 30

### Create pad and containers for stacked and summed histograms
pad1.cd()
pad1.SetBottomMargin(0.15)
pad1.SetLeftMargin(0.15)
pad1.SetTopMargin(0.18)
pad1.SetTicks(1,1)

### Declare legend
leg = ROOT.TLegend(0.2,0.7,0.85,0.8)
leg.SetTextFont(10*legendfont+3)
leg.SetTextSize(legendsize)
leg.SetNColumns(3)
leg.SetBorderSize(0)

### Add MC histograms
clist7 = [ROOT.kRed+1,ROOT.kOrange+7,ROOT.kOrange,ROOT.kGreen+1,ROOT.kAzure+8,ROOT.kAzure-3,ROOT.kMagenta-4]
clist = [ROOT.kRed+1,ROOT.kMagenta-4,ROOT.kAzure-3]
if len(tothistlist)>3: clist = clist7
for i,hist in enumerate(tothistlist):
    hist.SetStats(False)
    hist.SetLineWidth(3)
    hist.SetLineColor(clist[i])
    #hist.SetFillColor(clist[i])
    #hist.SetFillStyle(3001)
    leg.AddEntry(hist,hist.GetTitle(),"lf")
    hist.SetTitle("")

### Histogram layout
hist0 = tothistlist[0]
hist0.Draw("HIST E1")
# X-axis layout
xax = hist0.GetXaxis()
xax.SetNdivisions(10,4,0,ROOT.kTRUE)
xax.SetLabelFont(10*labelfont+3)
xax.SetLabelSize(labelsize)
xax.SetTitle(xaxistitle)
xax.SetTitleFont(10*axtitlefont+3)
xax.SetTitleSize(axtitlesize)
xax.SetTitleOffset(1.2)
# Y-axis layout
# log scale
pad1.SetLogy()
hist0.SetMaximum(hist0.GetMaximum()*5)
hist0.SetMinimum(hist0.GetMinimum()/2)
# lin scale
#mcstack.SetMaximum(mcstack.GetMaximum()*1.5)
#mcstack.SetMinimum(0.)
yax = hist0.GetYaxis()
yax.SetMaxDigits(3)
yax.SetNdivisions(8,4,0,ROOT.kTRUE)
yax.SetLabelFont(10*labelfont+3)
yax.SetLabelSize(labelsize)
yax.SetTitle(yaxistitle)
yax.SetTitleFont(10*axtitlefont+3)
yax.SetTitleSize(axtitlesize)
yax.SetTitleOffset(1.5)

### Draw histograms
hist0.Draw("E1")
for hist in tothistlist[1:]:
    hist.Draw("SAME E1")

### Draw normalization range if needed
if(normalization==3 or normalization==5):
    vl1 = ROOT.TLine(normrange[0],hist0.GetMinimum(),
            normrange[0],hist0.GetMaximum())
    vl1.SetLineStyle(9)
    vl1.Draw()
    vl2 = ROOT.TLine(normrange[1],hist0.GetMinimum(),
            normrange[1],hist0.GetMaximum())
    vl2.SetLineStyle(9)
    vl2.Draw()

### Title and other information displays
leg.Draw()
# title
ttitle = ROOT.TLatex()
ttitle.SetTextFont(10*titlefont+3)
ttitle.SetTextSize(titlesize)
ttitle.DrawLatexNDC(0.15,0.9,title)
if lumi>0:
    # additional info
    tinfo = ROOT.TLatex()
    tinfo.SetTextFont(10*infofont+3)
    tinfo.SetTextSize(infosize)
    info = 'luminosity: {0:.1f}'.format(lumi/1000.)+r' fb^{-1} (13 TeV)'
    tinfo.DrawLatexNDC(0.55,0.85,info)

c1.Update()
c1.SaveAs(outfile)
