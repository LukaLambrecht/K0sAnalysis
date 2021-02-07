################################
# set of tools involving lists #
################################

def split(inputlist,partsize):
    # split inputlist in partial lists of len = partsize (last one can be shorter)
    # return type is a list of those partial lists
    outputlist = []
    begin = 0
    while begin<len(inputlist):
	end = begin+partsize
	if end>=len(inputlist):
	    outputlist.append(inputlist[begin:])
	    break
	else:
	    outputlist.append(inputlist[begin:end])
	    begin = end
    return outputlist
