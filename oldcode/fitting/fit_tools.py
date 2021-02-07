######################################################################
# Some tools for doing fits to histograms, to be used in peak_fit.py #
######################################################################
import ROOT
import collections
import numpy as np

### polynomial function
def poly(x,par):
	# par[k] = coefficient with x**k
	res = par[0]
	for k in range(1,len(par)):
		res += par[k]*np.power(x[0],k)
	return res

def poly_fit(hist,fitrange,initialguesses,optionstring="LQ0"):
	# args: - histogram to be fitted on
	#	- tuple or list representing range to take into account for fit
	#	- (ordered) list of initial parameter guesses
	#	- option string for TH1F::Fit
	fitfunc = ROOT.TF1("fitfunc",poly,fitrange[0],fitrange[1],len(initialguesses))
	for i,val in enumerate(initialguesses):
		fitfunc.SetParameter(i,val)
	fitresult = hist.Fit("fitfunc",optionstring)
	paramdict = collections.OrderedDict()
	for i in range(len(initialguesses)):
		paramdict['a'+str(i)] = float(fitfunc.GetParameter(i))
	return (fitfunc,paramdict)

### gaussian peak with no background
def gauss(x,par): 
	# par[0] = gauss prefactor, 
	# par[1] = gauss mean,
	# par[2] = gauss std
	if(par[2]==0):
		return par[0]
	arg = (x[0]-par[1])/par[2]
	return par[0]*np.exp(-0.5*arg*arg)

def gauss_fit(hist,fitrange,initialguesses,optionstring="LQ0"):
	# args: - histogram to be fitted on
	#	- tuple or list representing range to take into account for fit
	#	- (ordered) list of initial parameter guesses
	#	- option string for TH1F::Fit
	fitfunc = ROOT.TF1("fitfunc",gauss,fitrange[0],fitrange[1],3)
	for i,val in enumerate(initialguesses):
		fitfunc.SetParameter(i,val)
	fitresult = hist.Fit("fitfunc",optionstring)
	paramdict = collections.OrderedDict()
	paramdict['amplitude'] = float(fitfunc.GetParameter(0))
	paramdict['mean'] = float(fitfunc.GetParameter(1))
	paramdict['std'] = float(abs(fitfunc.GetParameter(2)))
	return (fitfunc,paramdict)

### polynomial background with gaussian peak
def poly_plus_gauss(x,par): 
	# par[0] = mean
	# par[1] = prefactor
	# par[2] = std
	# par[k>2] = coefficient of x**(k-3)
	res = 0.
        if(len(par)>3):
                res = np.sum(np.array([par[k]*np.power(x[0],k-3) for k in range(3,len(par))]))
        if(par[2]==0):
                return res
        arg1 = (x[0]-par[0])/par[2]
        return res + par[1]*np.exp(-0.5*arg1*arg1)

def poly_plus_gauss_fit(hist,fitrange,initialguesses,optionstring="WLQ0"):
	# args: - histogram to be fitted on
	#	- tuple or list representing range to take into account for fit
	#	- (ordered) list of initial parameter guesses
	#	- option string for TH1F::Fit
	fitfunc = ROOT.TF1("fitfunc",poly_plus_gauss,fitrange[0],fitrange[1],len(initialguesses))
	for i,val in enumerate(initialguesses):
		fitfunc.SetParameter(i,val)
	fitresult = hist.Fit("fitfunc",optionstring)
	paramdict = collections.OrderedDict()
	paramdict['#mu'] = float(fitfunc.GetParameter(0))
	paramdict['A'] = float(fitfunc.GetParameter(1))
	paramdict[r'#sigma'] = float(abs(fitfunc.GetParameter(2)))
	for i in range(3,len(initialguesses)):
                paramdict['a'+str(i-3)] = float(fitfunc.GetParameter(i))
	return fitfunc,paramdict

### polynomial background with sum-of-two-gaussians peak (same mean, different std)
def poly_plus_doublegauss(x,par):
	# par[0] = mean
	# par[1] = prefactor 1
	# par[2] = std 1
	# par[3] = prefactor 2
	# par[4] = std2
	# par[k>4] = coefficient of x**(k-5)
	res = 0.
	if(len(par)>5):
		res = np.sum(np.array([par[k]*np.power(x[0],k-5) for k in range(5,len(par))]))
	if(par[2]==0 or par[4]==0):
		return res
	arg1 = (x[0]-par[0])/par[2]
	arg2 = (x[0]-par[0])/par[4]
	return res + par[1]*np.exp(-0.5*arg1*arg1) + par[3]*np.exp(-0.5*arg2*arg2)

def poly_plus_doublegauss_fit(hist,fitrange,initialguesses,optionstring="WLQ0"):
	# args: - histogram to be fitted on
	#	- tuple or list representing range to take into account for fit
	#	- (ordered) list of initial parameter guesses
	fitfunc = ROOT.TF1("fitfunc",poly_plus_doublegauss,fitrange[0],fitrange[1],len(initialguesses))
	for i,val in enumerate(initialguesses):
		fitfunc.SetParameter(i,val)
	fitfunc.SetParLimits(1,0.,initialguesses[1]*100)
	fitfunc.SetParLimits(2,0.,initialguesses[2]*100)
	fitfunc.SetParLimits(3,0.,initialguesses[3]*100)
	fitfunc.SetParLimits(4,0.,initialguesses[4]*100)
	fitresult = hist.Fit("fitfunc",optionstring)
	paramdict = collections.OrderedDict()
	paramdict[r'#mu'] = float(fitfunc.GetParameter(0))
	paramdict[r'A_{1}'] = float(fitfunc.GetParameter(1))
	paramdict[r'#sigma_{1}'] = float(abs(fitfunc.GetParameter(2)))
	paramdict[r'A_{2}'] = float(fitfunc.GetParameter(3))
	paramdict[r'#sigma_{2}'] = float(abs(fitfunc.GetParameter(4)))
	for i in range(5,len(initialguesses)):
		paramdict['a'+str(i-5)] = float(fitfunc.GetParameter(i))
	return fitfunc,paramdict

def plot_fit(hist,label,fitfunc,paramdict,backfit,xaxtitle,yaxtitle,
	     figtitle,savepath,extrainfo): 
	# args: - hist, fitfucn and backfit are the histogram, and two fitted functions 
	# 	  (e.g. total and background only)
	# 	- label is the legend entry for the histogram
	#	- paramdict is a dict containing names and values of fitted parameters of fitfunc
	# 	- xaxtitle and yaxtitle are axis titles, figtitle is figure title
	# 	- extrainfo is a string with extra info to show, use '<<' to split lines
	ROOT.gROOT.SetBatch(ROOT.kTRUE);
	# initialization of canvas
	c1 = ROOT.TCanvas("c1","c1")
	c1.SetCanvasSize(1200,1200)
	titlefont = 6; titlesize = 60
	labelfont = 5; labelsize = 45
	axtitlefont = 5; axtitlesize = 45
	infofont = 4; infosize = 30
	legendfont = 4; legendsize = 35
	c1.SetBottomMargin(0.1)
	c1.SetTopMargin(0.15)
	c1.SetLeftMargin(0.15)

	# legend
	leg = ROOT.TLegend(0.65,0.7,0.88,0.8)
	leg.SetTextFont(10*legendfont+3)
	leg.SetTextSize(legendsize)
	leg.SetBorderSize(0)

	# draw histogram
	hist.SetStats(False)
	hist.SetLineColor(ROOT.kBlue)
	hist.SetLineWidth(2)
	hist.Sumw2()
	leg.AddEntry(hist,label,"l")
	hist.Draw()

	# X-axis layout
	xax = hist.GetXaxis()
	xax.SetNdivisions(10,4,0,ROOT.kTRUE)
	xax.SetLabelFont(10*labelfont+3)
	xax.SetLabelSize(labelsize)
	xax.SetTitle(xaxtitle)
	xax.SetTitleFont(10*axtitlefont+3)
	xax.SetTitleSize(axtitlesize)

	# Y-axis layout
	hist.SetMaximum(hist.GetMaximum()*1.2)
	hist.SetMinimum(0.)
	yax = hist.GetYaxis()
	yax.SetMaxDigits(3)
	yax.SetNdivisions(8,4,0,ROOT.kTRUE)
	yax.SetLabelFont(10*labelfont+3)
	yax.SetLabelSize(labelsize)
	yax.SetTitle(yaxtitle)
	yax.SetTitleFont(10*axtitlefont+3)
	yax.SetTitleSize(axtitlesize)
	yax.SetTitleOffset(1.5)
	ROOT.gPad.SetTicks(1,1)
	hist.Draw("HIST E")
	tinfo = ROOT.TLatex()

	# draw fitted function
	if backfit is not None:
		backfit.SetLineColor(ROOT.kGreen+3)
		backfit.SetLineWidth(3)
		backfit.SetLineStyle(ROOT.kDashed)
		backfit.Draw("SAME")
		leg.AddEntry(backfit,'background fit','l')
		leg.Draw()

	# draw fitted function
	if fitfunc is not None:
		fitfunc.SetLineColor(ROOT.kRed)
		fitfunc.SetLineWidth(3)
		fitfunc.Draw("SAME")
		leg.AddEntry(fitfunc,'total fit','l')
		leg.Draw()

		# display additional info
		tinfo.SetTextFont(10*infofont+3)
		tinfo.SetTextSize(infosize)
		if fitfunc.GetNDF()==0:
			normchi2 = 0
		else:
			normchi2 = fitfunc.GetChisquare()/fitfunc.GetNDF()
		# general method
		for i,key in enumerate(paramdict):
			info = key+' : {0:.4E}'.format(paramdict[key])
			tinfo.DrawLatexNDC(0.65,0.65-i*0.035,info)
		info = r"#frac{#chi^{2}}{ndof}"+' of fit: {0:.2E}'.format(normchi2)
		tinfo.DrawLatexNDC(0.65,0.65-(len(paramdict)+1)*0.035,info)
		# temp: dirty method
		'''info = 'background: {0:.0f}'.format(paramdict['offset'])
		tinfo.DrawLatexNDC(0.60,0.65,info)
		if(paramdict['slope']>0):
			info = ' + {0:.0f}x'.format(paramdict['slope'])
		else:
			info = ' - {0:.0f}x'.format(abs(paramdict['slope']))
		tinfo.DrawLatexNDC(0.75,0.65-0.035,info)
		info = 'mean: {0:.2f} MeV'.format(paramdict['#mu']*1000)
		tinfo.DrawLatexNDC(0.61,0.65-2*0.035,info)
		info = r'core #sigma:'+' {0:.2f} MeV'.format(paramdict['#sigma_{1}']*1000)
		tinfo.DrawLatexNDC(0.62,0.65-3*0.035,info)
		info = r'tail #sigma:'+' {0:.2f} MeV'.format(paramdict['#sigma_{2}']*1000)
		tinfo.DrawLatexNDC(0.63,0.65-4*0.035,info)
		info = 'core fraction: {0:.0f} %'.format(paramdict['A_{1}']/
						(paramdict['A_{1}']+paramdict['A_{2}'])*100)
		tinfo.DrawLatexNDC(0.64,0.65-5*0.035,info)
		info = r"#frac{#chi^{2}}{ndof}"+' of fit: {0:.2f}'.format(normchi2)
		tinfo.DrawLatexNDC(0.65,0.65-6.5*0.035,info) '''

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
	tinfo.SetTextFont(10*titlefont+3)
	tinfo.SetTextSize(titlesize)
	tinfo.DrawLatexNDC(0.15,0.9,figtitle)

	c1.Update()
	c1.SaveAs(savepath)
