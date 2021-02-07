###########################################################################################
# Python script to read a noskim.root tree, extract the a Kshort vertex value and plot it #
###########################################################################################
import ROOT
import numpy as np
import math

# initialization
finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIAutumn18_DYJetsToLL/skim_ztomumu_all.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_MINIAOD/skim_ztomumu_1t20.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_JPsiToMuMu_MINIAODSIM_test/skim_jpsi_met_all.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_BToJPsi_MINIAODSIM_test/skim_jpsi_met_1t20.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_ZeroBias_MINIAOD_test/skim_jpsi_met.root'
#finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/noskim.root'
fin = ROOT.TFile.Open(finloc)
#tree = fin.Get("blackJackAndHookers/blackJackAndHookersTree")
tree = fin.Get("laurelin")
treetype = 'tree' # choose from 'tree' or 'ntuple'
nevents = tree.GetEntries()
nprocess = int(min(1e6,nevents))
print(str(nprocess)+' events out of '+str(nevents)+' will be processed.')
hist = ROOT.TH1F('hist','',20,0,20)
xaxtitle = r'p_T (GeV)'
varname = '_KsPtPos'
#limit = '_nKshorts'
title = r'single track transverse momentum'

# filling histogram
for i in range(nprocess):
	if(i>1 and (i+1)%10000==0):
		print('number of processed events: '+str(i+1)) 
	tree.GetEntry(i)
	if(treetype=='tree'):
		hist.Fill(getattr(tree,varname))
		#print(getattr(tree,varname))
		#pvx = getattr(tree,"_primaryVertexX"); pvy = getattr(tree,"_primaryVertexY")
		#bsx = getattr(tree,"_beamSpotX"); bsy = getattr(tree,"_beamSpotY")
		#relr = math.sqrt((pvx-bsx)**2+(pvy-bsy)**2)
		#hist.Fill(relr)
	elif(treetype=='ntuple'):
		nlimit = getattr(tree,limit)
		if nlimit==0:
			continue
		for j in range(nlimit):
			varvalue = getattr(tree,varname)[j]
			hist.Fill(varvalue)

# drawing histogram
ROOT.gROOT.SetBatch(ROOT.kTRUE)
c1 = ROOT.TCanvas("c1","c1")
c1.SetCanvasSize(1200,1200)
# set fonts and text sizes
titlefont = 6; titlesize = 60
labelfont = 5; labelsize = 50
axtitlefont = 5; axtitlesize = 50
infofont = 6; infosize = 30
legendfont = 4; legendsize = 30

c1.SetBottomMargin(0.15)
c1.SetLeftMargin(0.15)
c1.SetTopMargin(0.15)
hist.Draw("HIST")

# legend
leg = ROOT.TLegend(0.5,0.7,0.9,0.9)
leg.SetTextFont(10*legendfont+3)
leg.SetTextSize(legendsize)
leg.SetBorderSize(0)

hist.SetStats(False)
hist.SetLineColor(ROOT.kBlue)
#hist.SetFillColor(ROOT.kRed)
hist.SetLineWidth(3)
#hist.Sumw2()
leg.AddEntry(hist,hist.GetTitle(),"f")
hist.Draw("HIST")

# X-axis layout
xax = hist.GetXaxis()
xax.SetNdivisions(10,4,0,ROOT.kTRUE)
xax.SetLabelFont(10*labelfont+3)
xax.SetLabelSize(labelsize)
xax.SetTitle(xaxtitle)
xax.SetTitleFont(10*axtitlefont+3)
xax.SetTitleSize(axtitlesize)
xax.SetTitleOffset(1.2)
# Y-axis layout
#hist.SetMaximum(hist.GetMaximum()*1.2)
#hist.SetMinimum(0.)
c1.SetLogy()
hist.SetMaximum(hist.GetMaximum()*10)
hist.SetMinimum(hist.GetMaximum()/1e7)
yax = hist.GetYaxis()
yax.SetMaxDigits(3)
yax.SetNdivisions(8,4,0,ROOT.kTRUE)
yax.SetLabelFont(10*labelfont+3)
yax.SetLabelSize(labelsize)
yax.SetTitle('number of reconstructed vertices')
yax.SetTitleFont(10*axtitlefont+3)
yax.SetTitleSize(axtitlesize)
yax.SetTitleOffset(1.25)
hist.Draw("HIST")

# title
ttitle = ROOT.TLatex()	
ttitle.SetTextFont(10*titlefont+3)
ttitle.SetTextSize(titlesize)
ttitle.DrawLatexNDC(0.15,0.92,title)

'''# TEMP: draw vertical lines
linestyle = 9
linewidth = 2
linecolor = ROOT.kRed
vl1 = ROOT.TLine(4.3,hist.GetMinimum(),
		4.3,hist.GetMaximum())
vl1.SetLineWidth(linewidth); vl1.SetLineColor(linecolor)
vl1.SetLineStyle(linestyle)
vl1.Draw()
vl2 = ROOT.TLine(7.2,hist.GetMinimum(),
		7.2,hist.GetMaximum())
vl2.SetLineWidth(linewidth); vl2.SetLineColor(linecolor)
vl2.SetLineStyle(linestyle)
vl2.Draw()
vl3 = ROOT.TLine(11.,hist.GetMinimum(),
		11.,hist.GetMaximum())
vl3.SetLineWidth(linewidth); vl3.SetLineColor(linecolor)
vl3.SetLineStyle(linestyle)
vl3.Draw()
tinfo = ROOT.TLatex()
tinfo.SetTextFont(10*infofont+3)
tinfo.SetTextSize(infosize)
tinfo.SetTextColor(linecolor)
tinfo.DrawLatexNDC(0.27,0.8,"pixel layer 1")
tinfo.DrawLatexNDC(0.35,0.7,"pixel layer 2")
tinfo.DrawLatexNDC(0.44,0.6,"pixel layer 3")'''

c1.Update()
c1.SaveAs('figure.png')
