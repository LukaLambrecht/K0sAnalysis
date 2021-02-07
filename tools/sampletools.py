############################################################################################
# python script grouping some useful functions for reading the sample lists in this folder #
############################################################################################

def getsampleinfo(line):
    ### extract directory, sample name and version name from a single line in a sample list
    # line is assumed to be formatted as /pnfs/.../<user>/heavyNeutrino/<sample>/<version>
    if(len(line)==0 or line[0]!='/'):
	print('### WARNING ###: line '+line+' in sample list is not valid.')
	return
    line = line.rstrip('/\n')
    [directory,sample,version] = line.rsplit('/',2)
    return {'line':line,'directory':directory,
	    'sample_name':sample,'version_name':version}

def readsamplelist(samplelist):
    ### read all lines from a sample list
    # return type is a list of dicts (output of getsampleinfo)
    output = []
    with open(samplelist) as f:
	for line in f:
	    if len(line)==0: continue
	    if line[0]!='/': continue
	    line = line.rstrip('\n')
	    lineinfo = getsampleinfo(line)
	    if lineinfo is not None: output.append(lineinfo)
    return output
