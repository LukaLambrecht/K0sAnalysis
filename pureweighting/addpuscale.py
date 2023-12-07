######################################################################
# Python script to add a pileup reweighting histogram to a root file #
######################################################################
# command line args:
# - root file to work on
# - year (for reading pileup profile histogram)

import sys
from array import array
import ROOT
import os

def addpuscale(infilename,year):
    
    ### some argument checking
    year = str(year)
    if(year not in ['2016','2017','2018']):
        print('### ERROR ###: could not interpret argument: '+year)
        print('               (supposed to represent data taking year)')
        return None        

    ### open the PU hist for data
    gpath = '/storage_mnt/storage/user/llambrec/K0sAnalysis/pureweighting'
    pudata = ROOT.TFile.Open(os.path.join(gpath,'dataPuHist_'+year+'Inclusive_central.root'))
    try:
        puhist = pudata.Get('pileup')
        _ = puhist.GetBinContent(0)
    except:
        print('### ERROR ###: pileup profile in data could not be loaded.')
        print('               Check if file is present in '+gpath)
        return None
    puhist.SetDirectory(ROOT.gROOT)
    puhist.Scale(1./puhist.GetSumOfWeights())
    pudata.Close()

    ### open the nTrueInteractions for MC
    mcfile = ROOT.TFile.Open(infilename,'update')
    try:
        inthist = mcfile.Get('nTrueInteractions')
        _ = inthist.GetBinContent(0)
    except:
        print('### ERROR ###: interactions profile in simulation could not be loaded.')
        print('               Check if the correct histogram is present in the input file.')
        return None
    inthist.SetDirectory(ROOT.gROOT)
    inthist.Scale(1./inthist.GetSumOfWeights())

    ### determine reweighting factors
    scalehist = puhist.Clone()
    scalehist.Divide(inthist)
    scalehist.SetName('PUScale')
    if 'PUScale' in mcfile.GetListOfKeys():
        print('### ERROR ###: a pileup scale is already present in the input file.')
        return None
    else:
        print('writing PUScale to file...')
        scalehist.Write()
    mcfile.Close()

def getpuscale(ntrueint,scalehist):
    return scalehist.GetBinContent(scalehist.GetXaxis().FindBin(ntrueint))

if __name__=='__main__':
    ### some checks on command line arguments
    if len(sys.argv)!=3:
        print('### ERROR ###: too few command line args')
        print('               usage: python addpuweight.py <rootfile> <year>')
        sys.exit()
    addpuscale(sys.argv[1],sys.argv[2])
    
