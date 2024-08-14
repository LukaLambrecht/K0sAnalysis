######################
# Pileup reweighting #
######################

import os
import sys
import numpy as np
import ROOT


def get_pileup_profile(campaign, year):
  ### help function to get correct pileup profile file
  path = '/user/llambrec/K0sAnalysis/reweighting/pileup/data'
  if campaign=='run2preul':
    path = os.path.join(path, campaign)
    if year.startswith('2016'): year = '2016'
    if year not in ['2016','2017','2018']:
      msg = 'ERROR: year {} not recogized.'.format(year)
      raise Exception(msg)
    pufile = os.path.join(path,'dataPuHist_{}Inclusive.root'.format(year))
    histname = 'central'
    uphistname = 'up'
    downhistname = 'down'
  elif campaign=='run2ul':
    path = os.path.join(path, campaign)
    if year not in ['2016PreVFP','2016PostVFP','2017','2018']:
      msg = 'ERROR: year {} not recogized.'.format(year)
      raise Exception(msg)
    pufile = os.path.join(path,'Collisions{}_UltraLegacy_goldenJSON.root'.format(year))
    histname = 'nominal'
    uphistname = 'up'
    downhistname = 'down'
  else:
    msg = 'ERROR: campaign {} not recognized.'.format(campaign)
    raise Exception(msg)
  if not os.path.exists(pufile):
    msg = 'ERROR: pileup file {} does not seem to exist.'.format(pufile)
    raise Exception(msg)
  return (pufile, histname, uphistname, downhistname)


class PileupReweighter(object):
    
  def __init__(self, campaign, year,
    pufile=None, histname=None,
    uphistname=None, downhistname=None):
    ### initialize a pileup reweighter
    self.campaign = campaign
    self.year = year
    # get correct file and histogram names
    if( pufile is None or histname is None ):
      (self.pufile, self.histname, self.uphistname, self.downhistname) = get_pileup_profile(campaign, year)
    else:
      self.pufile = pufile
      self.histname = histname
      self.uphistname = uphistname
      self.downhistname = downhistname
    # open the file and get the histogram
    f = ROOT.TFile.Open(self.pufile)
    try:
      self.puhist = f.Get(self.histname)
      _ = self.puhist.GetBinContent(0)
      self.uppuhist = None
      self.downpuhist = None
      if self.uphistname is not None: self.uppuhist = f.Get(self.uphistname)
      if self.downhistname is not None: self.downpuhist = f.Get(self.downhistname)
    except:
      msg = 'ERROR: pileup profile in data could not be loaded.'
      raise Exception(msg)
    self.puhist.SetDirectory(ROOT.gROOT)
    self.uppuhist.SetDirectory(ROOT.gROOT)
    self.downpuhist.SetDirectory(ROOT.gROOT)
    f.Close()
    # printouts
    print('Initialized pileup reweighter with following properties:')
    print('  - campaign: {}'.format(campaign))
    print('  - year: {}'.format(year))
    print('  - nominal: {}'.format(self.puhist))
    print('  - up: {}'.format(self.uppuhist))
    print('  - down: {}'.format(self.downpuhist))
    # initialize scale histogram
    # note: for pre-UL analyses, the scale histogram should be calculated
    #       for each sample separately, given the pileup distribution in data
    #       and the one for the specific sample;
    #       while for UL analyses, the pileup histogram loaded above
    #       gives directly the required ratio.
    self.scalehist = None
    self.upscalehist = None
    self.downscalehist = None
    if self.campaign=='run2ul':
      self.scalehist = self.puhist.Clone()
      if self.uppuhist is not None: self.upscalehist = self.uppuhist.Clone()
      if self.downpuhist is not None: self.downscalehist = self.downpuhist.Clone()

  def initsample(self, sample):
    ### initialize the reweighter for a given sample

    # skip in case of UL sample, no initialization needed
    if self.campaign=='run2ul': return

    # get true interaction profile from sample
    f = ROOT.TFile.Open(sample)
    try:
      inthist = f.Get('nTrueInteractions')
      _ = inthist.GetBinContent(0)
    except:
        msg = 'ERROR: interactions profile in simulation could not be loaded.'
        raise Exception(msg)
    inthist.SetDirectory(ROOT.gROOT)
    f.Close()

    # initialize the rescaling histograms with this true interaction profile
    self.initntrueint(inthist)

  def initntrueint(self, ntrueint):

    # scale true interaction profile to a density
    ntrueint.Scale(1./ntrueint.GetSumOfWeights())

    # determine reweighting factors
    self.scalehist = self.puhist.Clone()
    self.scalehist.Scale(1./self.puhist.GetSumOfWeights())
    self.scalehist.Divide(ntrueint)
    if self.uppuhist is not None:
      self.upscalehist = self.uppuhist.Clone()
      self.upscalehist.Scale(1./self.uppuhist.GetSumOfWeights())
      self.upscalehist.Divide(ntrueint)
    if self.downpuhist is not None:
      self.downscalehist = self.downpuhist.Clone()
      self.downscalehist.Scale(1./self.downpuhist.GetSumOfWeights())
      self.downscalehist.Divide(ntrueint)

  def getreweight(self, ntrueint, wtype='nominal'):
    ### get the pileup reweighting factor for a given number of true interactions
    hist = self.scalehist
    if wtype=='up': hist = self.upscalehist
    elif wtype=='down': hist = self.downscalehist
    elif wtype=='nominal': pass
    else:
      msg = 'ERROR: wtype {} not recognized.'.format(wtype)
      raise Exception(msg)
    if hist is None:
      msg = 'ERROR: pileup reweighting histogram was not found.'
      raise Exception(msg)
    isscalar = False
    if( isinstance(ntrueint, int) or isinstance(ntrueint, float) ):
      isscalar = True
      ntrueint = np.array([ntrueint])
    res = np.zeros(len(ntrueint))
    for i in range(len(ntrueint)):
      res[i] = hist.GetBinContent(hist.GetXaxis().FindBin(ntrueint[i]))
    if isscalar: res = res[0]
    return res

  def weight(self, ntrueint):
    if self.scalehist is None:
      msg = 'ERROR: pileup reweighter was not yet initialized with a sample.'
      raise Exception(msg)
    return self.getreweight(ntrueint, wtype='nominal')

  def upweight(self, ntrueint):
    if self.upscalehist is None:
      msg = 'ERROR: pileup reweighter has no up-variation.'
      raise Exception(msg)
    return self.getreweight(ntrueint, wtype='up')

  def downweight(self, ntrueint):
    if self.downscalehist is None:
      msg = 'ERROR: pileup reweighter has no down-variation.'
      raise Exception(msg)
    return self.getreweight(ntrueint, wtype='down')
