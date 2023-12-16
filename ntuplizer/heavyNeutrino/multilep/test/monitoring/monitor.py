#!/usr/bin/env python3

##############################################################
# monitor crab jobs and put the results in a summary webpage #
##############################################################

# copied and modified from Kirill
# basic how to use:
# - follow the steps here if not done so before: https://t2bwiki.iihe.ac.be/PublicWebpages
# - run this script with 'python3 monitor.py --crabdir <crab log folder>'.
#   the crab log folder should be the folder grouping all crab logs within a heavyNeutrino release,
#   it is typically given by <some CMSSW version>/src/nanoSkimming/crabsubmission/crablogs.
# - it might take a long time to run if there are many samples
#   (since the crab status command is rather slow),
#   so it could be a good idea to run it in a screen terminal.
# - the result is stored in the form of a html document in ~/public_html/crab_status/index.html;
#   you can watch it in http://homepage.iihe.ac.be/~YOURUSERNAME/crab_status
# further notes on usage:
# - run with 'python3 monitor.py -h' for a list of all available args.
# - there are two prerequisites:
#   - this script requires a valid grid certificate (for the crab status command to work properly).
#     you can create one using 'voms-proxy-init --voms cms'.
#     optionally, you can set the location of your proxy using the '--proxy <path to your proxy>' argument.
#   - this script requires that you have a CMSSW environment (for the crab status command to work).
#     go to a recent CMSSW_<version>/src directory and run 'cmsenv' before running this script.
#   - to check if both prerequisites are satisfied, it might be a good idea to run a crab status command
#     on a single sample of your choice to see that it works properly, before running this script.
# - the default webpage name is 'crab_status' (see above), but it can be modified
#   with the '--webpage <name of webpage>' argument.
# - this script can be used to resubmit failed jobs as while doing the monitoring.
#   for this, you need to add the '--resubmit True' argument (the default is False).
# - in general, crab jobs are resubmittable up to 3 weeks after first submission (?),
#   and their status can be retrieved up to 4 weeks after first submission (?).
#   make sure to have stored a copy of the status before that deadline,
#   since ater that deadline the status is no longer retrievable 
#   and this script will output 'finished 0%' for each sample.
#   TO DO: implement some sort of check to avoid overwriting with 'finished 0%'?


import os, sys, glob, subprocess, pexpect, json
from datetime import datetime
import argparse

def define_css_style():
    ### define a fixed style string for the web page
    # only meant for internal use in web function

    s = '<style>'

    s += 'body {\n'
    s += 'margin: 0;\n'
    s += 'padding: 0;\n'
    s += 'width: 100%;\n'
    s += '}\n'

    s += 'h1 {\n'
    s += 'width: 100%;\n'
    s += 'text-align: center;\n'
    s += 'font-size:20px;\n'
    s += 'margin:0;\n'
    s += 'padding:0;\n'
    s += 'background: red;\n'
    s += 'color: #FFF;\n'
    s += 'display: inline-block;\n'
    s += '}\n'

    s += 'h3 {\n'
    s += 'width: 100%;\n'
    s += 'text-align: center;\n'
    s += 'font-size:15px;\n'
    s += 'background: #EAEDED;\n'
    s += 'margin:0;\n'
    s += 'padding:0;\n'
    s += 'display: inline-block;\n'
    s += '}\n'

    s += '.divide tr td { width:60%; }\n'

    # define style for progress bar, consisting of:
    # - "progress-container": the container for both the colored bars and text
    # - "progress-text": container for text overlaying the colored bars
    # - "progress-bar": the colored bar

    s += '.progress-container {\n'
    s += 'width: 100%;\n'
    s += 'height: 20px;\n'
    s += 'border: 1px solid black;\n'
    s += 'position: relative;\n'
    s += 'padding: 3px;\n'
    s += '}\n'

    s += '.progress-text {\n'
    s += 'position: absolute;\n'
    s += 'left: 5%;\n'
    s += '}\n'

    s += '.progress-bar {\n'
    s += 'position: absolute;\n'
    s += 'height: 20px;\n'
    s += '}\n'

    s += '</style>\n'

    return s


def make_progress_bar(progress_values):
    ### make html progress bar
    # input arguments:
    # - progress_values: a dict matching status names to percentages in str format,
    #   e.g. {'finished': '100%'}
    progress_str = ' '.join(['{}: {}'.format(key, val) for key, val in progress_values.items()])
    colors = {
      'finished': 'lightgreen',
      'transferring': 'turquoise',
      'running': 'deepskyblue',
      'failed': 'crimson'
    }
    html = '<td> <div class="progress-container">'
    cumul = 0
    for status, color in colors.items():
        if status not in progress_values.keys(): continue
        val = float(progress_values[status].strip('%'))
        stylestr = 'left: {}%; width: {}%; background-color: {}'.format(cumul, val, color)
        html += '<div class="progress-bar" style="{}"></div>'.format(stylestr)
        cumul += val
    html += '<div class="progress-text">'+progress_str+'</div>'
    html += '</div></td>'
    return html


def web( data, webpath, force=False ):
    ### convert sample completion info into a html document for web display.
    # input arguments:
    # - data: a dictionary as generated by the main section.
    #         it should contain the key 'samples' and optionally the key 'meta';
    #         the value for the 'meta' key is a str->str dict with meta-information
    #         to be displayed at the top of the page,
    #         the value for the 'samples' key is a dict matching sample names to status dicts.
    #         the sample names are assumed to be production/sample/version,
    #         and the status dicts are assumed to be str->str with status to fraction matching.
    #         example: data = {'samples': {
    #    'singlelepton_MC_2017_ULv5/
    #     WWG_TuneCP5_13TeV-amcatnlo-pythia8/
    #     crab_RunIISummer20UL17MiniAOD-106X_mc2017_realistic_v6-v2_singlelepton_MC_2017_ULv5': 
    #     {'running': '13.3%', 'finished': '73.3%', 'idle': '13.3%'}}}
    # - webpath: directory where the resulting index.html file should be stored.
    #            if it does not exist yet, it will be created;
    #            if it already exists and contains an index.html file, that file will be overwritten.

    # initializations
    now = datetime.now()
    if not os.path.exists(webpath): os.makedirs(webpath)

    # make the page layout and header
    page = '<html>\n'
    page += '<head>\n'+define_css_style()+'</head>\n'
    page += '<body>\n'
    page += '<table style="background-color:#2C3E50;color:#EAECEE;'
    page += 'font-size:40px;width:100%;text-align: center;">'
    page += '<tr><td>Status of ntuple production</td></tr>'
    page += '<tr><td style="font-size:15px;">Last update: '+now.strftime("%d/%m/%Y %H:%M:%S")+'</td></tr>'
    page += '</table>\n'

    # print some meta information
    page += '<div id="meta-info"><h1>Meta-info</h1></div>\n'
    if 'meta' in data.keys():
        meta = data['meta']
        for key,val in meta.items():
            page += '<table class="divide" cellpadding="5px" cellspacing="0">\n'
            page += '<tr>\n'
            page += '<td style="width:30%">'+key+'</td>'
            page += '<td style="widht:70%">'+val+'</td>\n'
            page += '</tr>\n'
        page += '</table>\n'
    else:
        page += '<table class="divide" cellpadding="5px" cellspacing="0">\n'
        page += '<tr>\n'
        page += '<td>(nothing to display)</td>'
        page += '</tr>\n'
        page += '</table>\n'

    # get the sample data
    sampledata = data['samples']

    # sort the sample list
    samples = sorted(list(sampledata.keys()),key=lambda x:x.lower())

    # loop over samples
    page += '<div id="samples"><h1>Samples</h1></div>\n'
    for sample in samples:

        # format sample name
        sampleparts = sample.split('/')
        samplename = sampleparts[1]
        sampleshortname = samplename.split('_')[0]
        versionname = sampleparts[2]
        versionshortname = versionname.replace('crab_','').split('-')[0]
        production = sampleparts[0]

        # get the grafana link for this sample
        sample_grafana = ''
        if 'grafana' in sampledata[sample].keys():
            sample_grafana = sampledata[sample]['grafana']

        # get the status data for this sample
        sample_status = sampledata[sample]['status']
        status_str = ', '.join('{}: {}'.format(key,val) 
            for key,val in sorted(sample_status.items()))
        finished_fraction = 0
        transferring_fraction = 0
        running_fraction = 0
        if 'finished' in sample_status.keys(): finished_fraction = float(sample_status['finished'].strip('%'))
        if 'transferring' in sample_status.keys(): transferring_fraction = float(sample_status['transferring'].strip('%'))
        if 'running' in sample_status.keys(): running_fraction = float(sample_status['running'].strip('%'))

        # special case for old submissions (status no longer retrievable):
        # avoid overwriting by 'finished 0%'.
        if not force:
            if( len(sample_status)==1
                and 'finished' in sample_status.keys()
                and finished_fraction == '0%' ):
                msg = 'ERROR: the status for the sample '+samplename
                msg += ' seems to be irretrievable,'
                msg += ' perhaps the submission is too long ago?'
                msg += ' Will not update the webpage to avoid overwriting useful information.'
                raise Exception(msg)

        # format the webpage entry
        page += '<table class="divide" cellpadding="5px" cellspacing="0">\n'
        page += '<tr>\n'
        # sample name
        page += '<td style="width:20%">'+sampleshortname+'</td>'
        # version name
        page += '<td style="width:20%">'+versionshortname+'</td>'
        # progress bar and text
        page += make_progress_bar(sample_status)
        # grafana link
        page += '<td style="width:20%"> <a href="'+sample_grafana+'" target="_blank">Grafana</a> </td>\n'
        page += '</tr>\n'

    page += '</table>\n'    
    page += '</body>\n'
    page += '</html>'

    wfile = open(os.path.join(webpath,'index.html'), 'w')
    wfile.write(page)
    wfile.close()


if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser('Monitor CRAB status')
    parser.add_argument('-c', '--crabdir', required=True, type=os.path.abspath,
      help='Main CRAB folder containing log files for all samples')
    parser.add_argument('-r', '--resubmit', default=False, action='store_true',
      help='Do resubmission of failed jobs (default: False, only monitor)')
    parser.add_argument('-p', '--proxy', default=None,
      help='Path to your proxy (default: do not export proxy explicitly)')
    parser.add_argument('-w', '--webpage', default='crab_status',
      help='Name of the webpage where the results will be displayed')
    parser.add_argument('-t', '--istest', default=False, action='store_true',
      help='Run in test mode, process only a few samples (default: False)')
    parser.add_argument('-f', '--force', default=False, action='store_true',
      help='Write web page even if the info for some samples could not be retrieved')
    parser.add_argument('--printraw', default=False, action='store_true',
      help='Print raw output of crab status command.')
    args = parser.parse_args()

    # print arguments
    print('Running with following configuration:')
    for arg in vars(args):
        print('  - {}: {}'.format(arg,getattr(args,arg)))

    # check command line arguments
    if not os.path.isdir(args.crabdir):
        raise Exception('ERROR: crab directory {} does not exist'.format(args.crabdir))
    if args.proxy is not None:
        if not os.path.exists(args.proxy):
            raise Exception('ERROR: provided proxy {} does not exist'.format(args.proxy))

    # export the proxy if requested
    if args.proxy is not None:
        os.system('export X509_USER_PROXY={}'.format(args.proxy))

    # parse the web path
    home = os.path.expanduser("~")
    webpath = os.path.join(home, 'public_html', args.webpage)

    # set variables and arguments for internal use
    templogfile = 'monitor_tmp_log.txt'

    # initializations
    data = {'meta': {'generating script': os.path.abspath(__file__),
            'command-line arguments': str(args)},
            'samples': {}}
    wdir = os.getcwd()
    passp = ['Enter GRID pass phrase for this identity:', pexpect.EOF]
    # note: once a proxy is created the password should not be needed anymore.
    # still, T2 asks the password sometimes, in which case simply '\n' should suffice
    # (see below)

    # move to crab directory and find all sample folders
    os.chdir(args.crabdir)
    fproc = sorted(glob.glob('*/*/*'))
    nfproc = len(fproc)

    # only for testing: subselect samples
    if args.istest:
        ntest = min(1, nfproc)
        print('WARNING: running in test mode, will only process'
             +' {} out of {} samples'.format(ntest, nfproc))
        fproc = fproc[:ntest]

    # initialize all samples to 0% finished and empty grafana link
    for fidx, f in enumerate(fproc):
        data['samples'][f] = {'status': {'finished':'0%'}, 'grafana':''}

    # loop over samples
    for fidx, f in enumerate(fproc):
        print('Now processing sample {} of {}'.format(fidx+1,len(fproc)))
        print('({})'.format(f))

        # run crab status command and write the output to a log file
        success = False
        attempt = 0
        while (attempt<5 and not success):
            cmd = 'crab status -d '+f
            if args.printraw: cmd += '  --verbose'
            ch = pexpect.spawn(cmd, encoding='utf-8')
            ch.timeout = 180 # in seconds, put large enough so the process finishes before limit
            ch.logfile = open(templogfile, 'w')
            passpindex = ch.expect(passp)
            if passpindex==0: ch.sendline('\n')
            ch.read()
            ch.close()
            # check the output
            with open(templogfile, 'r') as fin:
                outlines = fin.read().splitlines()
            if len(outlines)==0:
                print('Crab status seems to have failed, retrying...')
                attempt += 1
            else: success = True
        if not success:
            print('Crab status seems to have failed, skipping this sample.')
            data['samples'][f]['status'] = {'crab status': 'failed'}
            continue

        # read the log file
        jobsfailed = False
        statuscompleted = False
        with open(templogfile, 'r') as fin:
            outlines = fin.read().splitlines()
   
        # remove the log file
        os.system('rm {}'.format(templogfile))

        # print contents of log file
        if args.printraw:
            for line in outlines: print(line.strip('\n'))

        # parse the text from the log file
        for line in outlines:
            line = line.replace('Jobs status:','')
            words = line.split()
            if len(words)==0: continue
            # check for known job statuses
            for status in (['finished', 'running', 'transferring',
                            'failed', 'killed', 'idle','unsubmitted',
                            'toRetry']):
                if status in words[0]:
                    try: frac = words[2]
                    except: frac = '<none>'
                    # save to dict
                    data['samples'][f]['status'][status] = frac
                    # check if jobs failed for  this sample
                    if( status=='failed' ): jobsfailed = True
                    print('Percentage '+status+': '+frac)
            # find the grafana link
            if line.startswith('Dashboard monitoring URL'):
                data['samples'][f]['grafana'] = words[3]

            # check if job is complete
            if 'Status on the scheduler' in line:
                if 'COMPLETED' in line:
                    if not os.path.isfile(f+'/results/processedLumis.json'):
                        statuscompleted = True        

        # handle case where failed jobs were found
        if jobsfailed:
            if args.resubmit:
                print('Found failed jobs, now resubmitting...')
                ch = pexpect.spawn('crab resubmit -d '+f, encoding='utf-8')
                ch.timeout = 10000
                ch.expect(passp)
                ch.sendline('\n')
                ch.expect(passp)
                ch.sendline('\n')
                ch.read()
                ch.close()
                print('Done')

        # handle case where job is complete
        if statuscompleted:
            print('This task is completed.')

        # print separator
        print('\n----------------------------\n')

    # make web interface for gathered completion data              
    os.chdir(wdir)
    print('Loop over all samples completed.')
    print('Retrieved following data:')
    print(data)
    web(data, webpath, force=args.force)
    print('Sample status written to {}.'.format(webpath))
    print('Done.')
