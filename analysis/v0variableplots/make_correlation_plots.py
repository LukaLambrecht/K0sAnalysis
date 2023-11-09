################################################################
# Make a series of plots of all V0 related variables in a tree #
################################################################

import sys
import os
import json
import argparse
import numpy as np
import uproot
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True


def plot(x, y, bins=None, xaxtitle=None, yaxtitle=None, caxtitle=None):
    fig,ax = plt.subplots()
    norm = mpl.colors.LogNorm()
    ax.hist2d(x, y, bins=bins, norm=norm, cmap='viridis')
    if xaxtitle is not None: ax.set_xlabel(xaxtitle, fontsize=12)
    if yaxtitle is not None: ax.set_ylabel(yaxtitle, fontsize=12)
    # add a color bar
    cobject = mpl.cm.ScalarMappable(norm=norm)
    cbar = fig.colorbar(cobject, ax=ax)
    if caxtitle is not None:
      cbar.ax.get_yaxis().labelpad = 20
      cbar.ax.set_ylabel(caxtitle, fontsize=12, rotation=270)
    return fig,ax


if __name__=='__main__':

  parser = argparse.ArgumentParser( description = 'Make V0 plots' )
  parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
  parser.add_argument('-t', '--treename', required=True)
  parser.add_argument('-v', '--variables', required=True, type=os.path.abspath)
  parser.add_argument('-o', '--outputfile', default='output_test.png')
  parser.add_argument('-n', '--nprocess', type=int, default=-1)
  parser.add_argument('--extrainfos', default=None)
  parser.add_argument('--normalize', default=False, action='store_true')
  args = parser.parse_args()

  # read the variables
  variables = []
  with open(args.variables,'r') as f:
    variables = json.load(f)
  if len(variables)!=2:
    msg = 'ERROR: expected 2 variables but found {}'.format(len(variables))
    raise Exception(msg)

  # read the input tree
  with uproot.open(args.inputfile) as f:
    tree = f[args.treename]
    values1 = tree[variables[0]['name']].array(library='np')
    values2 = tree[variables[1]['name']].array(library='np')
    mass = tree['_mass'].array(library='np')

  # remove nan
  mask = (np.isnan(values1) | np.isnan(values2))
  values1 = values1[~mask]
  values2 = values2[~mask]
  mass = mass[~mask]

  # do extra cuts
  mask = (abs(mass - 0.498)<0.01)
  values1 = values1[mask]
  values2 = values2[mask]

  # make binning
  xbins = np.linspace(variables[0]['xlow'], variables[0]['xhigh'], num=variables[0]['nbins'])
  ybins = np.linspace(variables[1]['xlow'], variables[1]['xhigh'], num=variables[1]['nbins'])

  # parse extra info
  extrainfos = None
  if args.extrainfos is not None:
    extrainfos = args.extrainfos.split(',')

  # define plot settings
  xaxtitle = variables[0].get('xaxtitle',None)
  yaxtitle = variables[1].get('xaxtitle',None)
  caxtitle = 'Number of $K^{0}_{S}$ candidates'

  # make figure
  fig,ax = plot(values1, values2, bins=(xbins, ybins),
             xaxtitle=xaxtitle, yaxtitle=yaxtitle, caxtitle=caxtitle)
  fig.savefig(args.outputfile)
