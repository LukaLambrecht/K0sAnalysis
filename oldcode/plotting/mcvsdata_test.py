import json
import os
from array import array
import sys
import pipes

### Configure input parameters (hard-coded)
histfile = '~/Kshort/histograms/test.root' 
helpdir = '~/Kshort/histograms/help/' 
bck_mode = 1
varname = '_JPRPos'
treename = 'laurelin'
extracut = 'bool(getattr(tree,"_passMassCut"))' # ignored if bck_mode != 1
# settings for RPos histgram
bintype = 'variable' # choose from 'fixed' (fixed bin size) or 'variable'
xlow = -0.; xhigh = 2.; nbins = 30 # ignored if bintype is 'variable'
bins = [0.,1.,2.,4.,6.,10.,20.] # ignored if bintype is 'fixed'
normalization = 3
lumi = 1590. # automatically set to 1 if normalization != 1
normrange = [0.,0.2] # ignored if normalization != 3
eventtreename = 'nimloth' # ignored if normalization != 4
# settings for InvMass histograms (ignored if bck_mode != 2)
massvarname = '_LaInvMass'
mxlow = 1.085
mxhigh = 1.145
mnbins = 20

### Setting lumi to 1 unless normalization requests otherwise
if(normalization != 1):
	print('WARNING: lumi set to 1. because of normalization settings.')
	lumi = 1.

### Configure MC files
mcin = []
mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_BToJPsi_MINIAODSIM/skim_jpsi_1t12.root',
		'label':r'B #rightarrow J/#Psi',
		'xsection':3.88e5,'luminosity':lumi})
mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_JPsiToMuMu_MINIAODSIM/skim_jpsi_1t20.root',
		'label':r'prompt J/#Psi',
		'xsection':8.79e5*0.0397,'luminosity':lumi})
'''mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL_MINIAODSIM/skim_ztomumu_all.root',
		'label':r'simulation','xsection':1.,'luminosity':lumi}) # xsection 6529 (?)'''

### Configure data files
datain = []
datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_withloosetriggers/skim_jpsi_1t200.root'})
#datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleMuon_1210/skim_ztomumu_1t200.root'})

# core:
cmdargs = 'histfile='+histfile+' helpdir='+helpdir+' bck_mode='+str(bck_mode)+' varname='+varname
cmdargs = cmdargs+' treename='+treename+' bintype='+bintype+' normalization='+str(normalization)
cmdargs = cmdargs+' mcin='+pipes.quote(json.dumps(mcin,separators=(",",":")))
cmdargs = cmdargs+' datain='+pipes.quote(json.dumps(datain,separators=(",",":")))

# additional:
#cmdargs = cmdargs+' xlow='+str(xlow)+' xhigh='+str(xhigh)+' nbins='+str(nbins)
cmdargs = cmdargs+' bins='+pipes.quote(json.dumps(bins,separators=(",",":")))
cmdargs = cmdargs+' normrange='+pipes.quote(json.dumps(normrange,separators=(",",":")))
cmdargs = cmdargs+' extracut='+pipes.quote(extracut)
print(cmdargs)
os.system('python mcvsdata_fillrd.py '+cmdargs)

### Part 2
histfile = '~/Kshort/histograms/test.root' # file to read histograms
title = r'#pi^{+} from K^{0}_{S} isolation'
xaxistitle = 'relative isolation (dimensionless)' # set x axis title
yaxistitle = 'number of vertices' # set y axis title of upper graph

cmdargs = 'histfile='+histfile+' histtitle='+pipes.quote(title)
cmdargs = cmdargs+' xaxistitle='+pipes.quote(xaxistitle)
cmdargs = cmdargs+' yaxistitle='+pipes.quote(yaxistitle)
os.system('python mcvsdata_plot.py '+cmdargs)
