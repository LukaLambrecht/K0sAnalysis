import numpy as np

config = ({
  'rpv_vs_pt': {'variablename': '_RPV',
                'xaxtitle': '#Delta_{2D} (cm)',
		'yvariablename': '_pt',
                'yaxtitle': 'p_{T} (GeV)',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                    'bkgdefault': {'type':None, 'info':'Background not subtracted'},
                    'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
	               'defaultbins':{ 'xbins':[0., 0.5, 1.5, 4.0, 20.],
			          'ybins':[0.,5., 10., 20.] },
                   'finexbins':{ 'xbins':[0.,0.5,1.,1.5,2.,5.,10., 20.],
                                'ybins':[0.,5.,10., 20., 50.] },
                },
                'normalization': {
	          'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
	        }
  },
  'rpv_vs_phi': {'variablename': '_RPV',
                'xaxtitle': '#Delta_{2D} (cm)',
		'yvariablename': '_phi',
                'yaxtitle': '#phi',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                    'bkgdefault': {'type':None, 'info':'Background not subtracted'},
                    'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
	               'defaultbins':{ 'xbins':[0., 0.5, 1.5, 4.0, 20.],
                                'ybins':[-3.,-1.5, 0., 1.5, 3.] },
                   'finexbins':{ 'xbins':[0.,0.5,1.,1.5,2.,5.,10., 20.],
                                'ybins':[-3.,-2.,-1., 0., 1., 2., 3.] },
                },
                'normalization': {
	          'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
	        }
  },
  'rpv_vs_eta': {'variablename': '_RPV',
                'xaxtitle': '#Delta_{2D} (cm)',
		'yvariablename': '_eta',
                'yaxtitle': '#eta ',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                    'bkgdefault': {'type':None, 'info':'Background not subtracted'},
                    'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
	                'defaultbins':{ 
                        'xbins':[0., 0.5, 1.5, 4.0, 20.],
			                  'ybins':[-2.5,-1.6, 0., 1.6, 2.5] },
                   'finexbins':{ 'xbins':[0.,0.5,1.,1.5,2.,5.,10., 20.],
			                      'ybins':[-2.5,-1.6, 0., 1.6, 2.5] },
                },
                'normalization': {
	          'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
	        }
  },
  'rpvsig_vs_pt': {'variablename': '_RPVSig', 
                'xaxtitle': '#Delta_{2D} significance',
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
	              'defaultbins':{ 'xbins':[1., 20., 50., 100.,500.],
                                'ybins':[0.,5.,10., 20.] },
                  'finexbins':{ 'xbins':[0., 15., 50., 100., 200., 300., 400., 500., 600., 800.,1500.],
                                'ybins':[0.,5.,10., 20., 50., 500.] },
                },
                'normalization': {
                  'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
                }
  },
  'rpvsig_vs_eta': {'variablename': '_RPVSig', 
                'xaxtitle': '#Delta_{2D} significance',
                'yvariablename': '_eta', 
                'yaxtitle': '#eta',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                  'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
	              'defaultbins':{ 'xbins':[1., 20., 50., 100.,500.],
			                  'ybins':[-2.5,-1.6, 0., 1.6, 2.5] },
                  'finexbins':{ 'xbins':[0., 15., 50., 100., 200., 300., 400., 500., 600., 800.,1500.],
			                  'ybins':[-2.5,-1.6, 0., 1.6, 2.5] },
                },
                'normalization': {
                  'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
                }
  },
  'rpvsig_vs_phi': {'variablename': '_RPVSig', 
                'xaxtitle': '#Delta_{2D} significance',
                'yvariablename': '_phi', 
                'yaxtitle': '#phi',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates'],
                'bkgmodes': {
                  'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
	              'defaultbins':{ 'xbins':[1., 20., 50., 100.,500.],
                                'ybins':[-3.,-1.5, 0., 1.5, 3.] },
                  'finexbins':{ 'xbins':[0., 15., 50., 100., 200., 300., 400., 500., 600., 800.,1500.],
                                'ybins':[-3.,-2.,-1., 0., 1., 2., 3.] },
                },
                'normalization': {
                  'normrange':{ 'type':'range', 'info': 'Normalized for #Delta_{2D} < 0.5 cm',
                                'normvariable': '_RPV', 'normrange':[0.,0.5] },
                }
  }
  })

