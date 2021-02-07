#######################################################################
# A tool for restructuring the output of runLocal.sh in the ntuplizer #
#######################################################################
import os
import glob

directory = '/storage_mnt/storage/user/llambrec/Kshort/files/RunIIFall17_JPsiToMuMu_MINIAODSIM_test/'
#directory = '/storage_mnt/storage/user/llambrec/Kshort/files/test/'
do_group = False # whether or not to call hadd to group files
group = 5
if not do_group:
	group = 1

infiles = []
for infile in glob.glob(directory+'noskim_*.root'):
	infiles.append(infile)
infiles.sort()

def process(subset,index):
	os.system('mkdir job'+str(index))
	cmd = 'hadd job'+str(index)+'.root '
	for infile in subset:
		os.system('mv '+infile+' job'+str(index)+'/')
		cmd += infile[infile.rfind('/')+1:]+' '
	if do_group:
		os.chdir('job'+str(index))
		os.system(cmd)
		os.system('rm noskim_*.root')
		os.chdir(directory)

os.chdir(directory)
counter = 0
index = 0
subset = []
while counter<len(infiles):
	if(counter>0 and counter%group==0):
		process(subset,index)
		index += 1
		subset = []
	subset.append(infiles[counter])
	counter += 1
if(len(subset)>0):
	process(subset,index)
	index += 1
	
metafile = open('restructure.txt','w')
metafile.write('original number of files: '+str(len(infiles))+'\n')
metafile.write('grouping factor: '+str(group)+'\n')
metafile.write('resulting number of files: '+str(index)+'\n')
metafile.close()


	
