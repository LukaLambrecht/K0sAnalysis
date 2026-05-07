########################################################################################
# Count the number of instances in an invariant mass peak after background subtraction #
########################################################################################
# Note: this could potentially be updated to a new fitting library,
#       to remove all ROOT dependency.


import sys
import os
import numpy as np
from array import array
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import tools.fittools as ft
import plotting.plotfit as pft

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

# -------------------------------------------------------------------------------------
# Determine FWHM of a given Histogram:
# -------------------------------------------------------------------------------------
def Confidence(hist, confLevel = 0.95):
    ix      = hist.GetXaxis().FindBin(hist.GetMean())
    ixlow   = ix
    ixhigh  = ix
    nb      = hist.GetNbinsX()
    ntot    = hist.Integral()
    nsum    = hist.GetBinContent(ix)
    width   = hist.GetBinWidth(ix)
    
    if ntot==0:                                                 return 0
    while (nsum < confLevel * ntot):
        nlow    = hist.GetBinContent(ixlow-1)   if ixlow>0      else 0
        nhigh   = hist.GetBinContent(ixhigh+1)  if ixhigh<nb    else 0
        if (nsum+max(nlow,nhigh) < confLevel * ntot):
            if (nlow>=nhigh and ixlow>0):
                nsum    += nlow
                ixlow   -=1
                width   += hist.GetBinWidth(ixlow)
            elif ixhigh<nb:
                nsum    += nhigh
                ixhigh  +=1
                width   += hist.GetBinWidth(ixhigh)
            else:       raise ValueError('BOOM')
        else:
            if (nlow>nhigh):
                width   += hist.GetBinWidth(ixlow-1) * (confLevel * ntot - nsum) / nlow
            else:
                width   += hist.GetBinWidth(ixhigh+1) * (confLevel * ntot - nsum) / nhigh
            nsum        = ntot
    
    return width


def _fit_quality(fitfunc):
    ndf = int(fitfunc.GetNDF())
    chi2 = float(fitfunc.GetChisquare())
    if ndf <= 0:
        return chi2, ndf, np.inf
    return chi2, ndf, chi2 / float(ndf)


def _make_signal_fit(hist, fitrange, fitcenter, model, background_params, background_degree, funcname):
    peak_height = max(hist.GetMaximum() / 2., 1e-6)
    peak_width = max(hist.GetRMS(), hist.GetBinWidth(1), 1e-6)

    if model == 'single':
        guess = [fitcenter, peak_height, peak_width]
        if background_degree == 1:
            guess += [background_params['a0'], background_params['a1']]
        else:
            guess += [background_params['a0'], background_params['a1'], background_params['a2']]
        return ft.poly_plus_gauss_fit(hist, fitrange, guess, funcname=funcname)

    if model == 'double':
        guess = [fitcenter, peak_height, peak_width / 4., peak_height, peak_width]
        if background_degree == 1:
            guess += [background_params['a0'], background_params['a1']]
        else:
            guess += [background_params['a0'], background_params['a1'], background_params['a2']]
        return ft.poly_plus_doublegauss_fit(hist, fitrange, guess, funcname=funcname)

    raise ValueError('Unknown signal model {}'.format(model))


def _background_params_for_degree(paramdict, degree):
    background_params = {'a0': paramdict['a0'], 'a1': paramdict['a1']}
    if degree >= 2:
        background_params['a2'] = paramdict.get('a2', 0.)
    return background_params


def _make_signal_component(paramdict, model):
    if model == 'single':
        sigfit = ROOT.TF1('signal', 'gaus(0)')
        sigfit.SetParameters(paramdict['A'], paramdict['#mu'], paramdict['#sigma'])
        return sigfit

    if model == 'double':
        sigfit = ROOT.TF1('signal', 'gaus(0)+gaus(3)')
        sigfit.SetParameters(
            paramdict['A_{1}'], paramdict['#mu'], paramdict['#sigma_{1}'],
            paramdict['A_{2}'], paramdict['#mu'], paramdict['#sigma_{2}']
        )
        return sigfit

    raise ValueError('Unknown signal model {}'.format(model))


def _make_background_component(paramdict, degree):
    if degree == 1:
        backfit = ROOT.TF1('fitfunc', 'pol1(0)')
        backfit.SetParameters(paramdict['a0'], paramdict['a1'])
        return backfit

    backfit = ROOT.TF1('fitfunc', 'pol2(0)')
    backfit.SetParameters(paramdict['a0'], paramdict['a1'], paramdict['a2'])
    return backfit


def _select_best_candidate(candidates):
    best = None
    for candidate in candidates:
        if best is None:
            best = candidate
            continue
        if candidate['chi2_ndf'] < best['chi2_ndf']:
            best = candidate
    return best

# -------------------------------------------------------------------------------------
# Make background/signal fit and calculate event count:
#
#   Input arguments:  - hist = ROOT histogram to perform fitting on (left unmodified)
#                     - label = only for plotting
#                     - extrainfo = only for plotting
#                     - gargs = dict containgin global program parameters
#                     - mode = 'gfit' or 'subtract'
#                         or 'hybrid', which returns subtract results but makes fancy 'gfit' plot anyway
#   Return:           - return the integral (and error estimate) under a peak in a histogram, 
#                         subtracting the background contribution from sidebands
# -------------------------------------------------------------------------------------
def count_peak(hist, label, extrainfo, gargs, mode='subtract'):
    # initializations
    nbins           = hist.GetNbinsX()
    xlow            = hist.GetBinLowEdge(1)
    xhigh           = hist.GetBinLowEdge(nbins)+hist.GetBinWidth(nbins)
    fitrange        = (xlow, xhigh)
    fitcenter       = (xlow + xhigh)/2.     # Center of fit range
    fithalfwidth    = (xhigh - xlow)/4.     # differnce from center
    histclone       = hist.Clone()
    binlow          = histclone.FindBin(fitcenter-fithalfwidth)
    binhigh         = histclone.FindBin(fitcenter+fithalfwidth)

    # take into account only sidebands, not peak
    for i in range(binlow, binhigh):
        histclone.SetBinContent(i,0)
        histclone.SetBinError(i,0)
    # Threshold for choosing between single and double Gaussian
    singleGauss = 20000

    # make background-only fit
    # If more than 100 events     --> use linear background 
    # Else                        --> use quadratic background
    if(hist.GetEffectiveEntries() <= 1000): guess = [0., 0.]
    else:                                   guess = [0.,0.,0.]
    backfit, paramdict, backfitobj = ft.poly_fit(hist, fitrange, guess, "MSE0")
    
    if gargs['helpdir'] is not None:
        lumitext    = '' if gargs['lumi'] is None else '{0:.3g} '.format(float(gargs['lumi'])/1000.) + 'fb^{-1} (13.6 TeV)'
        outfile     = os.path.join(gargs['helpdir'], hist.GetName().replace(' ','_')+'_bck.png')
        pft.plot_fit(hist, outfile,
                fitfunc     =None, 
                backfit     =backfit, 
                label       =label, 
                paramdict   =paramdict,
                xaxtitle    ='Invariant mass (GeV)',
                yaxtitle    ='Number of reconstructed vertices',
                extrainfo   =extrainfo, 
                lumitext    =lumitext
        )

    # make signal peak fit if requested
    # subtract mode still needs the signal fit to estimate the peak integral
    if(mode=='gfit' or mode=='hybrid' or mode=='subtract'):
        # If more than 10000 events     --> use Double Gauss
        # Else                          --> use Single Gauss
        if(hist.GetEffectiveEntries() <= singleGauss):
            guess = [
                    fitcenter,                                                                                      # peak position
                    hist.GetMaximum()/2,                                                                            # peak 1 height
                    hist.GetRMS()                                                                                   # peak 1 width
            ]
            if(hist.GetEffectiveEntries() <= 1000): guess += [paramdict['a0'],paramdict['a1']]                      # background estimate
            else:                                   guess += [paramdict['a0'],paramdict['a1'], paramdict['a2']]     # background estimate
            #guess += [paramdict['a0'],paramdict['a1']]                     # background estimate
            
            globfit, paramdict, globfitobji, globres = ft.poly_plus_gauss_fit(hist, fitrange, guess)

        else:
            guess = [
                    fitcenter,                                              # peak position
                    hist.GetMaximum()/2,                                    # peak 1 height
                    hist.GetRMS()/4,                                        # peak 1 width
                    hist.GetMaximum()/2,                                    # peak 2 height
                    hist.GetRMS()                                           # peak 2 width
            ]
            if(hist.GetEffectiveEntries() <= 1000): guess += [paramdict['a0'],paramdict['a1']]                      # background estimate
            else:                                   guess += [paramdict['a0'],paramdict['a1'], paramdict['a2']]     # background estimate
           
            globfit, paramdict, globfitobj, globres = ft.poly_plus_doublegauss_fit(hist, fitrange, guess)
            print(paramdict) 
        
        # separate background component of fit
        if(hist.GetEffectiveEntries() <= 1000):  
            backfit2 = ROOT.TF1("fitfunc","pol1(0)", fitrange[0], fitrange[1])
            backfit2.SetParameters(paramdict['a0'], paramdict['a1'])
        else:
            backfit2 = ROOT.TF1("fitfunc","pol2(0)", fitrange[0], fitrange[1])
            backfit2.SetParameters(paramdict['a0'], paramdict['a1'], paramdict['a2'])
        
        if gargs['helpdir'] is not None:
            outfile = os.path.join(gargs['helpdir'], hist.GetName().replace(' ','_')+'_sig.png')
            pft.plot_fit(hist, outfile,
                    fitfunc     =globfit, 
                    backfit     =backfit2, 
                    label       =label, 
                    paramdict   =paramdict,
                    xaxtitle    ='Invariant mass (GeV)',
                    yaxtitle    ='Reconstructed vertices',
                    extrainfo   =extrainfo, 
                    lumitext    =lumitext,
                    sideband    =[fitcenter-fithalfwidth, fitcenter+fithalfwidth]
            )
    
    # ---------------------------------------------------------------------------------
    # Make single Gauss fit for L_xy confidence study:
    guess = [
        fitcenter,                              # peak position
        hist.GetMaximum()/2,                    # peak 1 height
        hist.GetRMS()                           # peak 1 width
    ]
    if(hist.GetEffectiveEntries() <= 1000): guess += [paramdict['a0'],paramdict['a1']]                      # background estimate
    else:                                   guess += [paramdict['a0'],paramdict['a1'], paramdict['a2']]     # background estimate
           
    globfit2, paramdict2, globfitobj2, globres2 = ft.poly_plus_gauss_fit(hist, fitrange, guess)
    
    # separate background component of fit
    if(hist.GetEffectiveEntries() <= 1000):  
        backfit3 = ROOT.TF1("fitfunc","pol1(0)", fitrange[0], fitrange[1])
        backfit3.SetParameters(paramdict['a0'], paramdict['a1'])
    else:
        backfit3 = ROOT.TF1("fitfunc","pol2(0)", fitrange[0], fitrange[1])
        backfit3.SetParameters(paramdict['a0'], paramdict['a1'], paramdict['a2'])
    
    if gargs['helpdir2'] is not None:
            outfile2 = os.path.join(gargs['helpdir2'], hist.GetName().replace(' ','_')+'_sig.png')
            pft.plot_fit(hist, outfile2,
                    fitfunc     =globfit2, 
                    backfit     =backfit3, 
                    label       =label, 
                    paramdict   =paramdict2,
                    xaxtitle    ='Invariant mass (GeV)',
                    yaxtitle    ='Reconstructed vertices',
                    extrainfo   =extrainfo, 
                    lumitext    =lumitext,
                    sideband    =[fitcenter-fithalfwidth, fitcenter+fithalfwidth]
            )
    # ---------------------------------------------------------------------------------
    
    # METHOD 1: subtract background from peak and count remaining instances
    if(mode=='subtract' or mode=='hybrid'):
        # Calculate the event count (integral) and statistical error
        if hist.GetEffectiveEntries()                           > 50:                               # Calculate integral
            if hist.GetEffectiveEntries()                       <= singleGauss: 
                sigfit                                          = ROOT.TF1("signal","gaus(0)")
                sigfit.SetParameters(paramdict[r'A'], paramdict[r'#mu'], paramdict[r'#sigma'])
                print(f'sigma = ', abs(globfit.GetParameter(2)), ' +- ', abs(globfit2.GetParError(2)))
            else:                                
                sigfit                                          = ROOT.TF1("signal","gaus(0)+gaus(3)")
                sigfit.SetParameters(paramdict[r'A_{1}'], paramdict[r'#mu'], paramdict[r'#sigma_{1}'],
                                                                paramdict[r'A_{2}'], paramdict[r'#mu'], paramdict[r'#sigma_{2}'])
                print(f'sigma_1 = ', abs(globfit.GetParameter(2)), ' +- ', abs(globfit2.GetParError(2)))
                print(f'sigma_2 = ', abs(globfit.GetParameter(4)), ' +- ', abs(globfit2.GetParError(4)))
            
            # Determine general fit parameters required for integration 
            params                                              = globres.GetParams()
            cov                                                 = globres.GetCovarianceMatrix()
            sidexbinwidth                                       = histclone.GetBinWidth(1)          # TODO: make more robust and general
           
            # calculate number of instances instead of integral
            
            # Subtract background (only if total fit worked but background fit failed)
            if backfit2.GetMinimum(fitrange[0],fitrange[1]) < -5:
                # calculate number of instances instead of integral
                npeak                                           = globfit.Integral(fitrange[0],fitrange[1]) / sidexbinwidth
                npeak_error                                     = globfit.IntegralError(fitrange[0],fitrange[1], params, cov.GetMatrixArray()) / sidexbinwidth
            else:
                npeak                                           = sigfit.Integral(fitrange[0],fitrange[1]) / sidexbinwidth
                npeak_error                                     = globfit.IntegralError(fitrange[0],fitrange[1], params, cov.GetMatrixArray()) / sidexbinwidth

            # Calculate peak width and error for confidence study
            confidence                                          = float(abs(globfit2.GetParameter(2)))
            conf_error                                          = float(abs(globfit2.GetParError(2)))

        else:                                                                                       # Cut and Count method
            histclone2                                          = hist.Clone()
            if backfit.GetMinimum(fitrange[0],fitrange[1]) > 0: histclone2.Add(backfit,-1)          # Subtract background (only if background fit is physical)
            npeak, npeak_error                                  = 0., 0.                            # Determine event count/statistical error
            
            # Count number of instances in each bin
            for i in range(0, nbins):
                npeak                                           += histclone2.GetBinContent(i)
                npeak_error                                     += np.power(histclone2.GetBinError(i),2)

            npeak_error                                         = np.sqrt(npeak_error)

            # Calculate peak width and error for confidence study
            confidence                                          = float(abs(histclone2.GetRMS()))
            conf_error                                          = float(abs(histclone2.GetRMSError()))
        
        print(f'Integral = ',   npeak,      ' +- ', npeak_error)
        print(f'Confidence = ', confidence, ' +- ', conf_error )

        return (npeak, npeak_error, confidence, conf_error)
        #return (npeak, npeak_error)

    # METHOD 2: do global fit and determine integral of peak with error
    elif mode=='gfit':
        if hist.GetEffectiveEntries() <= singleGauss:
            intpeak                                             = np.sqrt(2*np.pi) * paramdict['A'] * paramdict['#sigma']
        else:
            intpeak                                             = np.sqrt(2*np.pi)*(paramdict['A_{1}']*paramdict['#sigma_{1}']
                                                                                + paramdict['A_{2}']*paramdict['#sigma_{2}'])
        sidexbinwidth                                           = histclone.GetBinWidth(1)           # TODO: make more robust and general
        npeak                                                   = intpeak / sidexbinwidth            # calculate number of instances instead of integral
        npeak_error                                             = globfit.IntegralError(fitrange[0],fitrange[1]) / sidexbinwidth
        
        return (npeak, npeak_error, confidence, conf_error)
        #return (npeak, npeak_error)

    else:
        raise Exception('ERROR: peak counting mode not regognized!')


def count_peak_adaptive(hist, label, extrainfo, gargs, mode='subtract', return_metadata=False):
    # initializations
    nbins           = hist.GetNbinsX()
    xlow            = hist.GetBinLowEdge(1)
    xhigh           = hist.GetBinLowEdge(nbins)+hist.GetBinWidth(nbins)
    fitrange        = (xlow, xhigh)
    fitcenter       = (xlow + xhigh)/2.
    fithalfwidth    = (xhigh - xlow)/4.
    histclone       = hist.Clone()
    binlow          = histclone.FindBin(fitcenter-fithalfwidth)
    binhigh         = histclone.FindBin(fitcenter+fithalfwidth)

    for i in range(binlow, binhigh):
        histclone.SetBinContent(i,0)
        histclone.SetBinError(i,0)

    # background-only fits: use the best one as seed and for cut-and-count fallback
    backfit_candidates = []
    for degree, guess, funcname in (
        (1, [0., 0.], 'backfit_pol1'),
        (2, [0., 0., 0.], 'backfit_pol2'),
    ):
        fitfunc, paramdict, fitobj = ft.poly_fit(histclone, fitrange, guess, "MSE0", funcname=funcname)
        fitres = fitfunc
        chi2, ndf, chi2ndf = _fit_quality(fitfunc)
        backfit_candidates.append({
            'degree': degree,
            'fitfunc': fitfunc,
            'paramdict': paramdict,
            'fitobj': fitobj,
            'fitres': fitres,
            'chi2': chi2,
            'ndf': ndf,
            'chi2_ndf': chi2ndf,
        })

    best_backfit = _select_best_candidate(backfit_candidates)
    best_backfit_params = best_backfit['paramdict']
    best_backfit_degree = best_backfit['degree']
    backfit = best_backfit['fitfunc']
    paramdict = best_backfit_params

    print('Adaptive background fit: degree {} with chi2/ndf = {:.4g}/{:d} = {:.4g}'.format(
        best_backfit_degree, best_backfit['chi2'], best_backfit['ndf'], best_backfit['chi2_ndf']))

    if gargs['helpdir'] is not None:
        lumitext    = '' if gargs['lumi'] is None else '{0:.3g} '.format(float(gargs['lumi'])/1000.) + 'fb^{-1} (13.6 TeV)'
        outfile     = os.path.join(gargs['helpdir'], hist.GetName().replace(' ','_')+'_bck.png')
        pft.plot_fit(hist, outfile,
                fitfunc     =None,
                backfit     =backfit,
                label       =label,
                paramdict   =paramdict,
                xaxtitle    ='Invariant mass (GeV)',
                yaxtitle    ='Number of reconstructed vertices',
                extrainfo   =extrainfo,
                lumitext    =lumitext
        )

    need_signal_fit = (mode == 'gfit' or mode == 'hybrid' or hist.GetEffectiveEntries() > 50)
    best_signal = None
    best_confidence = None

    if need_signal_fit:
        signal_candidates = []
        confidence_candidates = []

        for background_degree in (1, 2):
            background_seed = _background_params_for_degree(best_backfit_params, background_degree)
            for model in ('single', 'double'):
                funcname = 'adaptive_{}_pol{}'.format(model, background_degree)
                fitfunc, fitparamdict, fitobj, fitres = _make_signal_fit(
                    hist, fitrange, fitcenter, model, background_seed, background_degree, funcname
                )
                chi2, ndf, chi2ndf = _fit_quality(fitfunc)
                signal_candidates.append({
                    'model': model,
                    'background_degree': background_degree,
                    'fitfunc': fitfunc,
                    'paramdict': fitparamdict,
                    'fitobj': fitobj,
                    'fitres': fitres,
                    'chi2': chi2,
                    'ndf': ndf,
                    'chi2_ndf': chi2ndf,
                })

            conf_funcname = 'adaptive_confidence_pol{}'.format(background_degree)
            conf_fitfunc, conf_paramdict, conf_fitobj, conf_fitres = _make_signal_fit(
                hist, fitrange, fitcenter, 'single', background_seed, background_degree, conf_funcname
            )
            conf_chi2, conf_ndf, conf_chi2ndf = _fit_quality(conf_fitfunc)
            confidence_candidates.append({
                'model': 'single',
                'background_degree': background_degree,
                'fitfunc': conf_fitfunc,
                'paramdict': conf_paramdict,
                'fitobj': conf_fitobj,
                'fitres': conf_fitres,
                'chi2': conf_chi2,
                'ndf': conf_ndf,
                'chi2_ndf': conf_chi2ndf,
            })

        best_signal = _select_best_candidate(signal_candidates)
        best_confidence = _select_best_candidate(confidence_candidates)

        globfit = best_signal['fitfunc']
        paramdict = best_signal['paramdict']
        globfitobj = best_signal['fitobj']
        globres = best_signal['fitres']
        signal_model = best_signal['model']
        signal_background_degree = best_signal['background_degree']

        globfit2 = best_confidence['fitfunc']
        paramdict2 = best_confidence['paramdict']
        globfitobj2 = best_confidence['fitobj']
        globres2 = best_confidence['fitres']
        confidence_background_degree = best_confidence['background_degree']

        print('Adaptive signal fit: {} + pol{} with chi2/ndf = {:.4g}/{:d} = {:.4g}'.format(
            signal_model, signal_background_degree, best_signal['chi2'], best_signal['ndf'], best_signal['chi2_ndf']))
        print('Adaptive confidence fit: single + pol{} with chi2/ndf = {:.4g}/{:d} = {:.4g}'.format(
            confidence_background_degree, best_confidence['chi2'], best_confidence['ndf'], best_confidence['chi2_ndf']))

        backfit2 = _make_background_component(paramdict, signal_background_degree)
        backfit3 = _make_background_component(paramdict2, confidence_background_degree)

        if gargs['helpdir'] is not None:
            lumitext    = '' if gargs['lumi'] is None else '{0:.3g} '.format(float(gargs['lumi'])/1000.) + 'fb^{-1} (13.6 TeV)'
            outfile = os.path.join(gargs['helpdir'], hist.GetName().replace(' ','_')+'_sig.png')
            pft.plot_fit(hist, outfile,
                    fitfunc     =globfit,
                    backfit     =backfit2,
                    label       =label,
                    paramdict   =paramdict,
                    xaxtitle    ='Invariant mass (GeV)',
                    yaxtitle    ='Reconstructed vertices',
                    extrainfo   =extrainfo,
                    lumitext    =lumitext,
                    sideband    =[fitcenter-fithalfwidth, fitcenter+fithalfwidth]
            )

        if gargs['helpdir2'] is not None:
                lumitext    = '' if gargs['lumi'] is None else '{0:.3g} '.format(float(gargs['lumi'])/1000.) + 'fb^{-1} (13.6 TeV)'
                outfile2 = os.path.join(gargs['helpdir2'], hist.GetName().replace(' ','_')+'_sig.png')
                pft.plot_fit(hist, outfile2,
                        fitfunc     =globfit2,
                        backfit     =backfit3,
                        label       =label,
                        paramdict   =paramdict2,
                        xaxtitle    ='Invariant mass (GeV)',
                        yaxtitle    ='Reconstructed vertices',
                        extrainfo   =extrainfo,
                        lumitext    =lumitext,
                        sideband    =[fitcenter-fithalfwidth, fitcenter+fithalfwidth]
                )

    # ---------------------------------------------------------------------------------
    # Make single Gauss fit for L_xy confidence study if it was not already built above:
    if not need_signal_fit:
        confidence_candidates = []
        for background_degree in (1, 2):
            background_seed = _background_params_for_degree(best_backfit_params, background_degree)
            conf_funcname = 'adaptive_confidence_pol{}'.format(background_degree)
            conf_fitfunc, conf_paramdict, conf_fitobj, conf_fitres = _make_signal_fit(
                hist, fitrange, fitcenter, 'single', background_seed, background_degree, conf_funcname
            )
            conf_chi2, conf_ndf, conf_chi2ndf = _fit_quality(conf_fitfunc)
            confidence_candidates.append({
                'model': 'single',
                'background_degree': background_degree,
                'fitfunc': conf_fitfunc,
                'paramdict': conf_paramdict,
                'fitobj': conf_fitobj,
                'fitres': conf_fitres,
                'chi2': conf_chi2,
                'ndf': conf_ndf,
                'chi2_ndf': conf_chi2ndf,
            })
        best_confidence = _select_best_candidate(confidence_candidates)
        globfit2 = best_confidence['fitfunc']
        paramdict2 = best_confidence['paramdict']
        globfitobj2 = best_confidence['fitobj']
        globres2 = best_confidence['fitres']
        confidence_background_degree = best_confidence['background_degree']
        backfit3 = _make_background_component(paramdict2, confidence_background_degree)

    # ---------------------------------------------------------------------------------

    if mode == 'subtract' or mode == 'hybrid':
        if hist.GetEffectiveEntries() > 50 and best_signal is not None:
            sigfit = _make_signal_component(paramdict, signal_model)

            params = globres.GetParams()
            cov = globres.GetCovarianceMatrix()
            sidexbinwidth = histclone.GetBinWidth(1)

            if backfit2.GetMinimum(fitrange[0],fitrange[1]) < -5:
                npeak = globfit.Integral(fitrange[0],fitrange[1]) / sidexbinwidth
                npeak_error = globfit.IntegralError(fitrange[0],fitrange[1], params, cov.GetMatrixArray()) / sidexbinwidth
            else:
                npeak = sigfit.Integral(fitrange[0],fitrange[1]) / sidexbinwidth
                npeak_error = globfit.IntegralError(fitrange[0],fitrange[1], params, cov.GetMatrixArray()) / sidexbinwidth

            confidence = float(abs(globfit2.GetParameter(2)))
            conf_error = float(abs(globfit2.GetParError(2)))
        else:
            histclone2 = hist.Clone()
            if backfit.GetMinimum(fitrange[0],fitrange[1]) > 0:
                histclone2.Add(backfit,-1)
            npeak, npeak_error = 0., 0.

            for i in range(0, nbins):
                npeak += histclone2.GetBinContent(i)
                npeak_error += np.power(histclone2.GetBinError(i),2)

            npeak_error = np.sqrt(npeak_error)
            confidence = float(abs(histclone2.GetRMS()))
            conf_error = float(abs(histclone2.GetRMSError()))

        print(f'Integral = ',   npeak,      ' +- ', npeak_error)
        print(f'Confidence = ', confidence, ' +- ', conf_error )

        result = (npeak, npeak_error, confidence, conf_error)
        if return_metadata and best_signal is not None:
            return {
                'peak_count': npeak,
                'peak_error': npeak_error,
                'confidence': confidence,
                'conf_error': conf_error,
                'background_model': 'pol{}'.format(best_backfit_degree),
                'signal_model': signal_model,
                'background_chi2': best_backfit['chi2'],
                'background_ndf': best_backfit['ndf'],
                'background_chi2_ndf': best_backfit['chi2_ndf'],
                'signal_chi2': best_signal['chi2'],
                'signal_ndf': best_signal['ndf'],
                'signal_chi2_ndf': best_signal['chi2_ndf'],
                'confidence_chi2': best_confidence['chi2'],
                'confidence_ndf': best_confidence['ndf'],
                'confidence_chi2_ndf': best_confidence['chi2_ndf'],
            }
        return result

    elif mode == 'gfit':
        sigfit = _make_signal_component(paramdict, signal_model if best_signal is not None else 'single')
        if signal_model == 'single':
            intpeak = np.sqrt(2*np.pi) * paramdict['A'] * paramdict[r'#sigma']
        else:
            intpeak = np.sqrt(2*np.pi) * (paramdict['A_{1}']*paramdict[r'#sigma_{1}'] + paramdict['A_{2}']*paramdict[r'#sigma_{2}'])

        sidexbinwidth = histclone.GetBinWidth(1)
        npeak = intpeak / sidexbinwidth
        npeak_error = globfit.IntegralError(fitrange[0],fitrange[1]) / sidexbinwidth

        confidence = float(abs(globfit2.GetParameter(2)))
        conf_error = float(abs(globfit2.GetParError(2)))

        result = (npeak, npeak_error, confidence, conf_error)
        if return_metadata and best_signal is not None:
            return {
                'peak_count': npeak,
                'peak_error': npeak_error,
                'confidence': confidence,
                'conf_error': conf_error,
                'background_model': 'pol{}'.format(best_backfit_degree),
                'signal_model': signal_model,
                'background_chi2': best_backfit['chi2'],
                'background_ndf': best_backfit['ndf'],
                'background_chi2_ndf': best_backfit['chi2_ndf'],
                'signal_chi2': best_signal['chi2'],
                'signal_ndf': best_signal['ndf'],
                'signal_chi2_ndf': best_signal['chi2_ndf'],
                'confidence_chi2': best_confidence['chi2'],
                'confidence_ndf': best_confidence['ndf'],
                'confidence_chi2_ndf': best_confidence['chi2_ndf'],
            }
        return result

    else:
        raise Exception('ERROR: peak counting mode not regognized!')


def count_peak_compare(hist, label, extrainfo, gargs, mode='subtract'):
    compare_gargs = dict(gargs)
    compare_gargs['helpdir'] = None
    compare_gargs['helpdir2'] = None
    
    # Get adaptive result with metadata
    adaptive_result = count_peak_adaptive(hist, label, extrainfo, compare_gargs, mode=mode, return_metadata=True)
    
    # Get legacy result
    legacy_tuple = count_peak(hist, label, extrainfo, compare_gargs, mode=mode)
    
    # Infer legacy model choice based on effective entries (same logic as count_peak)
    effective_entries = hist.GetEffectiveEntries()
    legacy_background_model = 'pol1' if effective_entries <= 1000 else 'pol2'
    legacy_signal_model = 'single' if effective_entries <= 20000 else 'double'
    
    legacy_result = {
        'peak_count': legacy_tuple[0],
        'peak_error': legacy_tuple[1],
        'confidence': legacy_tuple[2],
        'conf_error': legacy_tuple[3],
        'background_model': legacy_background_model,
        'signal_model': legacy_signal_model,
        'background_chi2': None,  # Not tracked in legacy
        'background_ndf': None,
        'background_chi2_ndf': None,
        'signal_chi2': None,
        'signal_ndf': None,
        'signal_chi2_ndf': None,
        'confidence_chi2': None,
        'confidence_ndf': None,
        'confidence_chi2_ndf': None,
    }
    
    return {
        'legacy': legacy_result,
        'adaptive': adaptive_result,
        'mode': mode,
        'label': label,
        'extrainfo': extrainfo,
        'histogram_name': hist.GetName(),
        'effective_entries': effective_entries,
    }

# -------------------------------------------------------------------------------------
# Wrap around fit function:
#   wrapper around fitting function using more modern paradigm for input parameters
#   Input:  - values: np array of sideband values
#           - weights: np array of weights corresponding to values
#           - variable: dict with all information about the sideband variable
#           - mode: passed down to called function
# -------------------------------------------------------------------------------------
def count_peak_unbinned(values, weights, variable, mode='subtract',
                        label=None, lumi=None, extrainfo=None,
                        histname='sideband', plotdir=None,
                        fit_strategy='legacy'):
    # make a ROOT histogram with the values and weights
    counts  = np.histogram(values, variable['bins'], weights=weights)[0]
    errors  = np.sqrt(np.histogram(values, variable['bins'], weights=np.power(weights,2))[0])
    
    hist    = ROOT.TH1F(histname, histname, len(variable['bins'])-1, array('f', variable['bins']))
    hist.SetDirectory(0)
    for i, (count, error) in enumerate(zip(counts, errors)):
      hist.SetBinContent(   i+1, count)
      hist.SetBinError(     i+1, error)

    # make directory to store plots
    singleGaussdir = None
    if plotdir is not None:
        singleGaussdir = os.path.join(plotdir, 'singleGauss')
        if not os.path.exists(plotdir):
            os.makedirs(plotdir)
        if not os.path.exists(singleGaussdir):
            os.makedirs(singleGaussdir)

    # make a dictionary with extra fit info
    fitinfo                 = {}
    fitinfo['lumi']         = lumi
    fitinfo['helpdir']      = plotdir
    fitinfo['helpdir2']     = singleGaussdir
    fitinfo['fitstrategy']  = fit_strategy

    # decorate extrainfo so plots display which fit strategy was used
    if extrainfo is None:
        extrainfo = ''
    if fit_strategy is not None:
        extrainfo = 'Fit strategy: {}<<'.format(fit_strategy) + extrainfo
    
    # call underlying function
    if fit_strategy == 'adaptive':
        return count_peak_adaptive(hist, label, extrainfo, fitinfo, mode=mode)
    if fit_strategy == 'compare':
        return count_peak_compare(hist, label, extrainfo, fitinfo, mode=mode)

    return count_peak(hist, label, extrainfo, fitinfo, mode=mode)
