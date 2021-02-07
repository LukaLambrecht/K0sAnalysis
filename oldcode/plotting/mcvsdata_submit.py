###########################################
# Submit mcvsdata fillrd and plot methods #
###########################################
import json
import os
import pipes

filllist = []
plotlist = []

### global settings
histdir = '/storage_mnt/storage/user/llambrec/Kshort/histograms2D'
fillscript = 'mcvsdata_fillrdpt.py' # choose from mcvsdata_fillrd.py or mcvsdata_fillrdpt.py
plotscript = 'mcvsdata_plot2d.py'
scriptloc = os.path.abspath(os.getcwd()) # location where the scripts are
includelist = (['2016B','2016C','2016D','2016E','2016F','2016G','2016H','2016',
		'2017B','2017C','2017D','2017E','2017F','2017',
		'2018A','2018B','2018C','2018D','2018'
		])

### fill eralist with files to run on and related properties
eralist = []
for era in includelist:
    if '2016' in era: 
	mcdir = 'RunIISummer16_DYJetsToLL'
    elif '2017' in era:
	mcdir = 'RunIIFall17_DYJetsToLL'
    elif '2018' in era:
	mcdir = 'RunIIAutumn18_DYJetsToLL'
    datadir = 'Run'+era+'_DoubleMuon'
    mcin = ([{	'file':'/storage_mnt/storage/user/llambrec/Kshort/files/'+mcdir+'/skim_ztomumu_all.root',
		'label':'simulation','xsection':1.,'luminosity':1.}])
    datain = ([{'file':'/storage_mnt/storage/user/llambrec/Kshort/files/'+datadir+'/skim_ztomumu_all.root',
		'label':era+' data'}])
    label = era
    eralist.append({'mcin':mcin,'datain':datain,'label':label})

### specific settings
counter = 0
xaxistitle = 'radial distance (cm)'
yaxistitle = 'transverse momentum (GeV)'
# for Ks
ksextracutwmass = 'bool(getattr(tree,"_passMassCut"))'
ksextracut = 'bool(2>1)' # defautl if no extra cut required
# x-axis
ksvarname = '_KsRPV'
ksnormrange = [0,0.5]
ksnormrange2 = [0.5,1.5]
ksbins = [0.,0.5,1.5,4.,20.]
# y-axis
ksvarname_y = '_KsPt'
ksnormrange_y = [0.,20.]
ksbins_y = [0.,4.,6.,20.]
# title
kstitle = 'K^{0}_{S} vertex radial distance'
# for La:
laextracutwmass = 'bool(getattr(tree,"_passMassCut"))'
laextracut = 'bool(2>1)'
# x-axis
lanormrange = [0.,0.5]
lanormrange2 = [0.5,1.5]
labins = [0.,0.5,1.5,4.,20.]
latitle = '#Lambda^{0} vertex radial distance'

for era in eralist:
	thishistdir = histdir+'/'+era['label']+'/'
	thismcin = era['mcin']
	thisdatain = era['datain']

	'''# plot: Kshort, normalization=4, variable bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_KsRPV','treename=laurelin',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+ksextracutwmass,
		'bintype=variable','bins='+json.dumps(ksbins,separators=(",",":")),
		'normalization=4','eventtree=nimloth'])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Kshort, normalization=4, fixed bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_KsRPV','treename=laurelin',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+ksextracutwmass,
		'bintype=fixed','xlow=0.','xhigh=20.','nbins=50',
		'normalization=4','eventtree=nimloth'])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Kshort, normalization=3, variable bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_KsRPV','treename=laurelin',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+ksextracutwmass,
		'bintype=variable','bins='+json.dumps(ksbins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(ksnormrange,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Kshort, normalization=3, different range
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
                'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
                'varname=_KsRPV','treename=laurelin',
                'mcin='+json.dumps(thismcin,separators=(",",":")),
                'datain='+json.dumps(thisdatain,separators=(",",":")),
                'bck_mode=1','extracut='+ksextracutwmass,
                'bintype=variable','bins='+json.dumps(ksbins,separators=(",",":")),
                'normalization=3','normrange='+json.dumps(ksnormrange2,separators=(",",":"))])
        plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
                'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
                'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
        counter += 1
	
	# plot: Kshort, linear background, variable bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_KsRPV','treename=laurelin',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=2','extracut='+ksextracut,'massvar=_KsInvMass',
		'mxlow=0.44','mxhigh=0.56','mnbins=30',
		'bintype=variable','bins='+json.dumps(ksbins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(ksnormrange,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Kshort, linear background, different normalization range
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_KsRPV','treename=laurelin',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=2','extracut='+ksextracut,'massvar=_KsInvMass',
		'mxlow=0.44','mxhigh=0.56','mnbins=30',
		'bintype=variable','bins='+json.dumps(ksbins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(ksnormrange2,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Lambda, normalization=4, variable bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_LaRPV','treename=telperion',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+laextracutwmass,
		'bintype=variable','bins='+json.dumps(labins,separators=(",",":")),
		'normalization=4','eventtree=nimloth'])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+latitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Lambda, normalization=4, fixed bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_LaRPV','treename=telperion',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+laextracutwmass,
		'bintype=fixed','xlow=0.','xhigh=20.','nbins=50',
		'normalization=4','eventtree=nimloth'])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+latitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Lambda, normalization=3, variable bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_LaRPV','treename=telperion',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+laextracutwmass,
		'bintype=variable','bins='+json.dumps(labins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(lanormrange,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+latitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Lambda, normalization=3, different range
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_LaRPV','treename=telperion',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=1','extracut='+laextracutwmass,
		'bintype=variable','bins='+json.dumps(labins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(lanormrange2,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+latitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Lambda, linear background, variable bins
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_LaRPV','treename=telperion',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=2','extracut='+laextracut,
		'massvar=_LaInvMass','mxlow=1.085','mxhigh=1.145','mnbins=30',
		'bintype=variable','bins='+json.dumps(labins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(lanormrange,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+latitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot: Lambda, linear background, different normalization range
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'helpdir='+thishistdir+'histn'+str(counter)+'/help/',
		'varname=_LaRPV','treename=telperion',
		'mcin='+json.dumps(thismcin,separators=(",",":")),
		'datain='+json.dumps(thisdatain,separators=(",",":")),
		'bck_mode=2','extracut='+laextracut,
		'massvar=_LaInvMass','mxlow=1.085','mxhigh=1.145','mnbins=30',
		'bintype=variable','bins='+json.dumps(labins,separators=(",",":")),
		'normalization=3','normrange='+json.dumps(lanormrange2,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
		'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
		'histtitle='+latitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter +=  1'''

	# plot2D: Ks, normalization=3, background subtraction
	filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
                'helpdir='+thishistdir+'histn'+str(counter)+'/help/','treename=laurelin',
                'mcin='+json.dumps(thismcin,separators=(",",":")),
                'datain='+json.dumps(thisdatain,separators=(",",":")),
                'bck_mode=2','extracut='+ksextracut,
                'massvar=_KsInvMass','mxlow=0.44','mxhigh=0.56','mnbins=30',
                'xvarname='+ksvarname,'xbins='+json.dumps(ksbins,separators=(",",":")),
                'normalization=3',
		'xnormrange='+json.dumps(ksnormrange2,separators=(",",":")),
		'ynormrange='+json.dumps(ksnormrange_y,separators=(",",":")),
		'yvarname='+ksvarname_y,'ybins='+json.dumps(ksbins_y,separators=(",",":"))])
	plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
                'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
                'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
	counter += 1

	# plot2D: Ks, normalization=3, small range, background subtraction
        filllist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
                'helpdir='+thishistdir+'histn'+str(counter)+'/help/','treename=laurelin',
                'mcin='+json.dumps(thismcin,separators=(",",":")),
                'datain='+json.dumps(thisdatain,separators=(",",":")),
                'bck_mode=2','extracut='+ksextracut,
                'massvar=_KsInvMass','mxlow=0.44','mxhigh=0.56','mnbins=30',
                'xvarname='+ksvarname,'xbins='+json.dumps(ksbins,separators=(",",":")),
                'normalization=3',
                'xnormrange='+json.dumps(ksnormrange,separators=(",",":")),
                'ynormrange='+json.dumps(ksnormrange_y,separators=(",",":")),
                'yvarname='+ksvarname_y,'ybins='+json.dumps(ksbins_y,separators=(",",":"))])
        plotlist.append(['histfile='+thishistdir+'histn'+str(counter)+'/test.root',
                'outfile='+thishistdir+'histn'+str(counter)+'/figure.png',
                'histtitle='+kstitle,'xaxistitle='+xaxistitle,'yaxistitle='+yaxistitle])
        counter += 1

	### Run using local submission
	if not os.path.exists(thishistdir):
		os.makedirs(thishistdir)
	for i in range(len(filllist)):
		diri = thishistdir+'histn'+str(i)
		if os.path.exists(diri):
			os.system("rm -r "+diri)
		os.mkdir(diri)
		os.chdir(diri)
		with open("plot_submit_local.sh", "w") as localsh:
		    	localsh.write('#source $VO_CMS_SW_DIR/cmsset_default.sh\n')
			localsh.write('cd /user/llambrec/CMSSW_10_2_16_patch1/src\n')
			localsh.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
			localsh.write('eval `scram runtime -sh`\n')
			localsh.write('cd '+scriptloc+'\n')
			# core command for filling:
			localsh.write('python '+fillscript)
			# extra options:
			for opt in filllist[i]:
				localsh.write(" "+"'"+opt+"'")
			localsh.write('\n')
			# core command for plot.py
			localsh.write('python '+plotscript)
			# extra options
			for opt in plotlist[i]:
				localsh.write(" "+"'"+opt+"'")
			localsh.write('\n')
		os.system("qsub plot_submit_local.sh")
		print('job nr '+str(i+1)+' of '+str(len(filllist))+' submitted')
	filllist = []
	plotlist = []
	counter = 0
	
	### For testing: run sequentially on m-machine
	'''for i in range(len(filllist)):
		diri = thishistdir+'histn'+str(i)
        	if os.path.exists(diri):
	                os.system("rm -r "+diri)
	        os.mkdir(diri)
		cmd = "python "+plotscript
		for opt in filllist[i]:
			cmd = cmd + " "+"'"+opt+"'"
		cmd2 = ""
		if plotscript=='mcvsdata_fillrd.py':
			cmd2 = "python mcvsdata_plot.py"
		elif plotscript=='mcvsdata_fillrdpt.py':
			cmd2 = "python mcvsdata_plot2d.py"
		for opt in plotlist[i]:
	        	cmd2 = cmd2 + " "+"'"+opt+"'"
	        os.system(cmd)
		os.system(cmd2)
	filllist = []
	plotlist = []
	counter = 0'''
