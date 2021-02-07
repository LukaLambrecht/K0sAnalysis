#####################################################################################
# Python script to read a noskim.root tuple (or similar), and plot a variable in it #
#####################################################################################
import ROOT
import sys
sys.path.append('../tools')
import plottools as pt

def fillvarfromtuple(tree,varname,xlow,xhigh,nbins,varsize='',weightvar='',nprocess=-1,label=''):
    # filling histogram from a given tree
    
    # make output histogram
    hist = ROOT.TH1F('hist','',nbins,xlow,xhigh)

    # set number of events to process
    if( nprocess<0 or nprocess>tree.GetEntries() ): nprocess=tree.GetEntries() 

    # loop over events
    for i in range(nprocess):
	if( i%10000==0 ):
	    print('number of processed events: '+str(i)) 
	tree.GetEntry(i)
	# determine weight for this entry
	weight = 1
	if weightvar!='': weight = getattr(tree,weightvar)
	# determine values for requested variable in this entry
	varvalues = []
	# case 1: branch is scalar
	if varsize=='':
	    varvalues = [getattr(tree,varname)]
	# case 2: branch is vector
	else:
	    nvalues = getattr(tree,varsize)
	    varvalues = [getattr(tree,varname)[j] for j in list(range(nvalues))]
	# fill the histogram
	for var in varvalues: hist.Fill(var,weight)
    
    # set histogram title
    if label=='': hist.SetTitle(varname)
    else: hist.SetTitle(label)
    return hist

def plotsinglehistogram(hist,figname,title='',xaxtitle='',yaxtitle='',logy=False):
    # drawing a single histogram

    pt.setTDRstyle()
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

    # set histogram properties
    hist.SetLineColor(ROOT.kBlue)
    hist.SetLineWidth(3)
    hist.Sumw2()

    # legend
    leg = ROOT.TLegend(0.6,0.7,0.9,0.8)
    leg.SetTextFont(10*legendfont+3)
    leg.SetTextSize(legendsize)
    leg.SetBorderSize(1)
    leg.AddEntry(hist,hist.GetTitle(),"l")
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
    if not logy:
	hist.SetMaximum(hist.GetMaximum()*1.2)
	hist.SetMinimum(0.)
    else:
	c1.SetLogy()
	hist.SetMaximum(hist.GetMaximum()*10)
	hist.SetMinimum(hist.GetMaximum()/1e7)
    yax = hist.GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle(yaxtitle)
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.5)
    hist.Draw("HIST")

    # title
    ttitle = ROOT.TLatex()	
    ttitle.SetTextFont(10*titlefont+3)
    ttitle.SetTextSize(titlesize)
    titlebox = (0.15,0.92)

    # draw all objects
    hist.Draw("HIST")
    leg.Draw("same")
    ttitle.DrawLatexNDC(titlebox[0],titlebox[1],title)

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

    c1.SaveAs(figname.split('.')[0]+'.png')

if __name__=='__main__':

    # initialization
    finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/test/noskim.root'

    fin = ROOT.TFile.Open(finloc)
    tree = fin.Get("blackJackAndHookers/blackJackAndHookersTree")
    nprocess = -1
    xaxtitle = r'a unit'
    yaxtitle = r'another unit'
    varname = '_V0VtxNormChi2'
    varsize = '_nV0s'
    title = r'a title'

    hist = fillvarfromtuple(tree,varname,0,15,30,varsize=varsize,weightvar='_weight',nprocess=nprocess)
    plotsinglehistogram(hist,'figure.png',xaxtitle=xaxtitle,yaxtitle=yaxtitle,title=title)
