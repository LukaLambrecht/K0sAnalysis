##################################################
# Merge recovery tasks into original directories #
##################################################

import os
import sys
import argparse
from six.moves import input


if __name__=='__main__':

    # command line arguments
    parser = argparse.ArgumentParser( description = 'Merge V0 files' )
    parser.add_argument('-i', '--filedir', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default='merged.root')
    parser.add_argument('-f', '--force', default=False, action='store_true')
    parser.add_argument('--recoverytag', default=None)
    parser.add_argument('--remove_input', default=False, action='store_true')
    args = parser.parse_args()

    if args.recoverytag is not None:
        mergedict = {}
        for recoverydir in sorted(os.listdir(args.filedir)):
            if not recoverydir.endswith(args.recoverytag): continue
            recoverydir = os.path.join(args.filedir, recoverydir)
            origdir = recoverydir.replace(args.recoverytag, '').strip('-_')
            if not os.path.exists(origdir):
                msg = 'WARNING: no original directory found'
                msg += ' for recovery directory {};'.format(recoverydir)
                msg += ' skipping this directory.'
                print(msg)
                continue
            mergedict[origdir] = [origdir, recoverydir]
        print('Found following directories to merge:')
        for key, val in mergedict.items():
            print('  {}'.format(key))
            for el in val: print('    {}'.format(el))
        print('Continue? (y/n)')
        go = input()
        if go!='y': sys.exit()
        for origdir, val in mergedict.items():
            outputfile = os.path.join(origdir, args.outputfile)
            cmd = 'hadd'
            if args.force: cmd += ' -f'
            cmd += ' {}'.format(outputfile)
            for el in val: cmd += ' {}/*.root'.format(el)
            print(cmd)
            os.system(cmd)
            if args.remove_input:
                for el in val:
                    if el==origdir: continue
                    cmd = 'rm -r {}'.format(el)
                    print(cmd)
                    os.system(cmd)
                for f in os.listdir(origdir):
                    f = os.path.join(origdir, f)
                    if f==outputfile: continue
                    cmd = 'rm {}'.format(f)
                    print(cmd)
                    os.system(cmd)
