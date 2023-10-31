########################################################################################
# count the number of instances in an invariant mass peak after background subtraction #
########################################################################################
# note: used in mcvsdata_fill.py and mcvsdata_fill2d.py
#       moved here to be able to use it common for both
import ROOT
import sys
import os
import numpy as np
sys.path.append(os.path.abspath('../tools'))
import fittools as ft
sys.path.append(os.path.abspath('../plotting'))
import plotfit as pft

ROOT.gROOT.SetBatch(ROOT.kTRUE)
def count_peak(hist,label,extrainfo,gargs,mode='subtract'):
    ### return the integral (and error estimate) under a peak in a histogram, 
    ### subtracting the background contribution from sidebands
    # input arguments:
    # - hist = histogram to perform fitting on (left unmodified)
    # - label = only for plotting
    # - extrainfo = only for plotting
    # - gargs = dict containgin global program parameters
    # - mode = 'gfit' or 'subtract'
    #           or 'hybrid', which returns subtract results but makes fancy 'gfit' plot anyway

    histclone = hist.Clone()
    binlow = histclone.FindBin(gargs['sidexcenter']-gargs['sidexwidth'])
    binhigh = histclone.FindBin(gargs['sidexcenter']+gargs['sidexwidth'])
    # take into account only sidebands, not peak
    for i in range(binlow+1,binhigh+1):
        histclone.SetBinContent(i,0)
        histclone.SetBinError(i,0)
    # make background-only fit
    guess = [0.,0.]
    backfit,paramdict = ft.poly_fit(histclone,gargs['fitrange'],guess,"Q0")
    pft.plot_fit(hist,os.path.join(gargs['helpdir'],hist.GetName().replace(' ','_')+'_bck.png'),
                fitfunc=None,backfit=backfit,label=label,paramdict=paramdict,
                xaxtitle='invariant mass (GeV)',
                yaxtitle='number of reconstructed vertices',
                extrainfo=extrainfo,lumi=gargs['lumi'])
    # make signal peak fit if requested
    if(mode=='gfit' or mode=='hybrid'):
        avgbck = paramdict['a0']+0.5*gargs['sidexcenter']*paramdict['a1']
        sidexbinwidth = (gargs['sidexhigh']-gargs['sidexlow'])/gargs['sidenbins']
        guess = [
                gargs['sidexcenter'], # peak position
                avgbck*10, # peak 1 height
                (gargs['sidexhigh']-gargs['sidexlow'])/45., # peak 1 width
                avgbck*10, # peak 2 height
                (gargs['sidexhigh']-gargs['sidexlow'])/15. # peak 2 width
                ]
        guess += [paramdict['a0'],paramdict['a1']] # background estimate
        globfit,paramdict = ft.poly_plus_doublegauss_fit(hist,gargs['fitrange'],guess)
        pft.plot_fit(hist,os.path.join(gargs['helpdir'],hist.GetName().replace(' ','_')+'_sig.png'),
                    fitfunc=globfit,backfit=backfit,label=label,paramdict=paramdict,
                    xaxtitle='invariant mass (GeV)',
                    yaxtitle='number of reconstructed vertices',
                    extrainfo=extrainfo,lumi=gargs['lumi'])

    # METHOD 1: subtract background from peak and count remaining instances
    if(mode=='subtract' or mode=='hybrid'):
        histclone2 = hist.Clone()
        histclone2.Add(backfit,-1)
        npeak = 0.
        npeak_error2 = 0.
        for i in range(binlow+1,binhigh+1):
            npeak += histclone2.GetBinContent(i)
            npeak_error2 += np.power(histclone2.GetBinError(i),2)
        return (npeak,np.sqrt(npeak_error2))

    # METHOD 2: do global fit and determine integral of peak with error
    elif mode=='gfit':
        intpeak = np.sqrt(2*np.pi)*(paramdict['A_{1}']*paramdict['#sigma_{1}']
                                        + paramdict['A_{2}']*paramdict['#sigma_{2}'])
        npeak = intpeak/sidexbinwidth # calculate number of instances instead of integral
        npeak_error = globfit.IntegralError(gargs['fitrange'][0],gargs['fitrange'][1])
        npeak_error /= sidexbinwidth
        return (npeak,npeak_error)

    else:
        print('### WARNING ###: peak counting mode not regognized!')
        return (0,0)
