# note: this is supposed to be the same configuration as the newer version,
#       only with a different (older) naming convention for the variables,
#       for running on older files.


import numpy as np

config = ({
  'rpv_vs_pt': {'variablename': '_KsRPV',
                'xaxtitle': '#Delta_{2D} (cm)',
		'yvariablename': '_KsPt',
                'yaxtitle': 'p_{T} (GeV)',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                  'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_KsInvMass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
	          'defaultbins':{ 'xbins':[0.,0.5,1.5,4.5,20.],
			          'ybins':[0.,5.,10.,20.] },
                  'finexbins':{ 'xbins':[0.,0.5,1.,1.5,2.,5.,10.,15.,20.],
                                'ybins':[0.,5.,10.,20.] },
                },
                'normalization': {
	          'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_KsRPV', 'normrange':[0.,0.5] },
	        }
  },
})
