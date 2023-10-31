####################################################
# script hard-coding the luminosity values per era #
####################################################
# see https://twiki.cern.ch/twiki/bin/viewauth/CMS/BrilcalcQuickStart
# and https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable

# Values are retrieved as follows
# - for 2016 pre-UL: probably brilcalc?
# - for 2017/2018 pre-UL:
#     subpages of https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable
# - for UL per year:
#     https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
#     https://twiki.cern.ch/twiki/bin/view/CMS/PdmVDatasetsUL2016
# - for UL 2016 per era:
#     retrieve run ranges from https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2016Analysis
#     and https://twiki.cern.ch/twiki/bin/view/CMS/PdmVDatasetsUL2016,
#     then use brilcalc


def getlumi( campaign, era ):
    # return lumi of given era
    # note: unit is inverse femtobarn!

    if campaign=='run2preul':
    
      if era=='2016B': return 5.75
      elif era=='2016C': return 2.57
      elif era=='2016D': return 4.24
      elif era=='2016E': return 4.03
      elif era=='2016F': return 3.11
      elif era=='2016G': return 7.58
      elif era=='2016H': return 8.65
      elif era=='2016': return 35.9
      # note: switch to new value for 2016 after improved analysis by Lumi POG (Spring 2021).
      #       however, the values per era are not updated and correspond to the situation
      #       before this update!
      #elif era=='2016': return 36.3

      elif era=='2017B': return 4.82
      elif era=='2017C': return 9.66
      elif era=='2017D': return 4.25
      elif era=='2017E': return 9.28
      elif era=='2017F': return 13.54
      elif era=='2017': return 41.5

      elif era=='2018A': return 14.0
      elif era=='2018B': return 7.1
      elif era=='2018C': return 6.94
      elif era=='2018D': return 31.93
      elif era=='2018': return 59.7

      elif era=='20172018': return 101
      elif era=='run2': return 137
      # note: see 2016
      #elif era=='run2': return 138

    elif campaign=='run2ul':

      if era=='2016PreVFP': return 19.5
      elif era=='2016PreVFPB': return 5.83
      elif era=='2016PreVFPC': return 2.60
      elif era=='2016PreVFPD': return 4.29
      elif era=='2016PreVFPE': return 4.07
      elif era=='2016PreVFPF': return 2.55
      elif era=='2016PostVFP': return 16.8
      elif era=='2016PostVFPF': return 0.58
      elif era=='2016PostVFPG': return 7.65
      elif era=='2016PostVFPH': return 8.74
      elif era=='2017': return 41.5
      elif era=='2018': return 59.8

      elif era=='2016': return 36.3
      elif era=='20172018': return 101
      elif era=='run2': return 138

    msg = 'ERROR: cannot find luminosity for era {} / {}'.format(campaign, era)
    raise Exception(msg)
