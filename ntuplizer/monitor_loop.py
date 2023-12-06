#!/usr/bin/env python3

#########################################################################################
# extension to monitor.py which allows continuous automatic monitoring and resubmission #
#########################################################################################

# how to use:
# - make sure to have done cmsenv, created a proxy, etc.
#   (it might be good to check that the crab status command is working as expected 
#    by running it on a single sample).
# - change the settings below to your liking.
# - run with "nohup python3 monitor_auto.py &> [name of a log file] &".
#   some explanation:
#   - "python3 monitor_auto.py" trivially runs this script.
#   - "&> [name of a log file]" redirects both stdout and stderr to the log file you chose.
#   - "nohup [...] &" runs the command in the background, 
#     and keeps it running even after you close the terminal.
# - alternatively, you could open a screen session and simply run 
#   "python3 monitor_auto.py &> [name of a log file]".
#   this gives you more control over terminating the command,
#   since with "nohup &", the process ID seems to be irretrievable 
#   after logging out of the m-machine (?).
# notes:
# - you will need a valid proxy for the entire duration of this script,
#   so create one with a long enough lifetime. 


import sys
import os
import time
import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser(description='Monitor CRAB jobs')
    parser.add_argument('-c', '--crabdir', required=True, type=os.path.abspath,
                        help='CRAB log directory')
    parser.add_argument('-n', '--niterations', default=1, type=int,
                        help='Number of iterations to do')
    parser.add_argument('-t', '--tsleep', default=3600, type=int,
                        help='Time between iterations, in seconds')
    parser.add_argument('-r', '--resubmit', default=False, action='store_true',
                        help='Do resubmit (default: only monitoring)')
    parser.add_argument('-w', '--webpage', default='crab_status_auto',
                        help='Name of the webpage to put the results')
    args = parser.parse_args()

    # print arguments
    print('Running with following configuration:')
    for arg in vars(args):
        print('  - {}: {}'.format(arg,getattr(args,arg)))

    # make a check on total runtime
    trun = args.tsleep * args.niterations
    print('Estimated runtime:')
    print('  {} seconds'.format(trun))
    print('  {:.2f} hours'.format(trun/3600.))
    print('  {:.2f} days'.format(trun/(3600.*24.)))
    print('Continue? (y/n)')
    go = input()
    if go != 'y': sys.exit()
    
    # make the command
    cmd = 'python3 monitor.py'
    cmd += ' --crabdir {}'.format(args.crabdir)
    if args.resubmit: cmd += ' --resubmit'
    cmd += ' --webpage {}'.format(args.webpage)

    # loop over number of iterations minus 1
    idx = 0
    while idx < args.niterations-1:
        os.system(cmd)
        sys.stdout.flush()
        sys.stderr.flush()
        time.sleep(args.tsleep)
        idx += 1
    # run last iteration 
    # (without waiting time after finishing)
    os.system(cmd)
