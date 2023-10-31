#######################################################
# Make a plot of the deltaR separation between tracks #
#######################################################

import sys
import os
import json
import argparse
import ROOT
sys.path.append(os.path.abspath('../../tools'))
sys.path.append(os.path.abspath('../../plotting'))
from plotvarfromtree import fillvarfromtree
from multihistplotter import plotmultihistograms

if __name__=='__main__':

  parser = argparse.ArgumentParser( description = 'Make V0 plots' )
  parser.add_argument('--inputfile', required=True, type=os.path.abspath)
  parser.add_argument('--treename', required=True)
  parser.add_argument('--outputfile', required=True, type=os.path.abspath)
  parser.add_argument('--nprocess', type=int, default=-1)
  parser.add_argument('--extrainfos', default=None)
  parser.add_argument('--normalize', default=False, action='store_true')
  args = parser.parse_args()

  # define the variables
  if args.treename=='laurelin':
    drvar = {
      "name": '_KsDeltaR',
      "xlow": 0.0,
      "xhigh": 0.5,
      "nbins": 50,
      "xaxtitle": '#DeltaR(#pi^{+},#pi^{-})',
      "yaxtitle": 'Number of candidates',
    }
    ptvar = '_KsPt'
    #ptbins = [0.,2.5,5.,7.5,10.,100.]
    ptbins = [0.,100.]
  else:
    raise Exception('ERROR: dR variable not defined for tree {}'.format(args.treename))

  # parse extra info
  extrainfos = None
  if args.extrainfos is not None:
    extrainfos = args.extrainfos.split(',')

  # read the input tree
  fin = ROOT.TFile.Open(args.inputfile)
  tree = fin.Get(args.treename)

  # loop over pt splits
  histlist = []
  for ptindex in range(len(ptbins)-1):
  
    # make output histogram
    hist = ROOT.TH1F('hist','hist', drvar['nbins'], drvar['xlow'], drvar['xhigh'])
    hist.SetDirectory(0)
    hist.Sumw2()

    # set number of events to process
    nprocess = args.nprocess
    if( args.nprocess<0 or args.nprocess>tree.GetEntries() ): nprocess=tree.GetEntries()
    print('{} out of {} events will be processed'.format(nprocess,tree.GetEntries()))

    # loop over events
    for i in range(nprocess):
        if( i%10000==0 ):
            print('number of processed events: '+str(i))
        tree.GetEntry(i)
        # apply pt selection
        if getattr(tree,ptvar) < ptbins[ptindex]: continue
        if getattr(tree,ptvar) > ptbins[ptindex+1]: continue
        # determine value for requested variable in this entry
        varvalue = getattr(tree,drvar['name'])
        # fill the histogram
        hist.Fill(varvalue)

    # determine the label
    if ptindex==0: label = 'p_{T} < ' + '{} GeV'.format(ptbins[1])
    elif ptindex==len(ptbins)-2: label = 'p_{T} > ' + '{} GeV'.format(ptbins[-2])
    else: label = '{}'.format(ptbins[ptindex]) + ' < p_{T} < ' + '{} GeV'.format(ptbins[ptindex+1])
    hist.SetTitle(label)

    # add histogram to list
    histlist.append(hist)

  # define plot settings
  xaxtitle = drvar.get('xaxtitle',None)
  yaxtitle = drvar.get('yaxtitle',None)
  if args.normalize: yaxtitle = 'Arbitrary units'
  title = drvar.get('title',None)
  #infoleft = 0.7
  infoleft = None
  #infotop = 0.65
  infotop = 0.75

  # plot the histogram
  plotmultihistograms( histlist,
            figname=args.outputfile, title=title, xaxtitle=xaxtitle, yaxtitle=yaxtitle,
            normalize=args.normalize,
            dolegend=(len(histlist)>1), labellist=[hist.GetTitle() for hist in histlist],
            colorlist=None,
            ymaxlinfactor=1.8,
            drawoptions='hist e',
            extrainfos=extrainfos, infosize=None, infoleft=infoleft, infotop=infotop)
