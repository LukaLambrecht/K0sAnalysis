#########################################################
# Read a ROOT tree and plot a single variable histogram #
#########################################################

import sys
import os
import ROOT
sys.path.append(os.path.abspath('../tools'))
import optiontools as opt
import singlehistplotter as shp

def fillvarfromtree( tree,
                     varname,
                     xlow = 0.,
                     xhigh = 1.,
                     nbins = 10,
                     weightvar = None, 
                     nprocess = -1,
                     label = None,
		     extraselection = None ):
    # filling histogram from a given tree

    # make output histogram
    hist = ROOT.TH1F('hist','hist', nbins, xlow, xhigh)
    hist.SetDirectory(0)
    hist.Sumw2()

    # set number of events to process
    if( nprocess<0 or nprocess>tree.GetEntries() ): nprocess=tree.GetEntries()
    print('{} out of {} events will be processed'.format(nprocess,tree.GetEntries()))

    # loop over events
    for i in range(nprocess):
        if( i%10000==0 ):
            print('number of processed events: '+str(i))
        tree.GetEntry(i)
	# apply additional selection
	if extraselection is not None:
	    if not eval(extraselection): continue
        # determine weight for this entry
        weight = 1
        if weightvar is not None: weight = getattr(tree,weightvar)
        # determine value for requested variable in this entry
        varvalue = getattr(tree,varname)
        # fill the histogram
        hist.Fill(varvalue,weight)

    # set histogram title
    if label is None: hist.SetTitle(varname)
    else: hist.SetTitle(label)
    return hist

def fillvarfromtreefile( fname, treename, varname, **kwargs ):
    fin = ROOT.TFile.Open(fname)
    tree = fin.Get(treename)
    hist = fillvarfromtree( tree, varname, **kwargs )
    return hist


if __name__=='__main__':

    options = []
    options.append( opt.Option('finloc', vtype='path') )
    options.append( opt.Option('treename') )
    options.append( opt.Option('nprocess', vtype='int', default=-1) )
    options.append( opt.Option('varname', explanation='name of the variable to plot' ) )
    options.append( opt.Option('weightvarname',
                        default=None,
                        explanation='weight of each event,'
                                    +' e.g. _weight in standard ntuples,'
                                    +' use default (None) for equal weighting'
                                    +' (entries instead of events)' ) )
    options.append( opt.Option('xaxtitle', default=None) )
    options.append( opt.Option('yaxtitle', default=None) )
    options.append( opt.Option('title', default=None) )
    options.append( opt.Option('xlow', vtype='float', default=0.) )
    options.append( opt.Option('xhigh', vtype='float', default=100.) )
    options.append( opt.Option('nbins', vtype='int', default=10) )
    options.append( opt.Option('extraselection', default=None) )
    options.append( opt.Option('outfilename', default='figure.png') )
    options = opt.OptionCollection( options )
    if len(sys.argv)==1:
        print('Use with following options:')
        print(options)
        sys.exit()
    else:
        options.parse_options( sys.argv[1:] )
        print('Found following configuration:')
        print(options)
    
    hist = fillvarfromtreefile( options.finloc, options.treename, options.varname, 
				xlow=options.xlow, xhigh=options.xhigh, nbins=options.nbins,
                                weightvar=options.weightvarname, 
				nprocess=options.nprocess,
				extraselection=options.extraselection)
    shp.plotsinglehistogram( hist, options.outfilename,
	xaxtitle=options.xaxtitle, yaxtitle=options.yaxtitle, title=options.title,
        topmargin=0.1 )
