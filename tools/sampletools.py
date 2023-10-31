#############################################################################
# python script grouping some useful functions for reading the sample lists #
#############################################################################

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

def yearfromfilename(filename):
    # extract the campaign and year from the name of an input file
    if( "RunIISummer20UL16MiniAODAPVv2" in filename
        or "HIPM_UL2016_MiniAODv2" in filename ):
        return ("run2ul", "2016PreVFP")
    elif( "RunIISummer20UL16MiniAODv2" in filename
        or "UL2016_MiniAODv2" in filename ):
        return ("run2ul", "2016PostVFP")
    elif( "RunIISummer20UL17MiniAODv2" in filename
        or "UL2017_MiniAODv2" in filename ):
        return ("run2ul", "2017")
    elif( "RunIISummer20UL18MiniAODv2" in filename
        or "UL2018_MiniAODv2" in filename ):
        return ("run2ul", "2018")
    elif( "Run2016" in filename
        or "RunIISummer16" in filename ):
        return ("run2preul", "2016")
    elif( "Run2017" in filename
        or "RunIIFall17" in filename ):
        return ("run2preul", "2017")
    elif( "Run2018" in filename
        or "RunIIAutumn18" in filename ):
        return ("run2preul", "2018")
    else:
        msg = "ERROR: year could not be extracted from filename"
        msg += " " + filename
        raise Exception(msg)
