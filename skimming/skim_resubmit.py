################################
# resubmit stuck skimming jobs #
################################

import os
import sys
from six.moves import input
sys.path.append('../tools')
import jobcheck as jc
 
if __name__=='__main__':

    # find the relevant error log files
    allefiles = []
    allefiles += [fname for fname in os.listdir(os.getcwd()) 
                    if ('cjob_skim' in fname and '_err_' in fname)]
    print('found {} error log files.'.format(len(allefiles)))
    print('start scanning...')

    # loop over all error log files found above
    # and find those corresponding to unfinished jobs
    efiles = []
    for efile in allefiles:
        # error checking
        if( jc.check_start_done(efile) or jc.check_error_content(efile) ): efiles.append(efile)
    print('found {} error log files corresponding to unfinished jobs.'.format(len(efiles)))

    # sort the list of error log files
    efiles = sorted(efiles)
    
    # get corresponding job ids
    jobids = []
    for efile in efiles:
        jobid = efile.split('_')[3]
        jobids.append(jobid)

    # check corresponding output log files and find corresponding executable
    shfiles = []
    for efile in efiles:
        ofile = efile.replace('_err_', '_out_')
        with open(ofile,'r') as f:
           firstline = f.readline()
        shfile = firstline.replace('###exename###: ', '').strip(' \n')
        shfiles.append(shfile)

    # temporary fix to force hadd to overwrite the merged file
    for shfile in shfiles:
      with open(shfile,'r') as f:
        lines = f.readlines()
      for i,line in enumerate(lines):
        if( line.startswith('hadd') and not line.startswith('hadd -f') ):
          lines[i] = line.replace('hadd', 'hadd -f')
      with open(shfile,'w') as f:
        for line in lines: f.write(line)

    # do some printing and checks
    print('found {} executables to resubmit:'.format(len(shfiles)))
    for i in range(len(shfiles)):
        print(' - job {} -> executable {}'.format(jobids[i], shfiles[i]))
    print('continue with resubmission?')
    go = input()
    if go!='y': sys.exit()

    # remove the corresponding jobs
    print('canceling jobs and corresponding log files that will be resubmitted...')
    for jobid in jobids:
        os.system('condor_rm {}'.format(jobid))

    # modify the job description file and submit jobs
    print('resubmitting...')
    jobfile = 'cjob_skim.txt'
    with open(jobfile,'r') as f:
        lines = f.readlines()
    for shfile in shfiles:
        lines[0] = 'executable = {}\n'.format(shfile)
        with open(jobfile,'w') as f:
            for line in lines: f.write(line)
        os.system('condor_submit {}'.format(jobfile))

    # remove old version of error, output and log files
    print('removing old log files...')
    for i in range(len(shfiles)):
        efile = efiles[i]
        ofile = efile.replace('_err_', '_out_')
        lfile = efile.replace('_err_', '_log_')
        os.system('rm {}'.format(efile))
        os.system('rm {}'.format(ofile))
        os.system('rm {}'.format(lfile))
    
    print('done')
