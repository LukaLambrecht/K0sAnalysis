####################################################################
# Reading a skimmed root file, perform high-level skimming on V0's #
####################################################################
import sys
import ROOT
import math
import numpy as np
from array import array

### some constants
ksmass = 0.49761;
lambdamass = 1.1157;

# for testing:
finloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL_1215/skim_ztomumu_all.root'
foutloc = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL_1215/skim_ztomumu_selectedpt2.root'
if('Fall' in finloc or 'Autumn' in finloc or 'Summer' in finloc):
	isdata = False
else:
	isdata = True

### part 1: simply copy hcounter, event and lepton trees
fin = ROOT.TFile.Open(finloc)
evttree = fin.Get("nimloth")
leptree = fin.Get("celeborn")
kstree = fin.Get("laurelin")
latree = fin.Get("telperion")
if not isdata:
        sumweights = fin.Get("hCounter")
fout = ROOT.TFile(foutloc,"recreate")
laurelin = kstree.CloneTree(0) # data structure for Kshort variables
telperion = latree.CloneTree(0) # data structure for Lambda variables
print('cloning event and lepton variables...')
evttree.CloneTree().Write()
leptree.CloneTree().Write()
if not isdata:
	sumweights.Write()

### part 2: apply selection on Kshorts
print('selecting K0S...')
for j in range(kstree.GetEntries()):
	kstree.GetEntry(j)
	
	# selection: pt threshold
	if(getattr(kstree,"_KsPtPos")<2. or getattr(kstree,"_KsPtNeg")<2.):
		continue
	# selection: impact parameter
	if(abs(getattr(kstree,"_KsD0Pos"))<0. or abs(getattr(kstree,"_KsD0Neg"))<0.):
		continue
	laurelin.Fill()

### part 3: apply selection on Lambdas
print('selecting Lambdas...')
for j in range(latree.GetEntries()):
        latree.GetEntry(j)
        
        # selection: pt threshold
	if(getattr(latree,"_LaPtPos")<2. or getattr(latree,"_LaPtNeg")<2.):
                continue
        # selection: impact parameter
        if(abs(getattr(latree,"_LaD0Pos"))<0. or abs(getattr(latree,"_LaD0Neg"))<0.):
                continue
        telperion.Fill()

laurelin.SetEntries()
telperion.SetEntries()
fout.Write()
fout.Close()
print('finished writing trees.')
