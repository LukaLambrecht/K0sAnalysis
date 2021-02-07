#################################################################
# Script to read variable from trees and make MC vs. data plots #
#################################################################
# This script reads a histogram created with mcvsdata_fillrdpt and does the actual plotting.
import ROOT
import numpy as np
import sys
import json
from array import array

### Configure input parameters
#histfile = '~/Kshort/histograms/test2d.root' # file to read histograms
histfile = 'test.root'
title = r'K^{0}_{S} data to simulation ratio'
xaxistitle = 'radial distance (cm)' # set x axis title
yaxistitle = r'something else' # set y axis title
outfile = 'figure.png'
totallumi = 0 # total luminosity of data (and MC) sample (used in plot information)
			# make sure it is consistent with totallumi in mcvsdata_fill!
			# set to 0 to suppress displaying this value

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
if(normalization==3):
	xnormrange = [f.Get("normrange")[0],f.Get("normrange")[1]]
	ynormrange = [f.Get("normrange")[2],f.Get("normrange")[3]]
mchistlist = []
i = 0
while True:
	if(f.Get("mchistn"+str(i)) == None):
		break
	mchistlist.append(f.Get("mchistn"+str(i)))
	i += 1
datahistlist = []
print(i)
i = 0
while True:
	if(f.Get("datahistn"+str(i)) == None):
		break
	datahistlist.append(f.Get("datahistn"+str(i)))
	i += 1
print(i)
# get bins and related properties
nxbins = mchistlist[0].GetNbinsX()
xbins = mchistlist[0].GetXaxis().GetXbins()
xlow = mchistlist[0].GetXaxis().GetXmin()
xhigh = mchistlist[0].GetXaxis().GetXmax()
nybins = mchistlist[0].GetNbinsY()
ybins = mchistlist[0].GetYaxis().GetXbins()
ylow = mchistlist[0].GetYaxis().GetXmin()
yhigh = mchistlist[0].GetYaxis().GetXmax()
print(nxbins)
print(xbins)

### Create canvas and set parameters
ROOT.gROOT.SetBatch(ROOT.kTRUE)
print('creating canvas...')
c1 = ROOT.TCanvas("c1","c1")
c1.SetCanvasSize(2000,1200)
pad1 = ROOT.TPad("pad1","",0.,0.,1.,1.)
pad1.Draw()
titlefont = 6; titlesize = 60
labelfont = 5; labelsize = 50
axtitlefont = 5; axtitlesize = 50
infofont = 6; infosize = 25
legendfont = 4; legendsize = 30

### Create pad and containers summed histograms
pad1.cd()
pad1.SetBottomMargin(0.15)
pad1.SetLeftMargin(0.15)
pad1.SetTopMargin(0.15)
pad1.SetRightMargin(0.15)
pad1.SetTicks(1,1)
mchistsum = mchistlist[0].Clone()
mchistsum.Reset()
mchistsum.SetStats(False)

### Add MC histograms
for i,hist in enumerate(mchistlist):
	mchistsum.Add(hist)
	print('added simulation histogram '+str(i+1)+' of '+str(len(mchistlist)))

### Add data histograms
if(len(datahistlist)>0):
	hist0 = datahistlist[0]
	print('added data histogram 1 of '+str(len(datahistlist)))
	for i,hist in enumerate(datahistlist[1:]):
		hist0.Add(hist)
		print('added data histogram '+str(i)+' of '+str(len(datahistlist)))
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

### optional: redefine histogram as category histogram with equal bin size
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
xnormrangenew = []
ynormrangenew = []
for i in range(nxbins):
	bincenter = (xbins[i]+xbins[i+1])/2.
	if bincenter>xnormrange[0]:
		xnormrangenew.append(xbinsnew[i])
		for j in range(i+1,nxbins):
			bincenter = (xbins[j]+xbins[j+1])/2.
			if bincenter>xnormrange[1]:
				xnormrangenew.append(xbinsnew[j])
				break
			elif j==nxbins-1: xnormrangenew.append(xbinsnew[j+1])
		break
print(xnormrangenew)
for i in range(nybins):
        bincenter = (ybins[i]+ybins[i+1])/2.
        if bincenter>ynormrange[0]:
                ynormrangenew.append(ybinsnew[i])
                for j in range(i+1,nybins):
                        bincenter = (ybins[j]+ybins[j+1])/2.
                        if bincenter>ynormrange[1]:
                                ynormrangenew.append(ybinsnew[j])
                                break
			elif j==nybins-1: ynormrangenew.append(ybinsnew[j+1])
                break
print(ynormrangenew)
labelsize = 40
infosize = 40
xbins = xbinsnew
ybins = ybinsnew
histratio = histnew
xnormrange = xnormrangenew
ynormrange = ynormrangenew

### plotting and layout
# X-axis layout
xax = histratio.GetXaxis()
xax.SetLabelFont(10*labelfont+3)
xax.SetLabelSize(labelsize)
xax.SetTitle(xaxistitle)
xax.SetTitleFont(10*axtitlefont+3)
xax.SetTitleSize(axtitlesize)
xax.SetTitleOffset(1.2)
# Y-axis layout
yax = histratio.GetYaxis()
yax.SetLabelFont(10*labelfont+3)
yax.SetLabelSize(labelsize)
yax.SetTitle(yaxistitle)
yax.SetTitleFont(10*axtitlefont+3)
yax.SetTitleSize(axtitlesize)
yax.SetTitleOffset(1.7)
histratio.SetMinimum(0.8)
histratio.SetMaximum(1.2)
ROOT.gStyle.SetPalette(ROOT.kBird)
histratio.Draw("COLZ")

### Draw normalization range if needed
if(normalization==3):
	b1 = ROOT.TBox(max(xnormrange[0],xlow),max(ynormrange[0],ylow),
			min(xnormrange[1],xhigh),min(ynormrange[1],yhigh))
	b1.SetLineStyle(0)
	b1.SetLineWidth(0)
	b1.SetLineColor(9)
	#b1.SetFillStyle(3017)
	b1.SetFillColorAlpha(ROOT.kRed,0.35)
	b1.Draw()

### Title and other information displays
# title
ttitle = ROOT.TLatex()	
ttitle.SetTextFont(10*titlefont+3)
ttitle.SetTextSize(titlesize)
ttitle.DrawLatexNDC(0.15,0.9,title)
# values and errors
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
if totallumi>0:
	tinfo = ROOT.TLatex()
	tinfo.SetTextFont(10*infofont+3)
	tinfo.SetTextSize(infosize)
	info = 'luminosity: '+str(totallumi)+' pb^{-1} (13 TeV)'
	tinfo.DrawLatexNDC(0.55,0.92,info)

c1.Update()
c1.SaveAs(outfile)
