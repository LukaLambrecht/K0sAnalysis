###########################################################
# script to hadd output files of fitinvmass_fancy_fill.py #
###########################################################
# can be used to make invariant mass plots for full run 2.

import sys
import os
import ROOT
sys.path.append(os.path.abspath('../tools'))
import histtools as ht

if __name__=='__main__':

    ### command line arguments: same as for hadd
    # (name of output file, names of input files)
    fout = sys.argv[1]
    finlist = sys.argv[2:]

    # load all non-histogram objects from first input file
    histlist = ht.loadallhistograms( finlist[0] ) # also need histograms for length of divbins
    fin = ROOT.TFile.Open( finlist[0] )
    divbins = fin.Get("divbins_w")
    divbins = [divbins[j] for j in range(len(histlist)+1)]
    divvarname = str(fin.Get("divvarname_w").GetTitle())
    divvarlabel = str(fin.Get("divvarlabel_w").GetTitle())
    lumi = float(fin.Get("lumi_w")[0])
    nfilled = float(fin.Get("nfilled_w")[0])
    fin.Close()
    # check if objects in other input files match, or add if needed
    for finname in finlist[1:]:
	checkhistlist = ht.loadallhistograms( finname )
	fin = ROOT.TFile.Open( finname )
	checkdivbins = fin.Get("divbins_w")
	checkdivbins = [checkdivbins[j] for j in range(len(checkhistlist)+1)]
	if checkdivbins != divbins:
	    raise Exception('ERROR: divbins in data and simulation file do not agree;'
			    +' found {} and {}'.format(divbins,checkdivbins))
	if str(fin.Get("divvarname_w").GetTitle())!= divvarname:
	    raise Exception('ERROR: divvarname in data and simulation file do not agree;'
			    +' found {} and {}'.format(divvarname,
			    str(fin.Get("divvarname_w").GetTitle())))
	lumi += float(fin.Get("lumi_w")[0])
	nfilled += float(fin.Get("nfilled_w")[0])
	fin.Close()
	#print(lumi)
	#print(nfilled)

    # do hadd to correctly merge the histograms, then get the histogram list
    cmd = 'hadd -f {}'.format(fout)
    for fin in finlist: cmd += ' {}'.format(fin)
    os.system(cmd)
    histlist = ht.loadallhistograms( fout )

    # recreate the output file and write histograms and other objects
    f = ROOT.TFile.Open( fout, 'recreate' )
    for hist in histlist: hist.Write()
    # write secondary variable bins
    divbins_w = ROOT.TVectorD(len(divbins))
    for j in range(len(divbins)):
        divbins_w[j] = divbins[j]
    divbins_w.Write("divbins_w")
    # write secondary variable name and label
    divvarname_w = ROOT.TNamed("divvarname_w",divvarname)
    divvarname_w.Write()
    divvarlabel_w = ROOT.TNamed("divvarlabel_w",divvarlabel)
    divvarlabel_w.Write()
    # write luminosity and number of processed events
    nfilled_w = ROOT.TVectorD(1); nfilled_w[0] = nfilled
    nfilled_w.Write("nfilled_w")
    lumi_w = ROOT.TVectorD(1); lumi_w[0] = lumi
    lumi_w.Write("lumi_w")
    f.Close() 
