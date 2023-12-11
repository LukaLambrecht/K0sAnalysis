#######################
# Rename merged files #
#######################

import os
import sys
import argparse


if __name__=='__main__':

    # command line arguments
    parser = argparse.ArgumentParser( description = 'Rename merged files' )
    parser.add_argument('-i', '--filedir', required=True, type=os.path.abspath)
    parser.add_argument('-f', '--fromname', required=True)
    parser.add_argument('-t', '--toname', required=True)
    args = parser.parse_args()

    for sampledir in sorted(os.listdir(args.filedir)):
        sampledir = os.path.join(args.filedir, sampledir)
        fromname = os.path.join(sampledir, args.fromname)
        toname = os.path.join(sampledir, args.toname)
        if not os.path.exists(fromname): continue
        cmd = 'mv {} {}'.format(fromname, toname)
        print(cmd)
        os.system(cmd)
