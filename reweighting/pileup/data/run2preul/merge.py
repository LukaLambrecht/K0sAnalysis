import ROOT

if __name__=='__main__':

    years = ['2016', '2017', '2018']
    suffixes = ['central', 'up', 'down']
    for year in years:
        histograms = []
        for suffix in suffixes:
            rootfile = 'dataPuHist_{}Inclusive_{}.root'.format(year, suffix)
            f = ROOT.TFile.Open(rootfile)
            hist = f.Get('pileup')
            hist.SetDirectory(0)
            f.Close()
            hist.SetName(suffix)
            hist.SetTitle(suffix)
            histograms.append(hist)
        outputfile = 'dataPuHist_{}Inclusive.root'.format(year)
        f = ROOT.TFile.Open(outputfile, 'recreate')
        for hist in histograms: hist.Write()
        f.Close()
