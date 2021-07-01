######################################
# tools for merging files using hadd #
######################################
import os
import sys
import jobsubmission as jobsub

def mergefiles(input_file_list,output_file_name,removeinput=False):
    ### merge files in inputfilelist into outputfile
    # all files in inputfilelist are assumed to be root files

    if len(input_file_list)<=1: return
    output_directory = output_file_name.rsplit('/',1)[0]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    command = 'hadd '+output_file_name
    for f in input_file_list:
        command += ' '+f
    scriptname = 'qjob_merge.sh'
    with open(scriptname,'w') as script:
        jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_20')
	script.write('1>&2 echo "### starting ###"\n')
        script.write(command+'\n')
        if removeinput:
            for f in input_file_list:
                script.write('rm '+f+'\n')
	script.write('1>&2 echo "### done ###"\n')
    jobsub.submitQsubJob(scriptname)

def mergeallfiles(input_directory,output_file_name,removeinput=False):
    ### same as mergefiles but merging all root files in a directory 
    # (using wildcard for shorter command and avoid potential errors)

    input_file_list = ([os.path.join(input_directory,f) for f in os.listdir(input_directory)
                        if f[-5:]=='.root'])
    if len(input_file_list)<=1: return
    output_directory = output_file_name.rsplit('/',1)[0]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    command = 'hadd '+output_file_name+' '+os.path.join(input_directory,'*.root')
    scriptname = 'qjob_merge.sh'
    with open(scriptname,'w') as script:
        jobsub.initializeJobScript(script,cmssw_version='CMSSW_10_2_20')
	script.write('1>&2 echo "### starting ###"\n')
        script.write(command+'\n')
        if removeinput:
            for f in input_file_list: script.write('rm '+f+'\n')
	script.write('1>&2 echo "### done ###"\n')
    jobsub.submitQsubJob(scriptname)
