#!/usr/bin/env python3
import numpy as np
import os
import sys

# ensure package imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from fitting.count_peak import count_peak_unbinned


def main():
    np.random.seed(123)

    nbkg = 500
    nsig = 800
    bkg_vals = np.random.uniform(0.4, 0.6, size=nbkg)
    sig_vals = np.random.normal(0.4976, 0.005, size=nsig)
    values = np.concatenate([bkg_vals, sig_vals])
    weights = np.ones_like(values)

    bins = list(np.linspace(0.4, 0.6, 101))
    variable = {'bins': bins}

    print('Running compare strategy...')
    try:
        result = count_peak_unbinned(
            values,
            weights,
            variable,
            mode='hybrid',
            label='synthetic',
            lumi=1000,
            extrainfo='synthetic test',
            histname='testhist',
            plotdir=None,
            fit_strategy='compare',
        )
        print('Compare result:')
        print('  legacy   =', result['legacy'])
        print('  adaptive =', result['adaptive'])
    except Exception as exc:
        print('Compare run failed:', repr(exc))

    print('\nDone')


if __name__ == '__main__':
    main()
