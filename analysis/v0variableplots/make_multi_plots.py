################################################################
# Make a series of plots of all V0 related variables in a tree #
################################################################
# Extension: plot and compare the distributions of several input files

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
  parser.add_argument('-i', '--inputfiles', required=True, type=os.path.abspath, nargs='+')
  parser.add_argument('-t', '--treename', required=True)
  parser.add_argument('-v', '--variables', required=True, type=os.path.abspath)
  parser.add_argument('-l', '--inputlabels', nargs='+', default=[])
  parser.add_argument('-o', '--outputdir', default='output_test')
  parser.add_argument('-n', '--nprocess', type=int, default=-1)
  parser.add_argument('--extrainfos', default=None)
  parser.add_argument('--colors', default=None)
  parser.add_argument('--normalize', default=False, action='store_true')
  args = parser.parse_args()

  # read the variables
  variables = []
  with open(args.variables,'r') as f:
    variables = json.load(f)

  # parse labels
  dolegend = True
  if len(args.inputlabels)==0:
    dolegend = False
    inputlabels = ['']*len(args.inputfiles)
  elif len(args.inputlabels)!=len(args.inputfiles):
    print('WARNING: number of labels does not correspond to number of hists.')
    print('Will ignore labels and not make a legend.')
    dolegend = False
    inputlabels = ['']*len(args.inputfiles)
  else:
    inputlabels = [el.replace('-',' ') for el in args.inputlabels]

  # parse extra info
  extrainfos = None
  if args.extrainfos is not None:
    extrainfos = args.extrainfos.replace('-',' ').split(',')

  # parse colors
  colorlist = None
  if args.colors is not None:
    if args.colors == '2016split':
      colorlist = [ROOT.kAzure-2, ROOT.kAzure-9, ROOT.kAzure+6, ROOT.kViolet]

  # make output directory
  if not os.path.exists(args.outputdir):
    os.makedirs(args.outputdir)

  # loop over variables
  for variable in variables:
    histlist = []

    # loop over input files
    for inputfile in args.inputfiles:

      # read the input tree
      fin = ROOT.TFile.Open(inputfile)
      tree = fin.Get(args.treename)

      # fill a histogram
      hist = fillvarfromtree( tree,
            variable['name'],
            xlow = variable['xlow'],
            xhigh = variable['xhigh'],
            nbins = variable['nbins'],
            nprocess = args.nprocess )
      histlist.append(hist)

    # define plot settings
    outputfile = os.path.join(args.outputdir, 'var_{}'.format(variable['name']))
    xaxtitle = variable.get('xaxtitle',None)
    yaxtitle = variable.get('yaxtitle',None)
    if args.normalize: yaxtitle = 'Arbitrary units'
    title = variable.get('title',None)
    infoleft = 0.7 if 'inforight' in variable.keys() else None
    infotop = 0.75

    # plot the histogram
    plotmultihistograms( histlist,
            figname=outputfile, title=title, xaxtitle=xaxtitle, yaxtitle=yaxtitle,
            normalize=args.normalize,
            dolegend=dolegend, labellist=inputlabels,
            colorlist=colorlist,
            ymaxlinfactor=1.8,
            drawoptions='hist e',
            extrainfos=extrainfos, infosize=None, infoleft=infoleft, infotop=infotop)

    # same in log scale
    logoutputfile = os.path.splitext(outputfile)[0]+'_log'
    plotmultihistograms( histlist,
            figname=logoutputfile, title=title, xaxtitle=xaxtitle, yaxtitle=yaxtitle,
            normalize=args.normalize,
            logy=True, yminlogfactor=0.2, ymaxlogfactor=100,
            dolegend=dolegend, labellist=inputlabels,
            colorlist=colorlist,
            drawoptions='hist e',
            extrainfos=extrainfos, infosize=None, infoleft=infoleft, infotop=infotop)
