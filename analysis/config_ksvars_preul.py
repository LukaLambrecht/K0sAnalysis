# note: this is supposed to be the same configuration as the UL version,
#       only with a different (older) naming convention for the variables.
# note: also it does not include the RPV significance variable,
#       as it is not present in the old pre-UL files.

import numpy as np

config = ({
    'rpv': {'variablename':'_KsRPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates'],
            'bkgmodes': {
              'bkgdefault': {'type':None, 'info':'Background not subtracted'},
              'bkgsideband': {'type':'sideband', 'info': 'Background subtracted',
                              'sidevariable': '_KsInvMass',
                              'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)},
            },
            'bins': {
              'finebins':np.linspace(0,20,num=41,endpoint=True),
              'defaultbins':[0.,0.5,1.5,4.,10.,20.],
            },
            'normalization': {
              'normlumi':{'type':'lumi', 'info':'Normalized to luminosity'},
              'normeventyield':{'type':'eventyield', 'info':'Normalized to data events'},
              'normrange':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm', 
                          'normvariable': '_KsRPV', 'normrange':[0.,0.5]},
            },
    }
})
