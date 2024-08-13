import os
import sys
import numpy as np
import scipy
from scipy.stats import rv_continuous

sys.path.append(os.path.abspath('../'))
from count_peak import count_peak_unbinned


class Pdf(rv_continuous):
    def _pdf(self, x):
        intercept = 0.1
        slope = 0.2
        m = 0.5
        s = 0.05
        linear = intercept + slope*x
        gaussian = np.exp(-0.5*np.power(np.divide((x-m), s), 2))
        # calculate normalization (assuming a range from 0 to 1!)
        norm_linear = intercept + slope/2.
        norm_gaussian = np.sqrt(2*np.pi)*s
        norm = norm_linear + norm_gaussian
        return (linear + gaussian)/norm

if __name__=='__main__':

    # generate data values
    # corresponding to a linear background
    # and gaussian peak
    xmin = 0
    xmax = 1
    pdf = Pdf(name='pdf', a=xmin, b=xmax)
    nvalues = 5000
    values = pdf.rvs(size=nvalues)
    weights = np.ones(nvalues)

    # make dummy variable dict
    variable = {
      "name": "Some variable",
      "variable": "dummy",
      "bins": np.linspace(xmin, xmax, endpoint=True, num=30)
    }

    # call count peak function
    plotdir = 'output_test'
    res = count_peak_unbinned(values, weights, variable, mode='subtract',
                              label=None, lumi=None, extrainfo='dummy data',
                              histname='sideband', plotdir=plotdir)
    print(res)
