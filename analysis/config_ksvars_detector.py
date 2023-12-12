import numpy as np

config = ({
    'rpv_lin': {'variablename':'_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates'],
            'bkgmodes': {
              'bkgsideband': {'type':'sideband', 'info': 'Background subtracted'}
            },
            'bins': {
              'finebins':np.linspace(0,20,num=41,endpoint=True),
            },
            'normalization': {
              'normrangesmall':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm', 
                          'normvariable': '_RPV', 'normrange':[0.,0.5]},
            },
    },
    'rpv_log': {'variablename':'_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates'],
            'bkgmodes': {
              'bkgsideband': {'type':'sideband', 'info': 'Background subtracted'}
            },
            'bins': {
              'finebins':np.linspace(0,20,num=41,endpoint=True),
            },
            'normalization': {
              'normrangesmall':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                          'normvariable': '_RPV', 'normrange':[0.,0.5]},
            },
    },
})
