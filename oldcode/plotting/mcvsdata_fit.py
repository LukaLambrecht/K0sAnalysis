#################################################################
# Script to read histograms from mcvsdata_fillrd.py or similar  #
# and perform a scaling of the cross sections to match the data #
#################################################################
import ROOT
from hyperopt import hp, fmin, tpe, rand, STATUS_OK, Trials, space_eval
import numpy as np
from functools import partial

### Configure input parameters
histfile = '~/Kshort/histograms/test.root' # file to read histograms

### Load histograms and variables
print('loading histograms')
f = ROOT.TFile.Open(histfile)
normalization = int(f.Get("normalization")[0])
if(normalization==3):
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
# sum all data hists into one
datahist = datahistlist[0].Clone()
for i in range(1,len(datahistlist)):
	datahist.Add(datahistlist[i])
# redefine bins, now including under and overflow bins
nbins = mchistlist[0].GetNbinsX()
xlow = mchistlist[0].GetXaxis().GetXmin()
xhigh = mchistlist[0].GetXaxis().GetXmax()
bins = mchistlist[0].GetXaxis().GetXbins()

### function to quantify mismatch between data and simulation
def mismatch_MSE(mchist,datahist):
	mse = 0.
	nbins = mchist.GetNbinsX()
	for i in range(nbins):
		mcbincontent = mchist.GetBinContent(i)
		databincontent = datahist.GetBinContent(i)
		mse += (mcbincontent-databincontent)**2
	mse = mse/nbins
	return mse

### function to scale histograms with given set of scales
def scale(mchistlist,scales):
	newsumofweights = 0
	for i in range(len(mchistlist)):
		newsumofweights += mchistlist[i].GetSumOfWeights()*scales[i]
	commonscale = datahist.GetSumOfWeights()/newsumofweights
	for i in range(len(mchistlist)):
		mchistlist[i].Scale(scales[i]*commonscale)
	mchistsum = mchistlist[0].Clone()
	for i in range(1,len(mchistlist)):
		mchistsum.Add(mchistlist[i])
	return mchistsum

def run(scales):
	global mchistlist,datahist
	scales_list = []
	for i in range(len(scales)):
		scales_list.append(float(scales['sigma'+str(i)]))
	print('scales for this run: '+str(scales_list))
	mchistsum = scale(mchistlist,scales_list)
	loss = mismatch_MSE(mchistsum,datahist)
	print('resulting loss: '+str(loss))
	print('----------------------')
	scale(mchistlist,np.reciprocal(scales_list))
	return{'loss':loss,'status':STATUS_OK}

#scales = [1.]*len(mchistlist)
scales = {'sigma0':1.,'sigma1':hp.loguniform('sigma1',np.log(1e-5),np.log(1e5))}
if(len(scales) != len(mchistlist)):
	print('ERROR: dimensions of mchistlist and scales do not match')
	exit()
nevals = 100
trials = Trials()
best = fmin(run, space = scales,
		algo = partial(tpe.suggest,n_startup_jobs=1),
		max_evals = nevals,
		trials = trials)
best = space_eval(scales,best)
best_list = []
for i in range(len(best)):
		best_list.append(float(best['sigma'+str(i)]))
print('best values:')
run(best)
print('writing histograms to file...')
scale(mchistlist,best_list)
outname = histfile[:-5]+'_fitted.root'
print(outname)
fout = ROOT.TFile.Open(outname,"recreate")
for hist in mchistlist+datahistlist:
	hist.Write(hist.GetName())
normalization_st = ROOT.TVectorD(1); normalization_st[0] = normalization
normalization_st.Write("normalization")
if(normalization==3):
	normrange_st = ROOT.TVectorD(2)
	normrange_st[0] = normrange[0]; normrange_st[1] = normrange[1]
	normrange_st.Write("normrange")
if(normalization==1):
	lumi_st = ROOT.TVectorD(1)
	lumi_st[0] = lumi
	lumi_st.Write("lumi")
fout.Close()
print('done')

