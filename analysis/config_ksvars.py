import numpy as np

config = ({
    'rpv': {'variablename':'_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates'],
            'yaxlog': True,
            'bkgmodes': {
              'bkgdefault': {'type':None, 'info':'Background not subtracted'},
              'bkgsideband': {'type':'sideband', 'info': 'Background subtracted'}
            },
            'bins': {
              'finebins':np.linspace(0,20,num=41,endpoint=True),
              'defaultbins':[0.,0.5,1.5,4.,10.,20.],
            },
            'normalization': {
              'normlumi':{'type':'lumi', 'info':'Normalized to luminosity'},
              'normeventyield':{'type':'eventyield', 'info':'Normalized to data events'},
              'normrangesmall':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm', 
                          'normvariable': '_RPV', 'normrange':[0.,0.5]},
              'normrangemed':{'type':'range', 'info': 'Normalized for #Delta_{2D} in 0.5 - 1.5 cm',
                        'normvariable': '_RPV', 'normrange':[0.5,1.5]}
            },
    },
    'rpvsig': {'variablename':'_RSigPV',
               'xaxtitle':'#Delta_{2D} significance',
               'yaxtitle': 'Reconstructed vertices',
               'treename': 'laurelin',
               'extrainfos': ['K^{0}_{S} candidates'],
               'yaxlog': True,
               'bkgmodes': {
                 'bkgsideband': {'type':'sideband', 'info': 'Background subtracted'}
               },
               'bins': {
                 'finebins':np.linspace(0,600,num=61,endpoint=True),
               },
               'normalization': {
                 'normrangesmall':{'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                             'normvariable': '_RPV', 'normrange':[0.,0.5]},
               },
    }
})
