#########################
# Merge eras into years #
#########################
# WARNING: lots of hard-coding, might need to adapt if running of different eras 
# or with different naming conventions.

import sys
import os
import argparse


if __name__=='__main__':

    yeardict = ({
      'DoubleMuon_Run2016PreVFP': [
        'DoubleMuon_crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v1',
        'DoubleMuon_crab_Run2016C-HIPM_UL2016_MiniAODv2-v1',
        'DoubleMuon_crab_Run2016D-HIPM_UL2016_MiniAODv2-v1',
        'DoubleMuon_crab_Run2016E-HIPM_UL2016_MiniAODv2-v1',
        'DoubleMuon_crab_Run2016F-HIPM_UL2016_MiniAODv2-v1'
      ],
      'DoubleMuon_Run2016PostVFP': [
        'DoubleMuon_crab_Run2016F-UL2016_MiniAODv2-v1',
        'DoubleMuon_crab_Run2016G-UL2016_MiniAODv2-v1',
        'DoubleMuon_crab_Run2016H-UL2016_MiniAODv2-v2'
      ],
      'DoubleMuon_Run2017': [
        'DoubleMuon_crab_Run2017B-UL2017_MiniAODv2-v1',
        'DoubleMuon_crab_Run2017C-UL2017_MiniAODv2-v1',
        'DoubleMuon_crab_Run2017D-UL2017_MiniAODv2-v1',
        'DoubleMuon_crab_Run2017E-UL2017_MiniAODv2-v2',
        'DoubleMuon_crab_Run2017F-UL2017_MiniAODv2-v1'
      ],
      'DoubleMuon_Run2018': [
        'DoubleMuon_crab_Run2018A-UL2018_MiniAODv2-v1_data_doublemuon',
        'DoubleMuon_crab_Run2018B-UL2018_MiniAODv2-v1_data_doublemuon',
        'DoubleMuon_crab_Run2018C-UL2018_MiniAODv2-v1_data_doublemuon',
        'DoubleMuon_crab_Run2018D-UL2018_MiniAODv2-v1_data_doublemuon'
      ]
    })

    # command line arguments
    parser = argparse.ArgumentParser( description = 'Merge V0 files' )
    parser.add_argument('-i', '--filedir', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default='merged.root')
    parser.add_argument('-f', '--force', default=False, action='store_true')
    args = parser.parse_args()

    for yeardir, eradirs in yeardict.items():
        yeardir = os.path.join(args.filedir, yeardir)
        # make output directory
        if not os.path.exists(yeardir): os.makedirs(yeardir)
        # make hadd command
        cmd = 'hadd'
        if args.force: cmd += ' -f'
        cmd += ' {}'.format(os.path.join(yeardir, args.outputfile))
        for eradir in eradirs:
            cmd += ' {}*/*.root'.format(os.path.join(args.filedir, eradir))
        # run hadd command
        os.system(cmd)
