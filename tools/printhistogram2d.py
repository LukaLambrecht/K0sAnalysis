####################################################
# print the bin contents and errors of a histogram #
####################################################

import sys
import ROOT
import histtools

filename = sys.argv[1]
histname = sys.argv[2]

f = ROOT.TFile.Open(filename,'read')
hist = f.Get(histname)
hist.SetDirectory(0)
f.Close()

histtools.printhistogram2d(hist,rangeinfo=True)
