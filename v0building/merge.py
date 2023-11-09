#########################################
# python script to merge built v0 files #
#########################################

import sys 
import os
import argparse
from fnmatch import fnmatch
sys.path.append('../tools')
import mergetools as mt

# this script will hadd all root files with appendix '_selected.root' in a folder

if __name__=='__main__':

    # command line arguments
    parser = argparse.ArgumentParser( description = 'Merge V0 files' )
    parser.add_argument('-i', '--filedir', required=True, type=os.path.abspath)
    parser.add_argument('-k', '--key', default='*_selected.root')
    parser.add_argument('-o', '--outputfile', default='selected.root')
    parser.add_argument('-f', '--force', default=False, action='store_true')
    parser.add_argument('--remove_input', default=False, action='store_true')
    args = parser.parse_args()

    # find all subdirectories in provided directory
    # that contain at least one root file matching the key
    indirs = {}
    for root,dirs,files in os.walk(args.filedir):
        for thisdir in dirs:
            thisdir = os.path.join(root,thisdir)
            filelist = ([ os.path.join(thisdir,f) for f in os.listdir(thisdir)
                          if fnmatch(f, args.key) ])
            if len(filelist)>=1: indirs[thisdir] = filelist

    for indir in indirs.keys():
        print('now running on {} ({} files)'.format(indir, len(indirs[indir])))
        outfile = os.path.join(indir, args.outputfile)
        if os.path.exists(outfile):
            if args.force: os.system('rm '+outfile)
            else:
                msg = 'WARNING: output file {} already exists,'.format(outfile)
                msg += ' skipping this merge.'
                print(msg)
                continue
        mt.mergefiles(indirs[indir], outfile, removeinput=args.remove_input, runjob=False)
