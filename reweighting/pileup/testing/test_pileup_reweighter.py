import os
import sys
import ROOT
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath('../'))
from pileupreweighter import PileupReweighter


if __name__=='__main__':

    # generate values for number of true interactions
    # from a gaussian distribution
    rng = np.random.default_rng()
    mean = 40
    std = 10
    n = 100000
    ntrueint = rng.normal(mean, std, size=n)

    # make the pileup reweighter
    p = PileupReweighter('run2preul', '2018')

    # initialize the pileup reweighter (only needed for pre-UL)
    inthist = ROOT.TH1F("h1", "h1", 100, 0, 100)
    for val in ntrueint: inthist.Fill(val)
    p.initntrueint(inthist)

    # do reweighting
    weights = p.weight(ntrueint)
    upweights = p.upweight(ntrueint)
    downweights = p.downweight(ntrueint)

    # make a figure
    fig, ax = plt.subplots()
    bins = np.linspace(0, 100, endpoint=True, num=101)
    density = True
    histtype = 'step'
    linewidth = 2
    ax.hist(ntrueint, bins=bins, label='Unweighted',
      density=density, histtype=histtype, linewidth=linewidth)
    ax.hist(ntrueint, bins=bins, weights=weights, label='Reweighted',
      density=density, histtype=histtype, linewidth=linewidth)
    ax.hist(ntrueint, bins=bins, weights=upweights, label='Up',
      density=density, histtype=histtype, linewidth=linewidth)
    ax.hist(ntrueint, bins=bins, weights=downweights, label='Down',
      density=density, histtype=histtype, linewidth=linewidth)
    ax.legend()
    fig.savefig('output_test.png')
