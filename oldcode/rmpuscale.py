###########################################################################
# Python script to remove a pileup reweighting histogram from a root file #
###########################################################################
# command line args:
# - root file to work on

import sys
from array import array
import ROOT
import os

def rmpuscale(infilename):
    
    ### initializations
    puname = 'PUScale'
    tmpfilename = os.path.splitext(infilename)[0]+'_tmp.root'
    
    ### open input file
    mcfile = ROOT.TFile.Open(infilename,'update')
    tmpfile = ROOT.TFile.Open(tmpfilename,'recreate')

    ### check if puscale is present
    has_puscale = False
    for key in mcfile.GetListOfKeys():
	if key.GetName()==puname:
	    has_puscale = True
    if not has_puscale:
	print('### ERROR ###: no pileup scale is present in the input file.')
	return None
    
    ### copy all but puscale to a new file
    objs = []
    for key in mcfile.GetListOfKeys():
	if key.GetName()==puname: continue
	print('trying to read {}...'.format(key.GetName()))
	obj = mcfile.Get( key.GetName() )
	obj.SetDirectory(ROOT.gROOT)
	try:
	    objs.append(obj.CloneTree()) # for trees
	except:
	    objs.append(obj) # for histograms

    for obj in objs:
	print('writing {}...'.format(obj.GetName()))
	obj.Write()
    mcfile.Close()
    tmpfile.Close()

if __name__=='__main__':
    ### some checks on command line arguments
    if len(sys.argv)!=2:
        print('### ERROR ###: too few command line args')
        print('               usage: python rmpuweight.py <rootfile>')
        sys.exit()
    rmpuscale(sys.argv[1])
    
