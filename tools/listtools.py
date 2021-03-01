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

###########################################################
# some tools for making subselections in lists of objects #
###########################################################

def subselect_strings(stringlist,mustcontainone=[],mustcontainall=[],
                        maynotcontainone=[],maynotcontainall=[]):
    ### generic function to subselect strings from a list of strings
    ### return type is (list of selected indices, list of selected strings)
    sellist = []
    indlist = []
    for i,s in enumerate(stringlist):
        if subselect_string(s,mustcontainone=mustcontainone,
                            mustcontainall=mustcontainall,
                            maynotcontainone=maynotcontainone,
                            maynotcontainall=maynotcontainall):
            sellist.append(s)
            indlist.append(i)
    return (indlist,sellist)

def subselect_objects(objlist,idlist,mustcontainone=[],mustcontainall=[],
                        maynotcontainone=[],maynotcontainall=[]):
    ### generic function to subselect objects from a list of objects.
    ### selection is done string-based, using a string identifier for each object.
    ### return type is (list of selected indices, list of selected objects)
    if( len(objlist)!=len(idlist) ):
        print('### ERROR ###: list of objects and list of identifiers have different lengths')
        return []
    (indlist,_) = subselect_strings(idlist,mustcontainone=mustcontainone,
                                mustcontainall=mustcontainall,
                                maynotcontainone=maynotcontainone,
                                maynotcontainall=maynotcontainall)
    selobjlist = [objlist[i] for i in indlist]
    return (indlist,selobjlist)

def subselect_string(string,mustcontainone=[],mustcontainall=[],
                        maynotcontainone=[],maynotcontainall=[]):
    ### return a boolean whether a given string satisfies all criteria
    # check if string contains at least one tag in mustcontaineone
    if( len(mustcontainone)>0 ):
        sat = False
        for tag in mustcontainone:
            if tag in string:
                sat = True
                break
        if not sat: return False
    # check if string contains all tags in mustcontainall
    if( len(mustcontainall)>0 ):
        sat = True
        for tag in mustcontainall:
            if tag not in string:
                sat = False
                break
        if not sat: return False
    # check if string contains no tag in maynotcontainone
    if( len(maynotcontainone)>0 ):
        sat = True
        for tag in maynotcontainone:
            if tag in string:
                sat = False
                break
        if not sat: return False
    # check if string does not contain all tags in maynotcontainall
    if( len(maynotcontainall)>0 ):
        sat = False
        for tag in maynotcontainall:
            if tag not in string:
                sat = True
                break
        if not sat: return False
    # string satisfies all conditions
    return True
