###########################################################
# python script to make dedicated V0 trees out of ntuples #
###########################################################
# note: will only work on files that have been processed with the custom ntuplizer
#       (e.g. using the V0Analyzer module)
#       and that have been processed with the skimmer in the ../skimming directory!
# note: preliminary translation from PyROOT into uproot;
#       status: works and synchronized with pyroot approach, but trackdR not yet implemented.
# note: use with CMSSW_12_X and python3

import sys
import os
import numpy as np
import uproot
import awkward as ak

# write starting tag (for automatic crash checking)
sys.stderr.write('###starting###\n')

if len(sys.argv)!=5:
    print('ERROR: wrong number of command line arguments.')
    print('       expected arguments:')
    print('         - input_file')
    print('         - output_file')
    print('         - nevents')
    print('         - selection')
    sys.exit()

input_file_path = os.path.abspath(sys.argv[1])
output_file_path = sys.argv[2]
nevents = int(sys.argv[3])
selection_name = sys.argv[4]

# check selection_name
allowed_selections = [
  'legacy',
  'legacy_loosenhits',
  'legacy_nonhits',
  'legacy_highpt',
  'ivf'
]
if selection_name not in allowed_selections:
    raise Exception('ERROR: selection '+selection_name+' not recognized.')
print('WARNING: selection is hard-coded for now and command line argument is ignored!')

# open input file
with uproot.open(input_file_path) as f:
    fkeys = [key.split(';')[0] for key in f.keys()]
    tree = f["blackJackAndHookers"]["blackJackAndHookersTree"]

    # read counter histograms
    isdata = False
    hcounterkey = "blackJackAndHookers/hCounter"
    ntrueintkey = "blackJackAndHookers/nTrueInteractions"
    if( hcounterkey not in fkeys or ntrueintkey not in fkeys ):
        print('No valid hCounter or nTrueInt found in this file, assuming this is data...')
        isdata = True
    else:
        hcounter = f[hcounterkey]
        ntrueint = f[ntrueintkey]
    
    # define branches to read from input file
    branchnames = ['_nimloth_Mll', '_nimloth_nJets',
                   '_beamSpotX', '_beamSpotY', '_beamSpotZ',
                   '_primaryVertexX', '_primaryVertexY', '_primaryVertexZ',
                   '_celeborn_lPt', '_celeborn_lEta', '_celeborn_lPhi', '_celeborn_lCharge']
    if not isdata: branchnames += ['_weight', '_nTrueInt']
    for b in tree.keys():
        if b.startswith('_V0'): branchnames.append(b)

    # read the data
    entry_stop = None
    if( nevents>0 and nevents<tree.num_entries ): entry_stop = nevents
    msg = 'Tree is found to have {} entries'.format(tree.num_entries)
    msg += ' of which {} will be read'.format(entry_stop if entry_stop is not None 
           else tree.num_entries)
    print(msg)
    print('Reading branches')
    sys.stdout.flush()
    sys.stderr.flush()
    branches = tree.arrays(branchnames, entry_stop=entry_stop)

# make masks for V0 types
ksmask = (branches['_V0Type']==1)
lmask = (branches['_V0Type']==2)
lbarmask = (branches['_V0Type']==3)
lmask = (lmask | lbarmask)

# define extra variables
print('Constructing auxiliary variables for selections')
# pointing angle wrt primary vertex
x = branches['_V0X'] - branches['_primaryVertexX']
y = branches['_V0Y'] - branches['_primaryVertexY']
px = branches['_V0Px']
py = branches['_V0Py']
cospointingPV = (x*px + y*py) / ( (x**2+y**2)**(1./2) * (px**2+py**2)**(1./2) )
# pointing angle wrt beam spot
x = branches['_V0X'] - branches['_beamSpotX']
y = branches['_V0Y'] - branches['_beamSpotY']
cospointingBS = (x*px + y*py) / ( (x**2+y**2)**(1./2) * (px**2+py**2)**(1./2) )
# sum of track pt
ptSum = branches['_V0PtPos'] + branches['_V0PtNeg']

# make masks for quality selections
print('Performing selections')
selmask = (
  (branches['_V0NHitsPos'] >= 6)
  & (branches['_V0NHitsNeg'] >= 6)
  & (branches['_V0PtPos'] > 1.)
  & (branches['_V0PtNeg'] > 1.)
  & (branches['_V0DCA'] < 0.2)
  & (branches['_V0VtxNormChi2'] < 7)
  & (cospointingPV > 0.99)
  & (cospointingBS > 0.99)
)

# fill nimloth
print('Filling per-event tree')
nimloth = {}
nimlothvars = [
  '_nimloth_Mll', '_nimloth_nJets',
  '_beamSpotX', '_beamSpotY', '_beamSpotZ',
  '_primaryVertexX', '_primaryVertexY', '_primaryVertexZ'
]
if not isdata: nimlothvars += ['_weight', '_nTrueInt']
for var in nimlothvars: nimloth[var] = branches[var]

# fill celeborn
print('Filling per-lepton tree')
celeborn = {}
celebornvars = [
  '_celeborn_lPt', '_celeborn_lEta', '_celeborn_lPhi', '_celeborn_lCharge'
]
for var in celebornvars: celeborn[var] = ak.flatten(branches[var])
if not isdata:
    celeborn['_weight'] = np.repeat(branches['_weight'], 2)
    celeborn['_nTrueInt'] = np.repeat(branches['_nTrueInt'], 2)

# fill laurelin
print('Filling K0s tree')
laurelin = {}
laurelinmask = (ksmask & selmask)
laurelin['_mass'] = ak.flatten(branches['_V0InvMass'][laurelinmask])
laurelin['_vertexX'] = ak.flatten(branches['_V0X'][laurelinmask])
laurelin['_vertexY'] = ak.flatten(branches['_V0Y'][laurelinmask])
laurelin['_vertexZ'] = ak.flatten(branches['_V0Z'][laurelinmask])
laurelin['_RPV'] = ak.flatten(branches['_V0RPV'][laurelinmask])
laurelin['_RBS'] = ak.flatten(branches['_V0RBS'][laurelinmask])
laurelin['_RSigPV'] = ak.flatten(branches['_V0RSigPV'][laurelinmask])
laurelin['_RSigBS'] = ak.flatten(branches['_V0RSigBS'][laurelinmask])
laurelin['_pt'] = ak.flatten(branches['_V0Pt'][laurelinmask])
laurelin['_ptSum'] = ak.flatten(ptSum[laurelinmask])
laurelin['_eta'] = ak.flatten(branches['_V0Eta'][laurelinmask])
laurelin['_phi'] = ak.flatten(branches['_V0Phi'][laurelinmask])
laurelin['_nHitsPos'] = ak.flatten(branches['_V0NHitsPos'][laurelinmask])
laurelin['_nHitsNeg'] = ak.flatten(branches['_V0NHitsNeg'][laurelinmask])
laurelin['_ptPos'] = ak.flatten(branches['_V0PtPos'][laurelinmask])
laurelin['_ptNeg'] = ak.flatten(branches['_V0PtNeg'][laurelinmask])
#fillvalue[0] = k0s.trackdR(); laurelin.GetBranch('_trackdR').Fill()
if not isdata:
    laurelin['_weight'] = ak.flatten( (branches['_V0Pt'][laurelinmask]>-1.)*branches['_weight'] )
    laurelin['_nTrueInt'] = ak.flatten( (branches['_V0Pt'][laurelinmask]>-1.)*branches['_nTrueInt'] )

# fill telperion
print('Filling Lambda tree')
telperion = {}
telperionmask = (lmask & selmask)
telperion['_mass'] = ak.flatten(branches['_V0InvMass'][telperionmask])
telperion['_vertexX'] = ak.flatten(branches['_V0X'][telperionmask])
telperion['_vertexY'] = ak.flatten(branches['_V0Y'][telperionmask])
telperion['_vertexZ'] = ak.flatten(branches['_V0Z'][telperionmask])
telperion['_RPV'] = ak.flatten(branches['_V0RPV'][telperionmask])
telperion['_RBS'] = ak.flatten(branches['_V0RBS'][telperionmask])
telperion['_RSigPV'] = ak.flatten(branches['_V0RSigPV'][telperionmask])
telperion['_RSigBS'] = ak.flatten(branches['_V0RSigBS'][telperionmask])
telperion['_pt'] = ak.flatten(branches['_V0Pt'][telperionmask])
telperion['_ptSum'] = ak.flatten(ptSum[telperionmask])
telperion['_eta'] = ak.flatten(branches['_V0Eta'][telperionmask])
telperion['_phi'] = ak.flatten(branches['_V0Phi'][telperionmask])
telperion['_nHitsPos'] = ak.flatten(branches['_V0NHitsPos'][telperionmask])
telperion['_nHitsNeg'] = ak.flatten(branches['_V0NHitsNeg'][telperionmask])
telperion['_ptPos'] = ak.flatten(branches['_V0PtPos'][telperionmask])
telperion['_ptNeg'] = ak.flatten(branches['_V0PtNeg'][telperionmask])
#fillvalue[0] = k0s.trackdR(); telperion.GetBranch('_trackdR').Fill()
if not isdata:
    telperion['_weight'] = ak.flatten( (branches['_V0Pt'][telperionmask]>-1.)*branches['_weight'] )
    telperion['_nTrueInt'] = ak.flatten( (branches['_V0Pt'][telperionmask]>-1.)*branches['_nTrueInt'] )

# write output trees to file
print('Writing trees to output file')
with uproot.recreate(output_file_path) as f:
    f['nimloth'] = nimloth
    f['celeborn'] = celeborn
    f['laurelin'] = laurelin
    f['telperion'] = telperion
    if not isdata:
        f['hCounter'] = hcounter
        f['nTrueInteractions'] = ntrueint

# write closing tag (for automatic crash checkiing)
sys.stderr.write('###done###\n')
