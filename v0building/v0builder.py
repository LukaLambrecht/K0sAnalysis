###########################################################
# python script to make dedicated V0 trees out of ntuples #
###########################################################
# note: will only work on files that have been processed with the custom ntuplizer
#       (e.g. using the V0Analyzer module)
#       and that have been processed with the skimmer in the ../skimming directory!
# note: use with CMSSW_12_X and python3, for the uproot module to be available!


# import external modules
import sys
import os
import argparse
import numpy as np
import uproot
import awkward as ak
import vector
# import framework modules
from v0selections import cospointing
from v0selections import selection


if __name__=='__main__':

  # write starting tag (for automatic crash checking)
  sys.stderr.write('###starting###\n')

  # read command line arguments
  parser = argparse.ArgumentParser( description = 'Perform V0 candidate selection' )
  parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
  parser.add_argument('-o', '--outputfile', required=True, type=os.path.abspath)
  parser.add_argument('-s', '--selection', default='legacy')
  parser.add_argument('-n', '--nevents', default=-1, type=int)
  parser.add_argument('--transfer', default=False, action='store_true')
  args = parser.parse_args()

  # check selection_name
  allowed_selections = [
    'legacy',
  ]
  if args.selection not in allowed_selections:
    raise Exception('ERROR: selection '+args.selection+' not recognized.')

  # handle case of transfering input file (instead of reading it directly)
  if args.transfer:
    # set temporary directory where to transfer to
    tmpdir = '/tmp'
    if 'TMPDIR' in os.environ: tmpdir = os.environ['TMPDIR']
    # set new input file name
    tmpfile = args.inputfile.strip('/').replace('/','_')
    tmpfile = os.path.join(tmpdir, tmpfile)
    # do the transfer
    cmd = 'cp {} {}'.format(args.inputfile, tmpfile)
    print('Transfering input file to {}...'.format(tmpdir))
    print(cmd)
    os.system(cmd)
    print('Done transfering input file.')
    args.inputfile = tmpfile
    # set new output file name
    origoutputfile = args.outputfile
    args.outputfile = tmpfile.replace('.root','_out.root')

  # open input file
  with uproot.open(args.inputfile) as f:
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
    if( args.nevents>0 and args.nevents<tree.num_entries ): entry_stop = args.nevents
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
  print('Constructing auxiliary variables')
  
  # pointing angle wrt primary vertex
  cospointingPV = cospointing(branches, reference='primaryVertex')
  
  # pointing angle wrt beam spot
  cospointingBS = cospointing(branches, reference='beamSpot')
  
  # sum of track pt
  ptSum = branches['_V0PtPos'] + branches['_V0PtNeg']

  # deltaR between tracks
  posp4 = vector.zip({
    'pt': branches['_V0PtPos'],
    'eta': branches['_V0EtaPos'],
    'phi': branches['_V0PhiPos'],
    'mass': 0.
  })
  negp4 = vector.zip({
    'pt': branches['_V0PtNeg'],
    'eta': branches['_V0EtaNeg'],
    'phi': branches['_V0PhiNeg'],
    'mass': 0.
  })
  trackdR = posp4.deltaR(negp4)

  # make masks for quality selections
  print('Performing selections')
  extra = {
    'cospointingPV': cospointingPV,
    'cospointingBS': cospointingBS
  }
  selmask = selection(branches, args.selection, extra=extra)

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
  laurelin['_RPVSig'] = ak.flatten(branches['_V0RPVSig'][laurelinmask])
  laurelin['_RBSSig'] = ak.flatten(branches['_V0RBSSig'][laurelinmask])
  laurelin['_pt'] = ak.flatten(branches['_V0Pt'][laurelinmask])
  laurelin['_ptSum'] = ak.flatten(ptSum[laurelinmask])
  laurelin['_eta'] = ak.flatten(branches['_V0Eta'][laurelinmask])
  laurelin['_phi'] = ak.flatten(branches['_V0Phi'][laurelinmask])
  laurelin['_nHitsPos'] = ak.flatten(branches['_V0NHitsPos'][laurelinmask])
  laurelin['_nHitsNeg'] = ak.flatten(branches['_V0NHitsNeg'][laurelinmask])
  laurelin['_ptPos'] = ak.flatten(branches['_V0PtPos'][laurelinmask])
  laurelin['_ptNeg'] = ak.flatten(branches['_V0PtNeg'][laurelinmask])
  laurelin['_normChi2Pos'] = ak.flatten(branches['_V0NormChi2Pos'][laurelinmask])
  laurelin['_normChi2Neg'] = ak.flatten(branches['_V0NormChi2Neg'][laurelinmask])
  laurelin['_trackdR'] = ak.flatten(trackdR[laurelinmask])
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
  telperion['_RPVSig'] = ak.flatten(branches['_V0RPVSig'][telperionmask])
  telperion['_RBSSig'] = ak.flatten(branches['_V0RBSSig'][telperionmask])
  telperion['_pt'] = ak.flatten(branches['_V0Pt'][telperionmask])
  telperion['_ptSum'] = ak.flatten(ptSum[telperionmask])
  telperion['_eta'] = ak.flatten(branches['_V0Eta'][telperionmask])
  telperion['_phi'] = ak.flatten(branches['_V0Phi'][telperionmask])
  telperion['_nHitsPos'] = ak.flatten(branches['_V0NHitsPos'][telperionmask])
  telperion['_nHitsNeg'] = ak.flatten(branches['_V0NHitsNeg'][telperionmask])
  telperion['_ptPos'] = ak.flatten(branches['_V0PtPos'][telperionmask])
  telperion['_ptNeg'] = ak.flatten(branches['_V0PtNeg'][telperionmask])
  telperion['_normChi2Pos'] = ak.flatten(branches['_V0NormChi2Pos'][telperionmask])
  telperion['_normChi2Neg'] = ak.flatten(branches['_V0NormChi2Neg'][telperionmask])
  telperion['_trackdR'] = ak.flatten(trackdR[telperionmask])
  if not isdata:
    telperion['_weight'] = ak.flatten( (branches['_V0Pt'][telperionmask]>-1.)*branches['_weight'] )
    telperion['_nTrueInt'] = ak.flatten( (branches['_V0Pt'][telperionmask]>-1.)*branches['_nTrueInt'] )

  # write output trees to file
  print('Writing trees to output file')
  with uproot.recreate(args.outputfile) as f:
    f['nimloth'] = nimloth
    f['celeborn'] = celeborn
    f['laurelin'] = laurelin
    f['telperion'] = telperion
    if not isdata:
        f['hCounter'] = hcounter
        f['nTrueInteractions'] = ntrueint

  # handle case of transfering output file
  if args.transfer:
    # move output to destination
    cmd = 'mv {} {}'.format(args.outputfile, origoutputfile)
    print('Transfering output file...')
    print(cmd)
    os.system(cmd)
    print('Done transfering output file.')
    # remove temporary file
    cmd = 'rm {}'.format(tmpfile)
    print('Removing temporary file {}'.format(tmpfile))
    os.system(cmd)

  # write closing tag (for automatic crash checkiing)
  sys.stderr.write('###done###\n')
