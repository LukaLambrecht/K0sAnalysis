###########################################################
# python script to make dedicated V0 trees out of ntuples #
###########################################################
# note: will only work on files that have been processed with the V0Analyzer module in the ntuplizer
#       and that have been processed with the skimmer in the ../skimming directory! 

import sys
import os
import ROOT
import math
import numpy as np
from array import array
from v0object import *

# write starting tag (for automatic crash checking)
sys.stderr.write('### starting ###\n')

if len(sys.argv)!=5:
    print('### ERROR ###: wrong number of command line arguments.')
    print('               usage: python v0builder.py <input_file> <output_file> <nevents>')
    print('                      <selection>')
    sys.exit()

input_file_path = os.path.abspath(sys.argv[1])
output_file_path = sys.argv[2]
nevents = int(sys.argv[3])
selection_name = sys.argv[4]

# check selection_name
if selection_name not in (['legacy','legacy_loosenhits','legacy_nonhits',
			    'ivf']):
    print('### ERROR ###: selection '+selection_name+' not recognized.')
    sys.exit()

# open input file and read tree
inf = ROOT.TFile.Open(input_file_path)
intree = inf.Get("blackJackAndHookers/blackJackAndHookersTree")
try:
    maxevents = intree.GetEntries()
    if nevents <= 0: nevents = maxevents 
    else: nevents = min(nevents,maxevents)
except:
    print('### ERROR ###: GetEntries method failed on input file.')
    print('               probably file was not closed properly.')
    exit()

# try to read hCounter and set isdata to True if attempt fails
isdata = False
hcounter = inf.Get("blackJackAndHookers/hCounter")
ntrueint = inf.Get("blackJackAndHookers/nTrueInteractions")
try:
    test = hcounter.GetBinContent(1)
    test = ntrueint.GetBinContent(1)
except:
    print('note: no valid hCounter or nTrueInt found in this file, assuming this is data...')
    isdata = True
    
# open output file and make trees
outf = ROOT.TFile(output_file_path,"recreate")
laurelin = ROOT.TTree("laurelin","") # data structure for Kshort variables
telperion = ROOT.TTree("telperion","") # data structure for Lambda variables
celeborn = ROOT.TTree("celeborn","") # data structure for muon variables
nimloth = ROOT.TTree("nimloth","") # data structure for event variables
fillvalue = array('f',[0.])

# define branches
# event variable branches (simply copy from skimmed ntuples)
nimloth_variables = ['_nimloth_Mll','_nimloth_nJets',
			'_beamSpotX','_beamSpotY','_beamSpotZ',
			'_primaryVertexX','_primaryVertexY','_primaryVertexZ']
for varname in nimloth_variables: nimloth.Branch(varname,fillvalue,str(varname+'/F'))
# muon variable branches (flatten and copy from skimmed ntuples)
# note: up to now both leptons are taken together, but easily extendable
celeborn_variables = ['_celeborn_lPt','_celeborn_lEta','_celeborn_lPhi','_celeborn_lCharge']
for varname in celeborn_variables: celeborn.Branch(varname,fillvalue,str(varname+'/F'))
# K0s variable branches
laurelin_variables = (['_mass','_vertexX','_vertexY','_vertexZ','_RPV','_RBS',
			'_pt','_ptSum','_eta','_phi',
			'_nHitsPos','_nHitsNeg','_ptPos','_ptNeg','_trackdR'])
for varname in laurelin_variables: laurelin.Branch(varname,fillvalue,str(varname+'/F'))
# Lambda0 variable branches
# note: up to now Lambda0 and Lambda0Bar are taken together
telperion_variables = (['_mass','_vertexX','_vertexY','_vertexZ','_RPV','_RBS',
			'_pt','_ptSum','_eta','_phi',
			'_nHitsPos','_nHitsNeg','_ptPos','_ptNeg','_trackdR'])
for varname in telperion_variables: telperion.Branch(varname,fillvalue,str(varname+'/F'))
# add extra branch for event weight and number of interactions to all trees
if not isdata:
    nimloth.Branch('_weight',fillvalue,str('_weight/F'))
    celeborn.Branch('_weight',fillvalue,str('_weight/F'))
    laurelin.Branch('_weight',fillvalue,str('_weight/F'))
    telperion.Branch('_weight',fillvalue,str('_weight/F'))
    nimloth.Branch('_nTrueInt',fillvalue,str('_nTrueInt/F'))
    celeborn.Branch('_nTrueInt',fillvalue,str('_nTrueInt/F'))
    laurelin.Branch('_nTrueInt',fillvalue,str('_nTrueInt/F'))
    telperion.Branch('_nTrueInt',fillvalue,str('_nTrueInt/F'))

# loop over input tree
print('starting event loop for '+str(nevents)+' events...')
for i in range(nevents):
    intree.GetEntry(i)
    if(i>0 and i%10000==0): 
	print('processed {} of {} events'.format(i,nevents))

    # fill nimloth and celeborn
    for varname in nimloth_variables:
	fillvalue[0] = getattr(intree,varname); nimloth.GetBranch(varname).Fill()
    for varname in celeborn_variables:
	fillvalue[0] = getattr(intree,varname)[0]; celeborn.GetBranch(varname).Fill()
	fillvalue[0] = getattr(intree,varname)[1]; celeborn.GetBranch(varname).Fill()
    if not isdata:
	fillvalue[0] = getattr(intree,'_weight')
	nimloth.GetBranch('_weight').Fill()
	celeborn.GetBranch('_weight').Fill()
	celeborn.GetBranch('_weight').Fill()
	fillvalue[0] = getattr(intree,'_nTrueInt')
	nimloth.GetBranch('_nTrueInt').Fill()
        celeborn.GetBranch('_nTrueInt').Fill()
        celeborn.GetBranch('_nTrueInt').Fill()

    # get collection of V0's from event	
    v0collection = V0Collection(); v0collection.initFromTreeEntry(intree)
    k0scollection = v0collection.getK0sCollection();
    lambdacollection = v0collection.getLambda0Collection() + v0collection.getLambda0BarCollection()

    # do additional selections here
    extra = {} # make dict of extra variables needed for selections
    extra['primaryVertex'] = (	getattr(intree,'_primaryVertexX'),
				getattr(intree,'_primaryVertexY'),
				getattr(intree,'_primaryVertexZ') )
    extra['beamSpot'] = (   getattr(intree,'_beamSpotX'),
			    getattr(intree,'_beamSpotY'),
			    getattr(intree,'_beamSpotZ') )
    k0scollection.applySelection( selection_name, extra )
    lambdacollection.applySelection( selection_name, extra )

    # fill laurelin
    for k0s in k0scollection:
	fillvalue[0] = k0s.mass; laurelin.GetBranch('_mass').Fill()
	fillvalue[0] = k0s.vertex[0]; laurelin.GetBranch('_vertexX').Fill()
	fillvalue[0] = k0s.vertex[1]; laurelin.GetBranch('_vertexY').Fill()
	fillvalue[0] = k0s.vertex[2]; laurelin.GetBranch('_vertexZ').Fill()
	RPV = np.sqrt(	np.power(k0s.vertex[0]-getattr(intree,'_primaryVertexX'),2)
			+np.power(k0s.vertex[1]-getattr(intree,'_primaryVertexY'),2) )
	fillvalue[0] = RPV; laurelin.GetBranch('_RPV').Fill()
	RBS = np.sqrt(  np.power(k0s.vertex[0]-getattr(intree,'_beamSpotX'),2)
                        +np.power(k0s.vertex[1]-getattr(intree,'_beamSpotY'),2) )
	fillvalue[0] = RBS; laurelin.GetBranch('_RBS').Fill()
	fillvalue[0] = k0s.fourmomentum.Pt(); laurelin.GetBranch('_pt').Fill()
	sumpt = k0s.postrack.fourmomentum.Pt() + k0s.negtrack.fourmomentum.Pt() 
	fillvalue[0] = sumpt; laurelin.GetBranch('_ptSum').Fill()
	fillvalue[0] = k0s.fourmomentum.Eta(); laurelin.GetBranch('_eta').Fill()
	fillvalue[0] = k0s.fourmomentum.Phi(); laurelin.GetBranch('_phi').Fill()
	fillvalue[0] = k0s.postrack.nhits; laurelin.GetBranch('_nHitsPos').Fill()
	fillvalue[0] = k0s.negtrack.nhits; laurelin.GetBranch('_nHitsNeg').Fill()
	fillvalue[0] = k0s.postrack.fourmomentum.Pt(); laurelin.GetBranch('_ptPos').Fill()
	fillvalue[0] = k0s.negtrack.fourmomentum.Pt(); laurelin.GetBranch('_ptNeg').Fill()
	fillvalue[0] = k0s.trackdR(); laurelin.GetBranch('_trackdR').Fill()
	if not isdata: 
	    fillvalue[0] = getattr(intree,'_weight'); laurelin.GetBranch('_weight').Fill()
	    fillvalue[0] = getattr(intree,'_nTrueInt'); laurelin.GetBranch('_nTrueInt').Fill()

    # fill telperion
    for l0 in lambdacollection:
        fillvalue[0] = l0.mass; telperion.GetBranch('_mass').Fill()
        fillvalue[0] = l0.vertex[0]; telperion.GetBranch('_vertexX').Fill()
        fillvalue[0] = l0.vertex[1]; telperion.GetBranch('_vertexY').Fill()
        fillvalue[0] = l0.vertex[2]; telperion.GetBranch('_vertexZ').Fill()
        RPV = np.sqrt(  np.power(l0.vertex[0]-getattr(intree,'_primaryVertexX'),2)
                        +np.power(l0.vertex[1]-getattr(intree,'_primaryVertexY'),2) 
                        +np.power(l0.vertex[2]-getattr(intree,'_primaryVertexZ'),2) )
        fillvalue[0] = RPV; telperion.GetBranch('_RPV').Fill()
        RBS = np.sqrt(  np.power(l0.vertex[0]-getattr(intree,'_beamSpotX'),2)
                        +np.power(l0.vertex[1]-getattr(intree,'_beamSpotY'),2) 
                        +np.power(l0.vertex[2]-getattr(intree,'_beamSpotZ'),2) )
        fillvalue[0] = RBS; telperion.GetBranch('_RBS').Fill()
	fillvalue[0] = l0.fourmomentum.Pt(); telperion.GetBranch('_pt').Fill()
        sumpt = l0.postrack.fourmomentum.Pt() + l0.negtrack.fourmomentum.Pt()        
        fillvalue[0] = sumpt; telperion.GetBranch('_ptSum').Fill()
        fillvalue[0] = l0.fourmomentum.Eta(); telperion.GetBranch('_eta').Fill()
        fillvalue[0] = l0.fourmomentum.Phi(); telperion.GetBranch('_phi').Fill()
	fillvalue[0] = l0.postrack.nhits; telperion.GetBranch('_nHitsPos').Fill()
        fillvalue[0] = l0.negtrack.nhits; telperion.GetBranch('_nHitsNeg').Fill()
	fillvalue[0] = l0.postrack.fourmomentum.Pt(); telperion.GetBranch('_ptPos').Fill()
	fillvalue[0] = l0.negtrack.fourmomentum.Pt(); telperion.GetBranch('_ptNeg').Fill()
	fillvalue[0] = l0.trackdR(); telperion.GetBranch('_trackdR').Fill()
	if not isdata: 
	    fillvalue[0] = getattr(intree,'_weight'); telperion.GetBranch('_weight').Fill()
	    fillvalue[0] = getattr(intree,'_nTrueInt'); telperion.GetBranch('_nTrueInt').Fill()

# write output trees to file
nimloth.SetEntries(); nimloth.Write()
celeborn.SetEntries(); celeborn.Write()
laurelin.SetEntries(); laurelin.Write()
telperion.SetEntries(); telperion.Write()
if not isdata:
    hcounter.Write()
    ntrueint.Write()
outf.Close()
# write closing tag (for automatic crash checkiing)
sys.stderr.write('### done ###\n')
