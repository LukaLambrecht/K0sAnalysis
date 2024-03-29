##################################################################################
# script to read 2 variables from flat trees and make 2D sim vs. data histograms #
##################################################################################

import ROOT
import os
import sys
import copy
import math
import numpy as np
from array import array
import json
sys.path.append(os.path.abspath('../fitting'))
from count_peak import count_peak
sys.path.append(os.path.abspath('../pureweighting'))
import addpuscale as pu

sys.stderr.write('###starting###\n')

### Set global program parameters

def parse_arguments():
    ### configure input parameters (command line for submission script)

    if len(sys.argv)==1: return {}
    cmdargs = sys.argv[1:]
    coreargs = {'histfile':None,'helpdir':None,'bck_mode':None,'treename':None,
		    'xvarname':None,'xbins':None,'yvarname':None,'ybins':None,
		    'normalization':None,
                    'mcin':None,'datain':None}
    otherargs = {'extracut':'','normrange':[0,0],'normvariable':'','eventtreename':'',
                'sidebandvarname':'','sidexlow':0,'sidexhigh':1,'sidenbins':1}
    i = 0
    while(i<len(cmdargs)):
        argname,argval = cmdargs[i].split('=')
        valid = True
        if argname=='histfile': coreargs['histfile'] = argval
        elif argname=='helpdir': coreargs['helpdir'] = argval
        elif argname=='bck_mode': coreargs['bck_mode'] = argval
	elif argname=='treename': coreargs['treename'] = argval
        elif argname=='xvarname': coreargs['xvarname'] = argval
        elif argname=='xbins': coreargs['xbins'] = array('f',json.loads(argval))
	elif argname=='yvarname': coreargs['yvarname'] = argval
        elif argname=='ybins': coreargs['ybins'] = array('f',json.loads(argval))
        elif argname=='normalization': coreargs['normalization'] = int(argval);
        elif argname=='mcin': coreargs['mcin'] = json.loads(argval)
        elif argname=='datain': coreargs['datain'] = json.loads(argval)
        else: valid=False
        if valid:
                cmdargs.pop(i)
        else: i+=1
    if None in coreargs.values():
        print('ERROR: the following core arguments were not defined:')
        for key in coreargs.keys():
            if(coreargs[key] is None): print(key)
        return {}
    checknorm3={'normrange':False,'normvariable':False}
    checknorm4 = {'eventtreename':False}
    checkbck = {'sidevarname':False,'sidexlow':False,'sidexhigh':False,'sidenbins':False}
    for arg in cmdargs:
        argname,argval = arg.split('=')
        # special optons not related to any particular setting:
        if(argname=='extracut'): otherargs['extracut'] = arg.split('=',1)[1]
        # (note: extra option 1 should allow to use '=' in extracut)
        if(argname=='reductionfactor'): otherargs['reductionfactor'] = argval
        # specific options:
        elif(coreargs['normalization']==3 or coreargs['normalization']==5):
            if argname=='normrange':
                otherargs['normrange'] = json.loads(argval); checknorm3['normrange']=True
	    if argname=='normvariable':
                otherargs['normvariable'] = argval; checknorm3['normvariable']=True
        elif(coreargs['normalization']==4):
            if argname=='eventtreename':
                otherargs['eventtreename'] = argval; checknorm4['eventtreename']=True
        if(coreargs['bck_mode']=='sideband'):
            if argname=='sidevarname':
                otherargs['sidevarname'] = argval; checkbck['sidevarname']=True
            if argname=='sidexlow':
                otherargs['sidexlow'] = float(argval); checkbck['sidexlow']=True
            if argname=='sidexhigh':
                otherargs['sidexhigh'] = float(argval); checkbck['sidexhigh']=True
            if argname=='sidenbins':
                otherargs['sidenbins'] = int(argval); checkbck['sidenbins']=True
    if((coreargs['normalization']==3 or coreargs['normalization']==5)
        and False in checknorm3.values()):
        print('ERROR: requested normalization in range but missing arguments.')
        for arg in checknorm3.keys():
            if not checknorm3[arg]: print('  '+arg)
        return {}
    if(coreargs['normalization']==4 and False in checknorm4.values()):
        print('ERROR: requested normalization to events but missing arguments.')
        for arg in checknorm4.keys():
            if not checknorm4[arg]: print('  '+arg)
        return {}
    if(coreargs['bck_mode']=='sideband' and False in checkbck.values()):
        print('ERROR: requested background subtraction but missing arguments.')
        for arg in checkbck.keys():
            if not checkbck[arg]: print('  '+arg)
        return {}
    return dict(coreargs.items()+otherargs.items())

args = {}
if len(sys.argv)>1:
    args = parse_arguments()
    if len(args.keys())==0: sys.exit()
else:
    args['histfile'] = os.path.abspath('../histograms/test.root')
    args['helpdir'] = os.path.abspath('../histograms/test/')
    args['bck_mode'] = 'default'
    # (bck_mode parameter:  default = count all instances of varname)
    #                       sidebands = subtract background based on sidebands in another variable)
    args['treename'] = 'laurelin'
    args['extracut'] = 'bool(2>1)'
    # settings for 2D-histogram
    args['xvarname'] = '_KsRPV'
    args['xbins'] = array('f',[0.,0.5,1.5,4.,20.])
    args['yvarname'] = '_KsSumPt'
    args['ybins'] = array('f',[0.,15.,20.,25.,40.])
    args['normalization'] = 3
    # (normalization parameter:	0 = no normalization, weights, xsection and lumi set to 1.)
    # (				1 = normalize using weights, xsection and lumi.)
    # (				2 = same as before but apply normalization to data afterwards.)
    # (				3 = same as before but normalize in specified range only.)
    # (				4 = normalize number of events to data, not number of instances)
    args['normrange'] = [0.,0.5] # ignored if normalization != 3 or 5
    args['normvariable'] = '_KsRPV' # ignroed if normalization != 3 or 5
    args['eventtreename'] = 'nimloth' # ignored if normalization != 4
    # settings for sideband histograms (ignored if mode != 2)
    args['sidevarname'] = '_KsInvMass'
    args['sidexlow'] = 0.44
    args['sidexhigh'] = 0.56
    args['sidenbins'] = 30
    # configure MC files
    args['mcin'] = []
    args['mcin'].append({'file':'/user/llambrec/K0sAnalysis/files/oldfiles/RunIISummer16_DYJetsToLL/skim_ztomumu_all.root','label':'simulation','xsection':6077.22,'luminosity':35900.})
    # configure data files
    args['datain'] = []
    args['datain'].append({'file':'/user/llambrec/K0sAnalysis/files/oldfiles/Run2016_DoubleMuon/skim_ztomumu_all.root','label':'data','luminosity':35900.})
    args['reductionfactor'] = 30.

### Check if input files exist:
allexist = True
for f in args['mcin']:
    if not os.path.exists(f['file']):
        print('### ERROR ###: input file '+f['file']+' does not exist.')
        allexist=False
for f in args['datain']:
    if not os.path.exists(f['file']):
        print('### ERROR ###: input file '+f['file']+' does not exist.')
        allexist=False
if not allexist: sys.exit()

### Check luminosity
args['lumi'] = sum([args['mcin'][i]['luminosity'] for i in range(len(args['mcin']))])
lumitest = sum([args['datain'][i]['luminosity'] for i in range(len(args['datain']))])
if( abs(lumitest-args['lumi'])/float(args['lumi'])>0.001 ):
    print('WARNING: total luminosity for data and simulation do not agree!')
    print('(luminosity values for data are only used for plot labels;')
    print(' the values for simulations are used in event weighting and to calculate the sum)')

### Initializations based on input parameters defined above
# bin operations
args['sidebinwidth'] = float(args['sidexhigh']-args['sidexlow'])/args['sidenbins']
# (ignored if bck_mode != 2)
args['fitrange'] = [args['sidexlow'],args['sidexhigh']] # (ignored if bck_mode != 2)
args['sidexcenter'] = (args['sidexhigh']+args['sidexlow'])/2. # (ignored if bck_mode != 2)
args['sidexwidth'] = (args['sidexhigh']-args['sidexlow'])/4. # (ignored if bck_mode != 2)
# weights
dataeventweights = 0. # ignored if normalization != 4
mceventweights = 0. # ignored if normalization != 4
datawinrange = 0. # ignored if normalization != 3
mcwinrange = 0. # ignored if normalization != 3
if(not os.path.exists(args['helpdir'])):
    os.makedirs(args['helpdir'])
nxbins = len(args['xbins'])-1; xlow = args['xbins'][0]; xhigh = args['xbins'][-1]
nybins = len(args['ybins'])-1; ylow = args['ybins'][0]; yhigh = args['ybins'][-1]
minxbinwidth = min(np.array(args['xbins'][1:]-np.array(args['xbins'][:-1])))
minybinwidth = min(np.array(args['ybins'][1:]-np.array(args['ybins'][:-1])))

# initialize histograms
# (1D lists: dimension 1: files)
mchistlist = []
datahistlist = []
for i in range(len(args['mcin'])):
    mchistlist.append(ROOT.TH2F(args['mcin'][i]['label'],args['mcin'][i]['label'],
				nxbins,args['xbins'],nybins,args['ybins']))
    mchistlist[i].SetDirectory(0)
for i in range(len(args['datain'])):
    datahistlist.append(ROOT.TH2F(args['datain'][i]['label'],args['datain'][i]['label'],
				nxbins,args['xbins'],nybins,args['ybins']))
    datahistlist[i].SetDirectory(0)
# initialize histograms for sideband variable (per bin in main variables)
# (3D lists: dimension 1: different files, dim 2 and 3: different main variable bins)
mcsidehistlist = []
datasidehistlist = []
if args['bck_mode']=='sideband':
    for i in range(len(args['datain'])):
	datasidehistlist.append([])
	for j in range(nxbins):
	    datasidehistlist[i].append([])
	    for k in range(nybins):
		hist = ROOT.TH1F(args['datain'][i]['label']+'_xbin'+str(j)+'_ybin'+str(k),"",
                             args['sidenbins'],args['sidexlow'],args['sidexhigh'])
		hist.Sumw2()
		hist.SetDirectory(0)
		datasidehistlist[i][j].append(hist)
    for i in range(len(args['mcin'])):
	mcsidehistlist.append([])
	for j in range(nxbins):
	    mcsidehistlist[i].append([])
	    for k in range(nybins):
		hist = ROOT.TH1F(args['mcin'][i]['label']+'_xbin'+str(j)+'_ybin'+str(k),"",
                             args['sidenbins'],args['sidexlow'],args['sidexhigh'])
		hist.Sumw2()
		hist.SetDirectory(0)
		mcsidehistlist[i][j].append(hist)
# initialize histograms for sideband variable for normalization in range
# (1D lists: dimesion 1: different files)
mcnormsidehistlist = []
datanormsidehistlist = []
if( args['bck_mode']=='sideband' and args['normalization']==3 ):
    for sample in args['datain']:
        hist = ROOT.TH1F(sample['label']+'_norm',"",args['sidenbins'],args['sidexlow'],args['sidexhigh'])
        hist.Sumw2()
        hist.SetDirectory(0)
        datanormsidehistlist.append(hist)
    for sample in args['mcin']:
        hist = ROOT.TH1F(sample['label']+'_norm',"",args['sidenbins'],args['sidexlow'],args['sidexhigh'])
        hist.Sumw2()
        hist.SetDirectory(0)
        mcnormsidehistlist.append(hist)

### loop over instances and fill histograms

def addinputfile(inlist, index, isdata, varhist,
    sidehistlist=None, sidenormhistlist=None, gargs=None):
    ### fill histogram belonging to a certain sample
    # input arguments: 
    # - inlist = input structure (list of dicts) containing sample info
    # - index = index in inlist for current sample
    # - isdata = bool whether current sample is data
    # - varhist = histogram to be filled
    #               (if not running in sideband subtraction mode)
    # - sidehistlist = histograms of sideband variable to be filled 
    #                   (if running in sideband subraction mode)
    # - gargs = dict containing global program settings

    f = ROOT.TFile.Open(inlist[index]['file'])
    eventsumweights = 0.
    sumweightsinrange = 0.
    sumweights=1; xsection=1; lumi=1
    puscale = None
    if(not isdata and not gargs['normalization']==0):
        try: sumweights = f.Get("hCounter").GetSumOfWeights()
        except: print('### WARNING ###: no valid hCounter in file!')
        try:
            puscale = f.Get("PUScale")
            test = puscale.GetBinContent(1)
        except:
            print('### WARNING ###: no valid PUScale in file!')
            puscale = None
        xsection = inlist[index]['xsection']
        lumi = inlist[index]['luminosity']
    # in case normalization of number of events is requested, get number of events
    if(args['normalization']==4):
        eventtree = f.Get(gargs['eventtreename'])
        if isdata:
            eventsumweights = eventtree.GetEntries()
        else:
            for j in range(int(eventtree.GetEntries())):
                eventtree.GetEntry(j)
                weight = getattr(eventtree,'_weight')
                if puscale is not None: weight *= pu.getpuscale(getattr(eventtree,'_nTrueInt'),puscale)
                eventsumweights += weight/sumweights*xsection*lumi
    # loop over V0 instances 
    tree = f.Get(gargs['treename'])
    red = 1
    if( 'reductionfactor' in gargs.keys() ): red = float(gargs['reductionfactor'])
    nentries = int(tree.GetEntries()/red)
    for j in range(nentries):
        if(j%5000==0):
            percent = j*100/nentries
            sys.stdout.write("\r"+str(percent)+'%')
            sys.stdout.flush()
        tree.GetEntry(j)

	# set correct weight for this entry
        weight = 1.
        if(not isdata and not gargs['normalization']==0):
            weight = getattr(tree,'_weight')
            if puscale is not None: weight *= pu.getpuscale(getattr(tree,'_nTrueInt'),puscale)

        # determine the variable value and do some extra checks
	xvarvalue = getattr(tree,args['xvarname'])
	yvarvalue = getattr(tree,args['yvarname'])
        # safety for nan values (not observed for RPV, but sometimes for RPV significance)
        if math.isnan(xvarvalue): continue
        if math.isnan(yvarvalue): continue
	# evaluate an extra selection condition if needed
        if('extracut' in gargs and len(gargs['extracut'])>0):
            if not eval(gargs['extracut']): continue
        # determine if this value is out of range
	if(xvarvalue<gargs['xbins'][0] or xvarvalue>gargs['xbins'][-1]): continue
	if(yvarvalue<gargs['ybins'][0] or yvarvalue>gargs['ybins'][-1]): continue

        # value is valid, now fill it in the correct histogram
        # case of no background subtraction
	if(gargs['bck_mode']=='default'):
	    varhist.Fill(xvarvalue,yvarvalue,weight*lumi*xsection/sumweights)
	    if(gargs['normalization']==3):
                normvalue = getattr(tree,gargs['normvariable'])
                if( normvalue>gargs['normrange'][0] 
                    and normvalue<gargs['normrange'][1] ):
		    sumweightsinrange += weight*lumi*xsection/sumweights
        # handle case of background subtraction
	elif(gargs['bck_mode']=='sideband'):
	    binx = varhist.GetXaxis().FindBin(xvarvalue)-1
	    biny = varhist.GetYaxis().FindBin(yvarvalue)-1
	    sidevarvalue = getattr(tree,gargs['sidevarname'])
	    sidehistlist[index][binx][biny].Fill(sidevarvalue,weight*lumi*xsection/sumweights)
            if(gargs['normalization']==3):
                normvalue = getattr(tree,gargs['normvariable'])
                if( normvalue>gargs['normrange'][0]
                    and normvalue<gargs['normrange'][1] ):
                    sidenormhistlist[index].Fill(sidevarvalue,weight*lumi*xsection/sumweights)
    f.Close()
    sys.stdout.write("\r"+'100%'+"\n")
    sys.stdout.flush()
    return eventsumweights,sumweightsinrange

print('adding simulation files...')
for i in range(len(args['mcin'])):
    print('file '+str(i+1)+' of '+str(len(args['mcin'])))
    mchist = mchistlist[i]
    temp = addinputfile(args['mcin'],i,False,mchist,
                        sidehistlist=mcsidehistlist,
                        sidenormhistlist=mcnormsidehistlist,
                        gargs=args)
    mceventweights += temp[0]
    mcwinrange += temp[1]
print('adding data files...')
for i in range(len(args['datain'])):
    print('file '+str(i+1)+' of '+str(len(args['datain'])))
    datahist = datahistlist[i]
    temp = addinputfile(args['datain'],i,True,datahist,
                        sidehistlist=datasidehistlist,
                        sidenormhistlist=datanormsidehistlist,
                        gargs=args)
    dataeventweights += temp[0]
    datawinrange += temp[1]

### Fill 2D histograms if running in background subtraction mode
 
if(args['bck_mode']=='sideband'):
    print('performing fits to background in all bins...')
    gargs = copy.copy(args)
    for i in range(nxbins):
	for j in range(nybins):
	    # define extra info
            extrainfo = '{0:.2f} < '.format(args['xbins'][i])
	    extrainfo += args['xvarname']
	    extrainfo += ' < {0:.2f}'.format(args['xbins'][i+1])
	    extrainfo += '<< {0:.2f} < '.format(args['ybins'][j])
	    extrainfo += args['yvarname']
	    extrainfo +=' < {0:.2f}'.format(args['ybins'][j+1])
            for k in range(len(args['mcin'])):
		gargs['lumi'] = args['mcin'][k]['luminosity']
		(npeak,nerror) = count_peak(mcsidehistlist[k][i][j],'simulation',
					    extrainfo,gargs,mode='hybrid')
                mchistlist[k].SetBinContent(i+1,j+1,npeak)
                mchistlist[k].SetBinError(i+1,j+1,nerror)
	    for k in range(len(args['datain'])):
		gargs['lumi'] = args['datain'][k]['luminosity']
		(npeak,nerror) = count_peak(datasidehistlist[k][i][j],'data',
                                        extrainfo,gargs,mode='hybrid')
		datahistlist[k].SetBinContent(i+1,j+1,npeak)
		datahistlist[k].SetBinError(i+1,j+1,nerror)

### Normalize MC histograms to data if needed

# for normalization equalling 2,
# calculate sum of MC and sum of data histograms,
# and scale total MC to total data
if(args['normalization']==2):
    mchist = mchistlist[0].Clone()
    for i in range(1,len(mchistlist)): mchist.Add(mchistlist[i])
    datahist = datahistlist[0].Clone()
    for i in range(1,len(datahistlist)): datahist.Add(datahistlist[i])
    ndataw = datahist.GetSumOfWeights()
    nmcw = mchist.GetSumOfWeights()
    scale = ndataw/nmcw
    for hist in mchistlist: hist.Scale(scale)

# for normalization equalling 3,
# calculate sum of weights of MC events and data events,
# for events with a specified variable in a specified range
if(args['normalization']==3):
    # use datawinrange and mcwinrange calculated in event loop,
    # but for sideband background subtraction, they need to be recalculated
    # by fitting the background in the sideband histograms
    if(args['bck_mode']=='sideband'):
        datawinrange = 0.
        mcwinrange = 0.
        extrainfo = '{0:.2f} < '.format(args['normrange'][0])
        extrainfo += args['normvariable']
        extrainfo += ' < {0:.2f}'.format(args['normrange'][1])
        for j in range(len(args['mcin'])):
            gargs['lumi'] = args['mcin'][j]['luminosity']
            (npeak,nerror) = count_peak(mcnormsidehistlist[j],'simulation',
                                        extrainfo,gargs,mode='hybrid')
            mcwinrange += npeak
        for j in range(len(args['datain'])):
            gargs['lumi'] = args['datain'][j]['luminosity']
            (npeak,nerror) = count_peak(datanormsidehistlist[j],'data',
                                        extrainfo,gargs,mode='hybrid')
            datawinrange += npeak
    scale = datawinrange/mcwinrange
    for hist in mchistlist: hist.Scale(scale)

# for normalization equalling 4, scale using event weights
if(args['normalization']==4):
    print('post-processing simulation files...')
    scale = dataeventweights/mceventweights
    for hist in mchistlist:
	mchist.Scale(scale)

### Write histograms to file

print('writing histograms to file...')
f = ROOT.TFile.Open(args['histfile'],"recreate")
# write histograms
for hist in mchistlist+datahistlist: hist.Write(hist.GetName())
# write meta-info
xvarname_st = ROOT.TNamed('xvarname', args['xvarname'])
xvarname_st.Write()
yvarname_st = ROOT.TNamed('yvarname', args['yvarname'])
yvarname_st.Write()
# write normalization
normalization_st = ROOT.TVectorD(1)
normalization_st[0] = args['normalization']
normalization_st.Write("normalization")
# write norm range
if(args['normalization']==3):
    normrange_st = ROOT.TVectorD(2)
    normrange_st[0] = args['normrange'][0]
    normrange_st[1] = args['normrange'][1]
    normrange_st.Write("normrange")
    normvariable_st = ROOT.TNamed('normvariable', args['normvariable'])
    normvariable_st.Write()
# write luminosity
lumi_st = ROOT.TVectorD(1)
lumi_st[0] = args['lumi']
lumi_st.Write("lumi")
# write background mode
bck_mode_st = ROOT.TVectorD(1)
if args["bck_mode"]=='default': bck_mode_st[0] = 1
elif args["bck_mode"]=='sideband': bck_mode_st[0] = 2
else: bck_mode_st[0] = 0
bck_mode_st.Write("bckmode")
# write V0 type
v0type_st = ROOT.TVectorD(1)
if args["treename"]=="laurelin": v0type_st[0] = 1
elif args["treename"]=="telperion": v0type_st[0] = 2
else: v0type_st[0] = 0
v0type_st.Write("v0type")
f.Close()

sys.stderr.write('###done###\n')
