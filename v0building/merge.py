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

    # printouts for testing
    print('Found following directories for merging:')
    for indir in sorted(indirs.keys()):
        print('  - {} ({} files)'.format(indir, len(indirs[indir])))

    # loop over input directories
    for indir in sorted(indirs.keys()):
        print('Now running on {} ({} files)'.format(indir, len(indirs[indir])))
        outfile = os.path.join(indir, args.outputfile)
        if os.path.exists(outfile):
            msg = 'WARNIING: output file {} already exists;'.format(outfile)
            if args.force:
                msg += ' removing and recreating it (since --force was set to True)'
                print(msg)
                os.system('rm '+outfile)
            else:
                msg += ' skipping this merge (since --force was set to False)'
                print(msg)
                continue
        # handle case of only one input file
        inputfiles = indirs[indir]
        if len(inputfiles)==1:
            cmd = 'mv {} {}'.format(inputfiles[0], outfile)
            print('Found only one input file in this directory, renaming to output file.')
            print(cmd)
            os.system(cmd)
            continue
        # now general case of multiple files
        mt.mergefiles(inputfiles, outfile, removeinput=args.remove_input, runjob=False)
