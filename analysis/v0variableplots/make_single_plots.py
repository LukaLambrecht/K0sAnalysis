################################################################
# Make a series of plots of all V0 related variables in a tree #
################################################################

import sys
import os
import json
import argparse
import ROOT
sys.path.append(os.path.abspath('../../tools'))
sys.path.append(os.path.abspath('../../plotting'))
from plotvarfromtree import fillvarfromtree
from singlehistplotter import plotsinglehistogram

if __name__=='__main__':

  parser = argparse.ArgumentParser( description = 'Make V0 plots' )
  parser.add_argument('--inputfile', required=True, type=os.path.abspath)
  parser.add_argument('--treename', required=True)
  parser.add_argument('--variables', required=True, type=os.path.abspath)
  parser.add_argument('--outputdir', default='output_test')
  parser.add_argument('--nprocess', type=int, default=-1)
  parser.add_argument('--extrainfos', default=None)
  parser.add_argument('--normalize', default=False, action='store_true')
  args = parser.parse_args()

  # read the variables
  variables = []
  with open(args.variables,'r') as f:
    variables = json.load(f)

  # read the input tree
  fin = ROOT.TFile.Open(args.inputfile)
  tree = fin.Get(args.treename)

  # parse extra info
  extrainfos = None
  if args.extrainfos is not None:
    extrainfos = args.extrainfos.split(',')

  # make output directory
  if not os.path.exists(args.outputdir):
    os.makedirs(args.outputdir)

  # loop over variables
  for variable in variables:

    # fill a histogram
    hist = fillvarfromtree( tree,
            variable['name'],
            xlow = variable['xlow'],
            xhigh = variable['xhigh'],
            nbins = variable['nbins'],
            nprocess = args.nprocess )

    # normalize
    if args.normalize:
      integral = float(hist.Integral("width"))
      hist.Scale(1/integral)
      variable['yaxtitle'] = 'Arbitrary units'

    # define plot settings
    outputfile = os.path.join(args.outputdir, 'var_{}'.format(variable['name']))
    xaxtitle = variable.get('xaxtitle',None)
    yaxtitle = variable.get('yaxtitle',None)
    title = variable.get('title',None)
    infoleft = 0.7 if 'inforight' in variable.keys() else None

    # plot the histogram
    plotsinglehistogram( hist, outputfile,
        xaxtitle=xaxtitle, yaxtitle=yaxtitle, title=title,
        topmargin=0.1,
        drawoptions='hist e',
        do_cms_text=True,
        extrainfos=extrainfos, infoleft=infoleft )
