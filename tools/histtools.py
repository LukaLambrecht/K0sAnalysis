########################################################################
# some small tools for working with histograms and lists of histograms #
########################################################################

import os
import math
import numpy as np
from array import array
import ROOT
import listtools as lt

### histogram reading and loading ###

def loadallhistograms(histfile):
    ### read a root file containing histograms and load all histograms to a list
    f = ROOT.TFile.Open(histfile)
    histlist = []
    keylist = f.GetListOfKeys()
    for key in keylist:
        hist = f.Get(key.GetName())
        # check if histogram is readable
        try:
            nentries = hist.GetEntries()
            nbins = hist.GetNbinsX()
            hist.SetDirectory(ROOT.gROOT)
        except:
            print('### WARNING ###: key "'+str(key.GetName())+'" does not correspond to valid hist.')
            continue
	hist.SetName(key.GetName())
	histlist.append(hist)
    f.Close()
    return histlist

def loadhistograms(histfile,mustcontainall=[],mustcontainone=[],
			    maynotcontainall=[],maynotcontainone=[]):
    ### read a root file containing histograms and load all histograms to a list
    # with selection already included at this stage
    # (instead of loading all and then selecting with methods below)
    # (useful in case of many histograms of which only a few are needed)
    f = ROOT.TFile.Open(histfile)
    histlist = []
    keylist = f.GetListOfKeys()
    for key in keylist:
	if not lt.subselect_string(key.GetName(),
		mustcontainone=mustcontainone,mustcontainall=mustcontainall,
		maynotcontainone=maynotcontainone,maynotcontainall=maynotcontainall): continue
        hist = f.Get(key.GetName())
        # check if histogram is readable
        try:
            nentries = hist.GetEntries()
            nbins = hist.GetNbinsX()
            hist.SetDirectory(0)
        except:
            print('WARNING in loadhistograms: key "'+str(key.GetName())
		    +'" does not correspond to valid hist.')
            continue
        histlist.append(hist)
    f.Close()
    return histlist


### histogram subselection ###

def selecthistograms(histlist,mustcontainone=[],mustcontainall=[],
			maynotcontainone=[],maynotcontainall=[]):
    idlist = [hist.GetName() for hist in histlist]
    (indlist,selhistlist) = lt.subselect_objects(histlist,idlist,
	mustcontainone=mustcontainone,mustcontainall=mustcontainall,
	maynotcontainone=maynotcontainone,maynotcontainall=maynotcontainall)
    return (indlist,selhistlist)

### histogram clipping ###

def cliphistogram(hist,clipboundary=0):
    ### clip a histogram to minimum zero
    # also allow a clipboundary different from zero, useful for plotting 
    # (e.g. to ignore artificial small values such as the one at the end of this function)
    for i in range(0,hist.GetNbinsX()+2):
        if hist.GetBinContent(i)<clipboundary:
            hist.SetBinContent(i,0)
            hist.SetBinError(i,0)
    # check if histogram is empty after clipping and if so, fill it with dummy value
    if hist.GetSumOfWeights()<1e-12: hist.SetBinContent(1,1e-6)

def cliphistograms(histlist,clipboundary=0):
    ### apply cliphistogram on all histograms in a list
    for hist in histlist: cliphistogram(hist,clipboundary=clipboundary)

def clipallhistograms(histfile,mustcontainall=[],clipboundary=0):
    ### apply cliphistogram on all histograms in a file
    histlist = loadallhistograms(histfile)
    if len(mustcontainall)==0:
	cliphistograms(histlist,clipboundary=clipboundary)
    else:
	(indlist,_) = selecthistograms(histlist,mustcontainall=mustcontainall)
	for index in indlist: cliphistogram(histlist[index],clipboundary=clipboundary)
    tempfilename = histfile[:-5]+'_temp.root'
    f = ROOT.TFile.Open(tempfilename,'recreate')
    for hist in histlist:
        hist.Write()
    f.Close()
    os.system('mv '+tempfilename+' '+histfile)

### finding minimum and maximum ###

def getminmax(histlist):
    # get suitable minimum and maximum values for plotting a hist collection (not stacked)
    totmax = 0.
    totmin = 99.
    for hist in histlist:
        for i in range(1,hist.GetNbinsX()+1):
            val = hist.GetBinContent(i)
            if val > totmax: totmax = val
            if val < totmin: totmin = val
    return (totmin,totmax)

def getminmaxmargin(histlist,clip=False):
    (totmin,totmax) = getminmax(histlist)
    topmargin = (totmax-totmin)/2.
    bottommargin = (totmax-totmin)/5.
    minv = totmin-bottommargin
    maxv = totmax+topmargin
    if( clip and minv<0 ): minv = 0
    return (minv,maxv)

### histogram conversion ###

def tgraphtohist( graph ):

    # get list of x values and sort them
    xvals = []
    for i in range(graph.GetN()): xvals.append(graph.GetX()[i])
    xvals = np.array(xvals)
    sortedindices = np.argsort(xvals)
    # make bins
    bins = []
    for i in sortedindices: bins.append(graph.GetX()[i]-graph.GetErrorXlow(i))
    bins.append(graph.GetX()[i]+graph.GetErrorXhigh(i))
    # make histogram
    hist = ROOT.TH1D("","",len(bins)-1,array('f',bins))
    # set bin contents
    for i in range(1,hist.GetNbinsX()+1):
        bincontent = graph.GetY()[sortedindices[i-1]]
        binerror = max(graph.GetErrorYlow(sortedindices[i-1]),
                        graph.GetErrorYhigh(sortedindices[i-1]))
        hist.SetBinContent(i,bincontent)
        hist.SetBinError(i,binerror)
    hist.SetName(graph.GetName())
    hist.SetTitle(graph.GetTitle())
    return hist

### histogram calculations ###

def binperbinmaxvar( histlist, nominalhist ):
    ### get the bin-per-bin maximum variation (in absolute value) of histograms in histlist 
    ### wrt nominalhist.
    maxhist = nominalhist.Clone()
    maxhist.Reset()
    nbins = maxhist.GetNbinsX()
    for i in range(0,nbins+2):
	nomval = nominalhist.GetBinContent(i)
	varvals = np.zeros(len(histlist))
	for j in range(len(histlist)):
	    varvals[j] = abs(histlist[j].GetBinContent(i)-nomval)
	maxhist.SetBinContent(i,np.amax(varvals))
    return maxhist
    
def rootsumsquare( histlist ):
    ### return a histogram that is the root-sum-square of all histograms in histlist.
    # check the input list
    if( len(histlist)<1 ):
	print('### ERROR ###: at least one histogram required for rootsumsquare')
	return None
    res = histlist[0].Clone()
    res.Reset()
    nbins = res.GetNbinsX()
    bincontents = np.zeros(nbins+2)
    for hist in histlist:
	if( hist.GetNbinsX()!=nbins ):
	    print('### ERROR ###: histograms are not compatible for summing in quadrature')
	    return None
	thisbincontents = np.zeros(nbins+2)
	for i in range(0,nbins+2): thisbincontents[i] = hist.GetBinContent(i)
	bincontents += np.power(thisbincontents,2)
    bincontents = np.sqrt(bincontents)
    for i in range(0,nbins+2):
	res.SetBinContent(i,bincontents[i])
    return res

### printing ###

def printhistogram(hist,naninfo=False):

    print('### {} ###'.format(hist.GetName()))
    for i in range(0,hist.GetNbinsX()+2):
        bininfo = '  -----------\n'
        bininfo += '  bin: {} -> {}\n'.format(hist.GetBinLowEdge(i),
                                            hist.GetBinLowEdge(i)+hist.GetBinWidth(i))
        bininfo += '  content: {}\n'.format(hist.GetBinContent(i))
	if naninfo:
	    bininfo += '    (isnan: {})\n'.format(math.isnan(hist.GetBinContent(i)))
	    bininfo += '    (isinf: {})\n'.format(math.isinf(hist.GetBinContent(i)))
        bininfo += '  error: {}\n'.format(hist.GetBinError(i))
        print(bininfo)
	
def printhistograms( histfile, mustcontainall=[], mustcontainone=[],
				maynotcontainall=[], maynotcontainone=[],
				naninfo=False ):
    allhists = loadallhistograms(histfile)
    selhists = selecthistograms(allhists,mustcontainone=mustcontainone,
					mustcontainall=mustcontainall,
					maynotcontainone=maynotcontainone,
					maynotcontainall=maynotcontainall)[1]
    for hist in selhists:
	printhistogram(hist,naninfo=naninfo)
