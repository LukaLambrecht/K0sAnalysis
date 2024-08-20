import numpy as np

config = ({
  'rpv_vs_pt': {'variablename': '_RPV',
                'xaxtitle': '#Delta_{2D} (cm)',
		'yvariablename': '_pt',
                'yaxtitle': 'p_{T} (GeV)',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                  'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
                  'coarsebins':{ 'xbins':[0.,0.5,5.,10.,20.],
                                 'ybins':[0.,5.,10.,20.] },
                },
                'normalization': {
	          'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
	        }
  }
})
