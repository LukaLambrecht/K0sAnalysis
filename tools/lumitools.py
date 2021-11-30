####################################################
# script hard-coding the luminosity values per era #
####################################################
# see https://twiki.cern.ch/twiki/bin/viewauth/CMS/BrilcalcQuickStart

def getlumi( era ):
    # return lumi of given era
    # note: unit is inverse femtobarn!

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

    else: print('### WARNING ###: cannot find luminosity for era '+era)
    return 0.
