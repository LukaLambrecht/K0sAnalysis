##########################################################
# Make invariant mass plots and fits of kshort or lambda #
##########################################################

import sys 
import os
import json
import argparse
import uproot
import numpy as np
import ROOT
from array import array
sys.path.append('../tools')
import fittools as ft
sys.path.append('../plotting')
import plotfit as pf

if __name__=='__main__':
    
  # read command line arguments
  parser = argparse.ArgumentParser( description = 'Plot invariant mass' )
  parser.add_argument('-i', '--inputfile', required=True, nargs='+')
  parser.add_argument('-t', '--treename', required=True)
  parser.add_argument('-v', '--variable', required=True, type=os.path.abspath)
  parser.add_argument('-o', '--outputfile', required=True, type=os.path.abspath)
  parser.add_argument('-n', '--nentries', default=-1, type=int)
  parser.add_argument('--isdata', default=False, action='store_true')
  parser.add_argument('--lumi', default=None, type=float)
  parser.add_argument('--xsection', default=None, type=float)
  parser.add_argument('--label', default=None)
  parser.add_argument('--unit', default='GeV', choices=['GeV','MeV'])
  parser.add_argument('--yvariable', default=None)
  parser.add_argument('--doplot', default=False, action='store_true')
  # options below are only for plot aesthetics, not relevant when doplot is False
  parser.add_argument('--title', default=None)
  parser.add_argument('--xaxtitle', default=None) # can use 'auto' for basic automatic option
  parser.add_argument('--yaxtitle', default=None) # can use 'auto' for basic automatic option
  parser.add_argument('--lumilabel', default=None)
  parser.add_argument('--drawstyle', default='hist')
  parser.add_argument('--show_bkg_fit', default=False, action='store_true')
  parser.add_argument('--show_sig_fit', default=False, action='store_true')
  parser.add_argument('--show_sideband', default=False, action='store_true')
  parser.add_argument('--show_fit_params', default=False, action='store_true')
  parser.add_argument('--polydegree', type=int, default=1)
  args = parser.parse_args()

  # load main variable
  with open(args.variable) as f:
    variable = json.load(f)
  print('Found following main variable:')
  for key,val in variable.items(): print('  {}: {}'.format(key,val))

  # modifiy bins if display units are different from default
  if args.unit=='MeV': variable['bins'] = [binedge*1000 for binedge in variable['bins']]

  # load sideband variable
  yvariable = None # default case if no secondary binning
  if args.yvariable is not None:
    with open(args.yvariable) as f:
      yvariable = json.load(f)
    print('Found following secondary variable:')
    for key,val in yvariable.items(): print('  {}: {}'.format(key,val))

  # loop over input files
  # (usually there will be just one input file,
  #  but multiple are possible e.g. to make quick run-2 plots for data;
  #  this will not work correctly for simulation as different xsection and lumi values are needed!)
  for inputfile in args.inputfile:
    # open the file and read hcounter
    print('Now running on file {}...'.format(inputfile))
    with uproot.open(inputfile) as f:
      sumweights = 1 # default case for data, overwritten for simulation below
      if not args.isdata:
        try: sumweights = f[hcountername].values()[0]
        except:
          msg = 'WARNING: isdata was set to False, but no valid hCounter found in file'
          msg += ' (for provided key {}),'.format(hcountername)
          msg += ' will use sum of weights = 1 for this sample.'
          msg += ' Valid keys are {}'.format(f.keys())
          print(msg)

      # get main tree and manage number of entries
      tree = f[args.treename]
      nentries = tree.num_entries
      nentries_reweight = 1.
      if( args.nentries is not None and args.nentries>0 and args.nentries<tree.num_entries ):
        nentries = args.nentries
        nentries_reweight = tree.num_entries / nentries
      msg = 'Tree {} was found to have {} entries,'.format(args.treename, tree.num_entries)
      msg += ' of which {} will be read (using reweighting factor {}).'.format(nentries, nentries_reweight)
      print(msg)

      # get weights
      if args.isdata: weights = np.ones(nentries)
      else:
        weights = tree[weightvarname].array(library='np', entry_stop=nentries)
        weights = weights / sumweights * args.xsection * args.lumi
      weights = weights * nentries_reweight

      # get the variable and some masks
      varvalues = tree[variable['variable']].array(library='np', entry_stop=nentries)
      if args.unit=='MeV': varvalues = varvalues*1000
      nanmask = np.isnan(varvalues)
      rangemask = ((varvalues > variable['bins'][0]) & (varvalues < variable['bins'][-1]))
      totalmask = ((~nanmask) & rangemask)

      # initialize a dummy secondary variable if it was not provided
      # (easier than if else statements below)
      dim = 1
      if args.yvariable is not None: dim = 2
      else:
        dummyvar = tree.keys()[0]
        dummyvalues = tree[dummyvar].array(library='np', entry_stop=nentries)
        dummymin = np.min(dummyvalues)
        dummymax = np.max(dummyvalues)
        yvariable = {'variable': dummyvar, 'bins': [dummymin/2., dummymax*2]}

      # get the secondary variable
      yvarvalues = tree[yvariable['variable']].array(library='np', entry_stop=nentries)
      ynanmask = np.isnan(yvarvalues)
      yrangemask = ((yvarvalues >= yvariable['bins'][0]) & (yvarvalues <= yvariable['bins'][-1]))
      totalmask = (totalmask & (~ynanmask) & yrangemask)

      # calculate the counts
      varvalues = varvalues[totalmask]
      yvarvalues = yvarvalues[totalmask]
      weights = weights[totalmask]
      counts = np.histogram2d(varvalues, yvarvalues,
                   bins=(variable['bins'], yvariable['bins']),
                   weights=weights)[0]
      errors = np.sqrt(np.histogram2d(varvalues, yvarvalues,
                   bins=(variable['bins'], yvariable['bins']),
                   weights=np.power(weights,2))[0])

  # write histograms to output file
  hists = []
  for i, (ylow, yhigh) in enumerate(zip(yvariable['bins'][:-1], yvariable['bins'][1:])):
    # make a ROOT histogram
    if args.label is not None: histname = 'hist_{}_{}'.format(args.label,i)
    else: histname = 'hist_{}'.format(i)
    hist = ROOT.TH1F(histname, histname, len(variable['bins'])-1, array('f', variable['bins']))
    hist.SetDirectory(0)
    for binnb, (count, error) in enumerate(zip(counts[:,i], errors[:,i])):
      hist.SetBinContent(binnb+1, count)
      hist.SetBinError(binnb+1, error)
    hists.append(hist)
  outrootfile = os.path.splitext(args.outputfile)[0]+'.root'
  f = ROOT.TFile.Open(outrootfile, 'recreate')
  for hist in hists: hist.Write()
  f.Close()
  
  # exit if no plot is needed  
  if not args.doplot: sys.exit()
  
  # loop over secondary bins
  for i, (ylow, yhigh) in enumerate(zip(yvariable['bins'][:-1], yvariable['bins'][1:])):
    hist = hists[i]

    # fit range settings
    xlow = variable['bins'][0]
    xhigh = variable['bins'][-1]
    fitrange = [xlow, xhigh]
    xcenter = (xhigh + xlow)/2.
    xwidth = (xhigh - xlow)/4.

    # remove middle band and fit sidebands to obtain background
    histclone = hist.Clone()
    binlow = histclone.FindBin(xcenter-xwidth)
    binhigh = histclone.FindBin(xcenter+xwidth)
    for binnb in range(binlow,binhigh):
        histclone.SetBinContent(binnb,0)
        histclone.SetBinError(binnb,0)
    guess = [0.]*(args.polydegree+1)
    bkgfit, paramdict, fitobj1 = ft.poly_fit(histclone,fitrange,guess,"Q0")
    average = bkgfit.Eval(xcenter)
    
    # do simultaneous fit with previous fit parameters as initial guesses
    sigma_1_init = 0.005
    sigma_2_init = 0.01
    if args.unit=='MeV':
        sigma_1_init *= 1000
        sigma_2_init *= 1000
    guess = [xcenter, average*10, sigma_1_init, average*10, sigma_2_init]
    for degree in range(args.polydegree+1):
        guess.append(paramdict["a"+str(degree)])
    totfit, paramdict, fitobj2 = ft.poly_plus_doublegauss_fit(hist,fitrange,guess)
    print('Fitted parameters:')
    for el in paramdict: print('    '+el+': '+str(paramdict[el]))
    print('Fit quality:')
    print('    chi2: {}'.format(totfit.GetChisquare()))
    print('    degrees of freedom: {}'.format(totfit.GetNDF()))

    # temp for testing: check chi2 with manual computation
    testchi2 = 0
    for i in range(1, hist.GetNbinsX()+1):
        obs = hist.GetBinContent(i)
        exp = totfit.Eval(hist.GetBinCenter(i))
        testchi2 += (obs-exp)**2/exp
    print('Manual chi2 (for testing): {}'.format(testchi2))

    # also get uncertainty on best-fit value for mass
    # not very clean, maybe improve later
    idx = 0
    for paramidx, paramname in enumerate(paramdict.keys()):
        if paramname=='#mu': idx = paramidx
    mu_central = totfit.GetParameter(idx)
    mu_unc = totfit.GetParError(idx)

    # make extra info
    extrainfo = ''
    if args.show_sig_fit:
        if args.unit=='GeV':
            mu_central *= 1000
            mu_unc *= 1000
        extrainfo += 'Fitted K_{S}^{0} mass: <<  '
        extrainfo += '{:.3f} #pm {:.3f} MeV << <<'.format(mu_central, mu_unc)
    #extrainfo += ' << <<HACK_KS'
    if dim==2:
        extrainfo += '{0:.2f} < '.format(ylow)
        extrainfo += yvariable['name']
        extrainfo += ' < {0:.2f}'.format(yhigh)

    # format the axis titles
    # note: the bin width is added to the y-axis title (on request),
    #       this assumes all bins have equal width...
    if(args.xaxtitle is not None and args.xaxtitle=='auto'):
        args.xaxtitle = 'Invariant mass (GeV)'
    if(args.yaxtitle is not None and args.yaxtitle=='auto'):
        binwidth = variable['bins'][1] - variable['bins'][0]
        if args.unit=='GeV': binwdith = binwidth*1000
        args.yaxtitle = 'Reconstructed vertices (/ {:.0f} MeV)'.format(binwidth)

    # format lumi header
    lumitext = ''
    if args.lumilabel is not None: lumitext += args.lumilabel
    elif args.lumi is not None: lumitext = '{0:.3g} '.format(float(args.lumi)/1000.) + 'fb^{-1} (13 TeV)'

    # settings for sideband indications
    sidebandxcoords = None
    if args.show_sideband:
        sidebandxcoords = [xcenter-xwidth, xcenter+xwidth]

    # make a plot
    if not args.show_bkg_fit: bkgfit = None
    if not args.show_sig_fit: totfit = None
    if not args.show_fit_params: paramdict = None
    outputfile = os.path.splitext(args.outputfile)[0]
    if len(yvariable['bins'])>2: outputfile += '_{}'.format(i)
    outputfile += '.png'
    pf.plot_fit(hist, outputfile,
                style=args.drawstyle, fitfunc=totfit, backfit=bkgfit,
                label=args.label, paramdict=paramdict,
                xaxtitle=args.xaxtitle, yaxtitle=args.yaxtitle,
                extrainfo=extrainfo,
                extracmstext='Preliminary',
                lumitext=lumitext,
                sideband=sidebandxcoords)
    outputfile = os.path.splitext(outputfile)[0] + '.pdf'
    pf.plot_fit(hist, outputfile,
                style=args.drawstyle, fitfunc=totfit, backfit=bkgfit,
                label=args.label, paramdict=paramdict,
                xaxtitle=args.xaxtitle, yaxtitle=args.yaxtitle,
                extrainfo=extrainfo,
                extracmstext='Preliminary',
                lumitext=lumitext,
                sideband=sidebandxcoords)
