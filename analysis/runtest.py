import os
import sys


if __name__=='__main__':

    filedir = '/pnfs/iihe/cms/store/user/llambrec/k0sanalysisdata/ulfiles/selected/'
    version = 'run2ul'
    #config = 'config_ksvars_test.py' # for 1D
    config = 'config_ks2dvars_test.py' # for 2D
    outputdir = 'output_test'
    eras = '2018'
    runmode = 'local'
    nentries = 100000

    cmd = 'python3 mcvsdata_submit.py'
    cmd += ' -i {}'.format(filedir)
    cmd += ' -v {}'.format(version)
    cmd += ' -c {}'.format(config)
    cmd += ' -o {}'.format(outputdir)
    cmd += ' -e {}'.format(eras)
    cmd += ' --runmode {}'.format(runmode)
    cmd += ' -n {}'.format(nentries)

    os.system(cmd)
