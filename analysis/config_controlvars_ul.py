# note: this is supposed to be the same configuration as the pre-UL version,
#       only with a different (newer) naming convention for the variables.

import numpy as np

config = ({
    'mll':   {'variablename':'_nimloth_Mll',
              'xaxtitle': 'Dilepton invariant mass (GeV)',
              'yaxtitle': 'Events',
              'treename': 'nimloth',
              'bkgmodes': {
                'bkgdefault': {'type':None},
              },
              'bins': {
                'binsdefault': np.linspace(85,97,num=50,endpoint=True),
              },
              'normalization': {
                'normlumi':{'type':'lumi'},
              },
    },
    'njets': {'variablename':'_nimloth_nJets',
              'xaxtitle': 'Number of jets',
              'yaxtitle': 'Events',
              'treename': 'nimloth',
              'bkgmodes': {
                'bkgdefault': {'type':None},
              },
              'bins': {
                'binsdefault': np.linspace(-0.5,6.5,num=8,endpoint=True),
              },
              'normalization': {
                'normlumi':{'type':'lumi'},
              },
    },
    'lpt':   {'variablename':'_celeborn_lPt',
              'xaxtitle':'Lepton transverse momentum (GeV)',
              'yaxtitle':'Leptons',
              'treename': 'celeborn',
              'bkgmodes': {
                'bkgdefault': {'type':None},
              },
              'bins': {
                'binsdefault': np.linspace(25,125,num=50,endpoint=True),
              },
              'normalization': {
                'normlumi':{'type':'lumi'},
              },
    },
    'leta':  {'variablename':'_celeborn_lEta',
              'xaxtitle':'Lepton pseudorapidity',
              'yaxtitle':'Leptons',
              'treename': 'celeborn',
              'bkgmodes': {
                'bkgdefault': {'type':None},
              },
              'bins': {
                'binsdefault': np.linspace(-2.4,2.4,num=50,endpoint=True),
              },
              'normalization': {
                'normlumi':{'type':'lumi'},
              },
    },
})
