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
  parser.add_argument('--pixel16', default=False, action='store_true')
  parser.add_argument('--pixel1718', default=False, action='store_true')
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
    values1 = tree[variables[0]['name']].array(library='np', entry_stop=args.nprocess)
    # special case if second variable is _RPVUnc:
    # not yet stored but can be calculated on the fly
    if variables[1]['name'] == '_RPVUnc':
      values2 = (tree['_RPV'].array(library='np', entry_stop=args.nprocess) / 
                 tree['_RPVSig'].array(library='np', entry_stop=args.nprocess))
    else: values2 = tree[variables[1]['name']].array(library='np', entry_stop=args.nprocess)
    mass = tree['_mass'].array(library='np', entry_stop=args.nprocess)

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
    extrainfos = args.extrainfos.replace('-',' ').split(',')
    for i, el in enumerate(extrainfos):
      el = el.replace('PreVFP', ' (old APV)')
      el = el.replace('PostVFP', ' (new APV)')
      el = el.replace('run2preul', 'Pre-legacy')
      el = el.replace('run2ul', 'Legacy')
      extrainfos[i] = el

  # define plot settings
  xaxtitle = variables[0].get('xaxtitle',None)
  yaxtitle = variables[1].get('xaxtitle',None)
  caxtitle = 'Number of $K^{0}_{S}$ candidates'

  # make figure
  fig,ax = plot(values1, values2, bins=(xbins, ybins),
             xaxtitle=xaxtitle, yaxtitle=yaxtitle, caxtitle=caxtitle)

  # add extra info
  if extrainfos is not None:
    txt = ax.text(0.95, 0.95, '\n'.join(extrainfos), fontsize=12, ha='right', va='top',
                   transform=ax.transAxes)
    txt.set_bbox(dict(facecolor='white', alpha=0.9, edgecolor='black'))

  # add cms text
  txt = ax.text(0.05, 0.95, r'\textbf{CMS} \textit{Preliminary}', fontsize=12, ha='left', va='top',
                   transform=ax.transAxes)
  txt.set_bbox(dict(facecolor='white', alpha=0.9, edgecolor='black')) 

  # add pixel layer indications if requested
  linestyle = '--'
  linewidth = 2 
  linecolor = 'r'
  ypos = ax.get_ylim()[1]*1.02
  fontsize=12
  if args.pixel16:
    for x in [4.4, 7.3, 10.2]:
      ax.axvline(x, ymin=0, ymax=1,
        linestyle=linestyle, linewidth=linewidth, color=linecolor)
    ax.text(4.4, ypos, "BPIX1", fontsize=fontsize, color=linecolor)
    ax.text(7.3, ypos, "BPIX2", fontsize=fontsize, color=linecolor)
    ax.text(10.2, ypos, "BPIX3", fontsize=fontsize, color=linecolor)
  if args.pixel1718:
    for x in [2.9, 6.8, 10.9, 16.]:
      ax.axvline(x, ymin=0, ymax=1,
        linestyle=linestyle, linewidth=linewidth, color=linecolor)
    ax.text(2.9, ypos, "BPIX1", fontsize=fontsize, color=linecolor)
    ax.text(6.8, ypos, "BPIX2", fontsize=fontsize, color=linecolor)
    ax.text(10.9, ypos, "BPIX3", fontsize=fontsize, color=linecolor)
    ax.text(16, ypos, "BPIX4", fontsize=fontsize, color=linecolor)

  # save figure
  fig.savefig(args.outputfile)
