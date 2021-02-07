##################################################################################
# Script to read 2 variables from flat trees and make 2D sim vs. data histograms #
##################################################################################
# This script creates a 2D-histogram with the number of Kshort decays
# as a function of the radial distance of their vertex and of the sum of pt's of the tracks.
import ROOT
import os
import numpy as np
from array import array
import ctypes
import sys
import json
sys.path.append(os.path.abspath('../pureweighting'))
from addpuscale import getpuscale
sys.path.append(os.path.abspath('../fitting'))
import fit_tools as ft

### Configure input parameters
#histfile = '~/Kshort/histograms/test2d.root' # file to store histograms in
#helpdir = '~/Kshort/histograms/help2d/' # directory to store other useful objects in
histfile = 'test.root'
helpdir = 'test/'
mode = 2
# (mode parameter:	0 = count all instances of varname)
#			1 = count all instances of varname passing an additional condition)
#			2 = subtract background based on sidebands in invariant mass histogram)
treename = 'laurelin'
#extracut = 'bool(getattr(tree,"_passMassCut"))' # ignored if mode != 1
#extracut = 'bool(abs(getattr(tree,"_bi_KsInvMass")-0.4976)<0.01)' # ignored if mode != 1
#extracut = 'bool(abs(getattr(tree,"_bi_LaInvMass")-1.11568)<0.005)' # ignored if mode != 1
extracut = 'bool(2>1)'
# settings for 2D-histgram
xvarname = '_KsRPV'
xbins = array('f',[0.,0.5,1.5,4.,20.])
xnormrange = [0.,0.5] # ignored if normalization != 3
yvarname = '_KsPtPos'
y2varname = '_KsPtNeg' # temporary
#ybins = array('f',[0.,4.,6.,20.])
ybins = array('f',[0.,15.,20.,25.,40.])
ynormrange = [0.,40.] # ignored if normalization != 3
normalization = 3
# (normalization parameter:	0 = no normalization, weights, xsection and lumi set to 1.)
# (				1 = normalize using weights, xsection and lumi.)
# (				2 = same as before but apply normalization to data afterwards.)
# (				3 = same as before but normalize in specified range only.)
# (				4 = normalize number of events to data, not number of instances)
eventtreename = 'nimloth' # ignored if normalization != 4
dataeventweights = 0. # ignored if normalization != 4
mceventweights = 0. # ignored if normalization != 4
# settings for InvMass histograms (ignored if mode != 2)
massvarname = '_KsInvMass'
mxlow = 0.44
mxhigh = 0.56
mnbins = 30

### Configure MC files
mcin = []
mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIISummer16_DYJetsToLL/skim_ztomumu_all.root',
                'label':'simulation',
                'xsection':1.,'luminosity':1.})
#mcin.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_DYJetsToLL_MINIAODSIM/skim_ztoee_1t35.root',
#               'label':'simulation',
#               'xsection':1.,'luminosity':1.})

### Configure data files
datain = []
datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2016_DoubleMuon/skim_ztomumu_all.root'})
#datain.append({'file':'/storage_mnt/storage/user/llambrec/Kshort/files/Run2017E_DoubleEG_MINIAOD/skim_ztoee_1t50.root'})

### Configure input parameters (command line for submission script
cmdargs = sys.argv[1:]
if len(cmdargs)>0:
        coreargs = {'histfile':False,'helpdir':False,'bck_mode':False,'treename':False,
			'normalization':False,'xvarname':False,'yvarname':False,
			'xbins':False,'ybins':False,
                        'mcin':False,'datain':False}
        i = 0
        while(i<len(cmdargs)):
                argname,argval = cmdargs[i].split('=')
                valid = True
                if argname=='histfile': histfile = argval; coreargs['histfile']=True
                elif argname=='helpdir': helpdir = argval; coreargs['helpdir']=True
                elif argname=='bck_mode': mode = int(argval); coreargs['bck_mode']=True
                elif argname=='xvarname': xvarname = argval; coreargs['xvarname']=True
		elif argname=='yvarname': yvarname = argval; coreargs['yvarname']=True
		elif argname=='xbins': xbins = array('f',json.loads(argval)); coreargs['xbins']=True
		elif argname=='ybins': ybins = array('f',json.loads(argval)); coreargs['ybins']=True
                elif argname=='treename': treename = argval; coreargs['treename']=True
                elif argname=='normalization':
                        normalization = int(argval);
                        coreargs['normalization']=True
                elif argname=='mcin': mcin = json.loads(argval); coreargs['mcin']=True
                elif argname=='datain': datain = json.loads(argval); coreargs['datain']=True
                else: valid=False
                if valid:
                        cmdargs.pop(i)
                else: i+=1
        if False in coreargs.values():
                print('ERROR: the following core arguments were not defined:')
                for key in coreargs.keys():
                        if(coreargs[key]==False): print(key)
                exit()
        checknorm1 = {'lumi':False}; checknorm3={'xnormrange':False,'ynormrange':False} 
	checknorm4 = {'eventtree':False}
        checkbck1 = {'extracut':False}
        checkbck2 = {'massvar':False,'mxlow':False,'mxhigh':False,'mnbins':False,'extracut':False}
        for arg in cmdargs:
                argname,argval = arg.split('=')
                if(normalization==1):
                        if argname=='lumi': lumi=float(argval); checknorm1['lumi']=True
                elif(normalization==3):
                        if argname=='xnormrange':
                                xnormrange=json.loads(argval)
                                checknorm3['xnormrange']=True
			if argname=='ynormrange':
				ynormrange=json.loads(argval)
				checknorm3['ynormrange']=True
                elif(normalization==4):
                        if argname=='eventtree':
                                eventtreename = argval
                                checknorm4['eventtree']=True
                if(mode==1):
                        if argname=='extracut':
                                extracut = arg.split('=',1)[1]
                                checkbck1['extracut']=True
                                # (note: extra option 1 should allow to use '=' in extracut)
		elif(mode==2):
                        if argname=='massvar': massvarname = argval; checkbck2['massvar']=True
                        if argname=='mxlow': mxlow = float(argval); checkbck2['mxlow']=True
                        if argname=='mxhigh': mxhigh = float(argval); checkbck2['mxhigh']=True
                        if argname=='mnbins': mnbins = int(argval); checkbck2['mnbins']=True
                        if argname=='extracut': extracut = argval; checkbck2['extracut']=True
        if(normalization==1 and False in checknorm1.values()):
                print('ERROR: requested normalization to xsection and lumi but missing arguments.')
                exit()
        if(normalization==3 and False in checknorm3.values()):
                print('ERROR: requested normalization in range but missing arguments.')
                exit()
        if(normalization==4 and False in checknorm4.values()):
                print('ERROR: requested normalization to events but missing arguments.')
                exit()
        if(mode==1 and False in checkbck1.values()):
                print('ERROR: requested additional background cut but missing arguments.')
                exit()
        if(mode==2 and False in checkbck2.values()):
                print('ERROR: requested background subtraction but missing arguments.')
                exit()

### Setting lumi to 1 unless normalization requests otherwise
if(normalization != 1):
        print('WARNING: lumi set to 1. because of normalization settings.')
        lumi = 1.
        for d in mcin:
                d['luminosity'] = 1.

### Initializations based on input parameters defined above
mbinwidth = float(mxhigh-mxlow)/mnbins
fitrange = [mxlow,mxhigh]
mxcenter = (mxhigh+mxlow)/2.
mxwidth = (mxhigh-mxlow)/4.
if(not os.path.exists(helpdir)):
	os.system("mkdir -p "+helpdir)
nxbins = len(xbins)-1; xlow = xbins[0]; xhigh = xbins[-1]
nybins = len(ybins)-1; ylow = ybins[0]; yhigh = ybins[-1]
xbinwidth = min(np.array(xbins[1:]-np.array(xbins[:-1])))
ybinwidth = min(np.array(ybins[1:]-np.array(ybins[:-1])))
# initialize histograms
# (1D lists: dimension 1: files)
mchistlist = []
datahistlist = []
for i in range(len(mcin)):
        mchistlist.append(ROOT.TH2F("mchistn"+str(i),mcin[i]['label'],nxbins,xbins,nybins,ybins))
        mchistlist[i].SetDirectory(0)
for i in range(len(datain)):
        datahistlist.append(ROOT.TH2F("datahistn"+str(i),"data",nxbins,xbins,nybins,ybins))
        datahistlist[i].SetDirectory(0)
# initialize histograms for invariant mass (per bin)
mcmasshistlist = []
datamasshistlist = []
if mode==2:
	for i in range(len(datain)):
		datamasshistlist.append([])
		for j in range(nxbins):
			datamasshistlist[i].append([])
			for k in range(nybins):
				hist = ROOT.TH1F("datamasshist_"+str(i)+"_"+str(j)+"_"+str(k),"",
									mnbins,mxlow,mxhigh)
				hist.Sumw2()
				hist.SetDirectory(0)
				datamasshistlist[i][j].append(hist)
	for i in range(len(mcin)):
		mcmasshistlist.append([])
		for j in range(nxbins):
			mcmasshistlist[i].append([])
			for k in range(nybins):
				hist = ROOT.TH1F("mcmasshist_"+str(i)+"_"+str(j)+"_"+str(k),"",
						mnbins,mxlow,mxhigh)
				hist.Sumw2()
				hist.SetDirectory(0)
				mcmasshistlist[i][j].append(hist)
# initialize sum of weights for candidates in normalization range
wmcinrange = 0.
wdatainrange = 0.

### loop over instances
def addinputfile(masshistlist,varhist,inlist,index,isdata):
	# notes: - first argument is ignored if mode!=2, pass any variable
	#        - second argument is not ignored if mode==2 but only for bin-finding, not filling.
	f = ROOT.TFile.Open(inlist[index]['file'])
	eventsumweights = 0.
	sumweights=1; xsection=1; lumi=1
        if(not isdata and not normalization==0):
                sumweights = f.Get("hCounter").GetSumOfWeights()
		puscale = f.Get("PUScale")
                xsection = inlist[index]['xsection']
                lumi = inlist[index]['luminosity']
        winrange = 0.
	# if normalization==4: loop over events and sum weights
	if(normalization==4):
		eventtree = f.Get(eventtreename)
		if isdata:
			eventsumweights = eventtree.GetEntries()
		else:
			sumweights = f.Get("hCounter").GetSumOfWeights()
			for j in range(int(eventtree.GetEntries())):
				eventtree.GetEntry(j)
				weight = getattr(eventtree,'_weight')
				weight *= getpuscale(getattr(eventtree,'_nTrueInt'),puscale)
				eventsumweights += weight/sumweights*xsection*lumi
	# loop over V0 instances 
	tree = f.Get(treename)
	# (for testing purposes: use only a fracion of the data !!!)
	for j in range(int(tree.GetEntries()/1.)):
		tree.GetEntry(j)
		weight = 1.
		if(not isdata and not normalization==0):
			weight = getattr(tree,'_weight')
			weight *= getpuscale(getattr(tree,'_nTrueInt'),puscale)
		xvarvalue = getattr(tree,xvarname)
		yvarvalue = getattr(tree,yvarname)
		if(xvarvalue>xlow and xvarvalue<xhigh
		   and yvarvalue>ylow and yvarvalue<yhigh):
			if(mode==0):
				varhist.Fill(xvarvalue,yvarvalue,weight*lumi*xsection/sumweights)
			elif(mode==1):
				if(eval(extracut)):
					varhist.Fill(xvarvalue,yvarvalue,weight*lumi*xsection/sumweights)
			elif(mode==2):
				if(eval(extracut)):
					binx = varhist.GetXaxis().FindBin(xvarvalue)-1
					biny = varhist.GetYaxis().FindBin(yvarvalue)-1
					massvarvalue = getattr(tree,massvarname)
					masshistlist[index][binx][biny].Fill(massvarvalue,weight*lumi
										*xsection/sumweights)
		### temp: second y value:
		if y2varname != '':
		    y2varvalue = getattr(tree,y2varname)
		    if(xvarvalue>xlow and xvarvalue<xhigh
			and y2varvalue>ylow and y2varvalue<yhigh):
                        if(mode==0):
			        varhist.Fill(xvarvalue,y2varvalue,weight*lumi*xsection/sumweights)
                        elif(mode==1):
                                if(eval(extracut)):
                                        varhist.Fill(xvarvalue,y2varvalue,weight*lumi*xsection/sumweights)
                        elif(mode==2):
                                if(eval(extracut)):
                                        binx = varhist.GetXaxis().FindBin(xvarvalue)-1
                                        biny = varhist.GetYaxis().FindBin(y2varvalue)-1
                                        massvarvalue = getattr(tree,massvarname)
                                        masshistlist[index][binx][biny].Fill(massvarvalue,weight*lumi
                                                                                *xsection/sumweights)
		### end of temp

		if(normalization==3 and xvarvalue>xnormrange[0] and xvarvalue<xnormrange[1]
		   and yvarvalue>ynormrange[0] and yvarvalue<ynormrange[1]):
			if(mode==0): winrange += weight*lumi*xsection/sumweights
			elif(mode==1 and eval(extracut)): winrange += weight*lumi*xsection/sumweights
			# Note: if mode=2: use different technique (see also mcvsdata_fillrd.py)
	f.Close()
	return eventsumweights,winrange

print('adding simulation files...')
for i in range(len(mcin)):
	print('file '+str(i+1)+' of '+str(len(mcin)))
	temp = addinputfile(mcmasshistlist,mchistlist[i],mcin,i,False)
	mceventweights += temp[0]
	wmcinrange += temp[1]
	print(temp)
print('adding data files...')
for i in range(len(datain)):
	print('file '+str(i+1)+' of '+str(len(datain)))
	temp = addinputfile(datamasshistlist,datahistlist[i],datain,i,True)
	dataeventweights += temp[0]
	wdatainrange += temp[1]

### Help functions to perform background fit and subtract it (only needed if mode == 2)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
# following is deprecated, use import from mcvsdata_fillrd.py!
def subtract_background(hist,label,extrainfo):
        # only first argument is important for fit, rest is only plotting
        # note that the parameters mxcenter, mxwidth, mxlow, mxhigh, mnbins and fitrange are implied globally!
        histclone = hist.Clone()
        binlow = histclone.FindBin(mxcenter-mxwidth)
        binhigh = histclone.FindBin(mxcenter+mxwidth)
        # take into account only sidebands, not peak
        for i in range(binlow+1,binhigh+1):
                histclone.SetBinContent(i,0)
                histclone.SetBinError(i,0)
        guess = [0.,0.]
        backfit,paramdict = ft.poly_fit(histclone,fitrange,guess,"Q0")
        ft.plot_fit(hist,label,None,paramdict,backfit,'invariant mass (GeV)',
                        'number of reconstructed vertices','',
                        helpdir+hist.GetName()+'.png',extrainfo)
        # METHOD 1: subtract background from peak and count remaining instances
        histclone2 = hist.Clone()
        histclone2.Add(backfit,-1)
        npeak = 0.
        npeak_error2 = 0.
        for i in range(binlow+1,binhigh+1):
                npeak += histclone2.GetBinContent(i)
                npeak_error2 += np.power(histclone2.GetBinError(i),2)
	return (npeak,np.sqrt(npeak_error2))

### Fill 2D histograms if not done so before 
if(mode == 2):
	print('performing fits to background in all bins...')
        if '_Ks' in massvarname: massinfo = 'HACK_KS'
        elif '_La' in massvarname: massinfo = 'HACK_LA'
        elif '_JP' in massvarname: massinfo = 'HACK_JP'
        else: massinfo = ''
        for i in range(nxbins):
		for j in range(nybins):
                	extrainfo = '{0:.2f} < '.format(xbins[i])+xvarname+' < {0:.2f}'.format(xbins[i+1])
			extrainfo += '<< {0:.2f} < '.format(ybins[j])+yvarname+' < {0:.2f}'.format(ybins[j+1])
                	extrainfo += '<< <<'+massinfo
                	for k in range(len(mcin)):
				print(str(k)+' '+str(i)+' '+str(j))
                        	res = subtract_background(mcmasshistlist[k][i][j],'simulation',extrainfo)
                      	  	ncandidates = res[0]
				error = res[1] # don't use peak fit results for now as they are unstable
                       	 	mchistlist[k].SetBinContent(i+1,j+1,ncandidates)
                        	mchistlist[k].SetBinError(i+1,j+1,error)
                	# (bin 0 is underflow bin!)
                	for k in range(len(datain)):
                        	res = subtract_background(datamasshistlist[k][i][j],'data',extrainfo)
                     		ncandidates = res[0]
				error = res[1]
				datahistlist[k].SetBinContent(i+1,j+1,ncandidates)
				datahistlist[k].SetBinError(i+1,j+1,error)
                	# (bin 0 is underflow bin!)

### Normalize MC histograms to data if needed
if(normalization==2 or normalization==3):
        mchist = mchistlist[0].Clone()
        for i in range(1,len(mchistlist)):
                mchist.Add(mchistlist[i])
        datahist = datahistlist[0].Clone()
        for i in range(1,len(datahistlist)):
                datahist.Add(datahistlist[i])
if(normalization==2):
	print('post-processing simulation files...')
	ndataw = datahist.GetSumOfWeights()
	nmcw = mchist.GetSumOfWeights()
	scale = ndataw/nmcw
	for hist in mchistlist:
		hist.Scale(scale)
if(normalization==3):
	print('post-processing simulation files...')
	# need to recalculate datawinrange and mcwinrange if bck_mode==2, 
        # as they cannot be calculated in event loop
        if(mode==2):
                wdatainrange = datahist.Integral(datahist.GetXaxis().FindBin(xnormrange[0]+0.1*xbinwidth),
                               			datahist.GetXaxis().FindBin(xnormrange[1]-0.1*xbinwidth),
						datahist.GetYaxis().FindBin(ynormrange[0]+0.1*ybinwidth),
						datahist.GetYaxis().FindBin(ynormrange[1]-0.1*ybinwidth))
                wmcinrange = mchist.Integral(mchist.GetXaxis().FindBin(xnormrange[0]+0.1*xbinwidth),
                                                mchist.GetXaxis().FindBin(xnormrange[1]-0.1*xbinwidth),
                                                mchist.GetYaxis().FindBin(ynormrange[0]+0.1*ybinwidth),
                                                mchist.GetYaxis().FindBin(ynormrange[1]-0.1*ybinwidth))
	scale = wdatainrange/wmcinrange
	for hist in mchistlist:
		hist.Scale(scale)
if(normalization==4):
	print('post-processing simulation files...')
	scale = dataeventweights/mceventweights
	for hist in mchistlist:
		mchist.Scale(scale)

### Write histograms to file
print('writing histograms to file...')
f = ROOT.TFile.Open(histfile,"recreate")
for hist in mchistlist+datahistlist:
        hist.Write(hist.GetName())
normalization_st = ROOT.TVectorD(1); normalization_st[0] = normalization
normalization_st.Write("normalization")
if(normalization==3):
	normrange_st = ROOT.TVectorD(4)
	normrange_st[0] = xnormrange[0]; normrange_st[1] = xnormrange[1]
	normrange_st[2] = ynormrange[0]; normrange_st[3] = ynormrange[1]
	normrange_st.Write("normrange")
f.Close()
print('done')
