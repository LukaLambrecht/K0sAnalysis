# note: this is supposed to be the same configuration as the pre-UL version,
#       only with a different (newer) naming convention for the variables.

import numpy as np

config = ({
    'rpv': {'variablename':'_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates'],
            'bkgmodes': {
              'bkgsideband': {'type':'sideband', 'info': 'Background subtracted',
                              'sidevariable': '_mass',
                              'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)},
            },
            'bins': {
              'defaultbins':[0.,0.5,1.5,4.,10.,20.],
            },
            'normalization': {
              'normrange':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm', 
                          'normvariable': '_RPV', 'normrange':[0.,0.5]},
            },
    }
})
