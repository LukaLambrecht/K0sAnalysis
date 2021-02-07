###########################################################################################
# Python script to read a noskim.root tree, extract the a Kshort vertex value and plot it #
###########################################################################################
import ROOT
from plotvarfromtuple import plotsinglehistogram

def fillvarfromtree(tree,varname,xlow,xhigh,nbins,weightvar='',nprocess=-1,label='',
		    extraselection=''):
    # filling histogram from a given tree

    # make output histogram
    hist = ROOT.TH1F('hist','',nbins,xlow,xhigh)

    # set number of events to process
    if( nprocess<0 or nprocess>tree.GetEntries() ): nprocess=tree.GetEntries()
    print('{} out of {} events will be processed'.format(nprocess,tree.GetEntries()))

    # loop over events
    for i in range(nprocess):
        if( i%10000==0 ):
            print('number of processed events: '+str(i))
        tree.GetEntry(i)
	# apply additional selection
	if len(extraselection)>0:
	    if not eval(extraselection): continue
        # determine weight for this entry
        weight = 1
        if weightvar!='': weight = getattr(tree,weightvar)
        # determine value for requested variable in this entry
        varvalue = getattr(tree,varname)
        # fill the histogram
        hist.Fill(varvalue,weight)

    # set histogram title
    if label=='': hist.SetTitle(varname)
    else: hist.SetTitle(label)
    return hist

if __name__=='__main__':

    # initialization
    finloc = '/user/llambrec/Kshort/files/skim_ztomumu/selected_legacy/DoubleMuon_Run2016/selected.root'
    fin = ROOT.TFile.Open(finloc)
    tree = fin.Get("laurelin")
    nprocess = -1
    xaxtitle = r'deltaR'
    yaxtitle = r'number of vertices'
    varname = '_trackdR'
    title = r'deltaR between tracks'
    extraselection = '(getattr(tree,"_ptPos")>5 and getattr(tree,"_ptNeg")>5)'
   
    hist = fillvarfromtree(tree,varname,0.,0.55,50,weightvar='',nprocess=nprocess,
			    extraselection=extraselection)
    plotsinglehistogram(hist,'figure_pt5.png',xaxtitle=xaxtitle,yaxtitle=yaxtitle,title=title) 
