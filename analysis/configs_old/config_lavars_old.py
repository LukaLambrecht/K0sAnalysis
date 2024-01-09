# note: this is supposed to be the same configuration as the newer version,
#       only with a different (older) naming convention for the variables,
#       for running on older files.


import numpy as np

config = ({
    'rpv': {'variablename':'_LaRPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'telperion',
            'extrainfos': ['#Lambda^{0} candidates'],
            'bkgmodes': {
              'bkgdefault': {'type':None, 'info':'Background not subtracted'},
              'bkgsideband': {'type':'sideband', 'info': 'Background subtracted',
                              'sidevariable': '_LaInvMass',
                              'sidebins': np.linspace(1.08, 1.15, num=31, endpoint=True)},
            },
            'bins': {
              'finebins':np.linspace(0,20,num=41,endpoint=True),
            },
            'normalization': {
              'normlumi':{'type':'lumi', 'info':'Normalized to luminosity'},
              'normeventyield':{'type':'eventyield', 'info':'Normalized to data events'},
              'normrange':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 1.5 cm', 
                          'normvariable': '_LaRPV', 'normrange':[0.,1.5]},
            },
    }
})
