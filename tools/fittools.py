###########################################
# Some tools for doing fits to histograms #
###########################################

import ROOT
import collections
import numpy as np
from functools import partial

### polynomial function
def poly(x, par, degree=0):
    # par[k] = coefficient with x**k
    # note: in new versions of ROOT or CMSSW or python,
    #       one cannot rely on len(par) anymore to get the degree
    #       of the polynomial; instead it is passed here explicitly.
    res = 0.
    for k in range(degree+1):
        res += par[k]*np.power(x[0], k)
    return res

def poly_fit(hist, fitrange, initialguesses, optionstring="LQ0"):
    # args: - histogram to be fitted on
    #        - tuple or list representing range to take into account for fit
    #        - (ordered) list of initial parameter guesses
    #        - option string for TH1F::Fit
    # note: the fitobj object (see below) must be kept in memory explicitly
    #       for using fitfunc (else error "the callable was deleted"),
    #       so it is returned as well, but not meant to be used explicitly.
    degree = len(initialguesses)-1
    fitobj = partial(poly, degree=degree)
    fitfunc = ROOT.TF1("fitfunc", fitobj, fitrange[0], fitrange[1], len(initialguesses))
    for i,val in enumerate(initialguesses):
        fitfunc.SetParameter(i,val)
    fitresult = hist.Fit("fitfunc", optionstring)
    paramdict = collections.OrderedDict()
    for i in range(len(initialguesses)):
        paramdict['a'+str(i)] = float(fitfunc.GetParameter(i))
    return (fitfunc, paramdict, fitobj)

### gaussian peak with no background
def gauss(x, par): 
    # par[0] = gauss prefactor, 
    # par[1] = gauss mean,
    # par[2] = gauss std
    if(par[2]==0): return par[0]
    arg = (x[0]-par[1])/par[2]
    return par[0]*np.exp(-0.5*arg*arg)

def gauss_fit(hist, fitrange, initialguesses, optionstring="LQ0"):
    # args: - histogram to be fitted on
    #        - tuple or list representing range to take into account for fit
    #        - (ordered) list of initial parameter guesses
    #        - option string for TH1F::Fit
    # note: the fitobj object (see below) must be kept in memory explicitly
    #       for using fitfunc (else error "the callable was deleted"),
    #       so it is returned as well, but not meant to be used explicitly.
    fitobj = gauss
    fitfunc = ROOT.TF1("fitfunc", fitobj, fitrange[0], fitrange[1], 3)
    for i,val in enumerate(initialguesses):
        fitfunc.SetParameter(i,val)
    fitresult = hist.Fit("fitfunc", optionstring)
    paramdict = collections.OrderedDict()
    paramdict['amplitude'] = float(fitfunc.GetParameter(0))
    paramdict['mean'] = float(fitfunc.GetParameter(1))
    paramdict['std'] = float(abs(fitfunc.GetParameter(2)))
    return (fitfunc, paramdict, fitobj)

### polynomial background with gaussian peak
def poly_plus_gauss(x, par, degree=-1): 
    # par[0] = mean
    # par[1] = prefactor
    # par[2] = std
    # par[k>2] = coefficient of x**(k-3)
    # note: in new versions of ROOT or CMSSW or python,
    #       one cannot rely on len(par) anymore to get the degree
    #       of the polynomial; instead it is passed here explicitly.
    res = 0.
    if(degree>=0):
        res = np.sum(np.array([par[k]*np.power(x[0],k-3) for k in range(3, 4+degree)]))
    if(par[2]==0): return res
    arg1 = (x[0]-par[0])/par[2]
    return res + par[1]*np.exp(-0.5*arg1*arg1)

def poly_plus_gauss_fit(hist, fitrange, initialguesses, optionstring="WLQ0"):
    # args: - histogram to be fitted on
    #        - tuple or list representing range to take into account for fit
    #        - (ordered) list of initial parameter guesses
    #        - option string for TH1F::Fit
    # note: the fitobj object (see below) must be kept in memory explicitly
    #       for using fitfunc (else error "the callable was deleted"),
    #       so it is returned as well, but not meant to be used explicitly.
    degree = len(initialguesses)-4
    # (note: use -4 since len=3 implies no polynomial, i.e. should be set to -1)
    fitobj = partial(poly_plus_gauss, degree=degree)
    fitfunc = ROOT.TF1("fitfunc", fitobj, fitrange[0], fitrange[1], len(initialguesses))
    for i,val in enumerate(initialguesses):
        fitfunc.SetParameter(i,val)
    fitresult = hist.Fit("fitfunc", optionstring)
    paramdict = collections.OrderedDict()
    paramdict['#mu'] = float(fitfunc.GetParameter(0))
    paramdict['A'] = float(fitfunc.GetParameter(1))
    paramdict[r'#sigma'] = float(abs(fitfunc.GetParameter(2)))
    for i in range(3,len(initialguesses)):
        paramdict['a'+str(i-3)] = float(fitfunc.GetParameter(i))
    return (fitfunc, paramdict, fitobj)

### polynomial background with sum-of-two-gaussians peak (same mean, different std)
def poly_plus_doublegauss(x, par, degree=-1):
    # par[0] = mean
    # par[1] = prefactor 1
    # par[2] = std 1
    # par[3] = prefactor 2
    # par[4] = std2
    # par[k>4] = coefficient of x**(k-5)
    # note: in new versions of ROOT or CMSSW or python,
    #       one cannot rely on len(par) anymore to get the degree
    #       of the polynomial; instead it is passed here explicitly.
    res = 0.
    if(degree>=0):
        res = np.sum(np.array([par[k]*np.power(x[0],k-5) for k in range(5, 6+degree)]))
    if(par[2]==0 or par[4]==0): return res
    arg1 = (x[0]-par[0])/par[2]
    arg2 = (x[0]-par[0])/par[4]
    return res + par[1]*np.exp(-0.5*arg1*arg1) + par[3]*np.exp(-0.5*arg2*arg2)

def poly_plus_doublegauss_fit(hist, fitrange, initialguesses, optionstring="WLQ0"):
    # args: - histogram to be fitted on
    #        - tuple or list representing range to take into account for fit
    #        - (ordered) list of initial parameter guesses
    # note: the fitobj object (see below) must be kept in memory explicitly
    #       for using fitfunc (else error "the callable was deleted"),
    #       so it is returned as well, but not meant to be used explicitly.
    degree = len(initialguesses)-6
    # (note: use -6 since len=5 implies no polynomial, i.e. should be set to -1)
    fitobj = partial(poly_plus_doublegauss, degree=degree)
    fitfunc = ROOT.TF1("fitfunc", fitobj, fitrange[0], fitrange[1], len(initialguesses))
    for i,val in enumerate(initialguesses):
        fitfunc.SetParameter(i,val)
    fitfunc.SetParLimits(1,0.,initialguesses[1]*100)
    fitfunc.SetParLimits(2,0.,initialguesses[2]*100)
    fitfunc.SetParLimits(3,0.,initialguesses[3]*100)
    fitfunc.SetParLimits(4,0.,initialguesses[4]*100)
    fitresult = hist.Fit("fitfunc", optionstring)
    paramdict = collections.OrderedDict()
    paramdict[r'#mu'] = float(fitfunc.GetParameter(0))
    paramdict[r'A_{1}'] = float(fitfunc.GetParameter(1))
    paramdict[r'#sigma_{1}'] = float(abs(fitfunc.GetParameter(2)))
    paramdict[r'A_{2}'] = float(fitfunc.GetParameter(3))
    paramdict[r'#sigma_{2}'] = float(abs(fitfunc.GetParameter(4)))
    for i in range(5,len(initialguesses)):
        paramdict['a'+str(i-5)] = float(fitfunc.GetParameter(i))
    return (fitfunc, paramdict, fitobj)
