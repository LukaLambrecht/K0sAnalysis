####################################################
# script hard-coding the luminosity values per era #
####################################################
# see https://twiki.cern.ch/twiki/bin/viewauth/CMS/BrilcalcQuickStart
# and https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable

# Values are retrieved as follows
# - for 2017/2018 pre-UL:
#     subpages of https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable
# - for 2016 pre-UL: use brilcalc, see details below.
# - for UL per year:
#     https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
#     https://twiki.cern.ch/twiki/bin/view/CMS/PdmVDatasetsUL2016
# - for UL 2016 per era: use brilcalc, see details below.


def getlumi( campaign, era ):
    # return lumi of given era
    # note: unit is inverse femtobarn!

    if campaign=='run2preul':

      # 2016:
      # run brilcalc as follows:
      # brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json -u /fb -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt
      # as recommended by this twiki page:
      # https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
      # and add run ranges specified on this twiki page:
      # https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2016Analysis
      if era=='2016B': return 5.83
      elif era=='2016C': return 2.60
      elif era=='2016D': return 4.29
      elif era=='2016E': return 4.07
      elif era=='2016F': return 3.14
      elif era=='2016G': return 7.65
      elif era=='2016H': return 8.74
      elif era=='2016BtoF': return 19.9 # corresponds to sum of B to F -> ok.
      elif era=='2016GtoH': return 16.4 # corresponds to sum of G to H -> ok.
      elif era=='2016': return 36.3 # corresponds to sum of per-era and to recommendations -> ok.

      # 2017: see twiki pages mentioned above.
      elif era=='2017B': return 4.82
      elif era=='2017C': return 9.66
      elif era=='2017D': return 4.25
      elif era=='2017E': return 9.28
      elif era=='2017F': return 13.54
      elif era=='2017': return 41.5 # corresponds to sum of per-era -> ok.

      # 2018: see twiki pages mentioned above.
      elif era=='2018A': return 13.98
      elif era=='2018B': return 7.06
      elif era=='2018C': return 6.90
      elif era=='2018D': return 31.75
      elif era=='2018': return 59.7 # corresponds to sum of per-era -> ok.

      elif era=='20172018': return 101
      elif era=='run2': return 138

    elif campaign=='run2ul':

      # 2016:
      # run brilcalc as follows:
      # brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json -u /fb -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt
      # as recommended by this twiki page:
      # https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
      # and add run ranges specified on this twiki page:
      # https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2016Analysis
      # and here: https://twiki.cern.ch/twiki/bin/view/CMS/PdmVDatasetsUL2016
      if era=='2016PreVFP': return 19.5
      # note: brilcalc actually gives 19.34, but keep recommendation of 19.5
      elif era=='2016PreVFPB': return 5.83
      elif era=='2016PreVFPC': return 2.60
      elif era=='2016PreVFPD': return 4.29
      elif era=='2016PreVFPE': return 4.07
      elif era=='2016PreVFPF': return 2.55
      elif era=='2016PostVFP': return 16.8
      # note: brilcalc actually gives 16.98, but keep recommendation of 16.8
      elif era=='2016PostVFPF': return 0.58
      elif era=='2016PostVFPG': return 7.65
      elif era=='2016PostVFPH': return 8.74
      elif era=='2016': return 36.3 # corresponds to sum of per-era -> ok.

      # 2017 and 2018: see twiki pages mentioned above.
      elif era=='2017': return 41.5 # same as pre-UL (difference is only in second digit).
      elif era=='2018': return 59.8 # slightly higher than pre-UL, according to recommendations.

      elif era=='20172018': return 101
      elif era=='run2': return 138

    msg = 'ERROR: cannot find luminosity for era {} / {}'.format(campaign, era)
    raise Exception(msg)
