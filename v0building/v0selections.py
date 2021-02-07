##############################################
# file containing V0 selection functionality #
##############################################

import numpy as np
from v0object import *

##### interface function mapping selection name to function #####

def pass_selection( v0object, selection_name, extra=None ):
    # v0object is an object of type V0Object
    # extra is a dict whose content can differ for different selection functions
    if(selection_name=='legacy'): return selection_legacy( v0object, extra )
    if(selection_name=='legacy_loosenhits'): return selection_legacy_loosenhits( v0object, extra )
    if(selection_name=='legacy_nonhits'): return selection_legacy_nonhits( v0object, extra )
    if(selection_name=='legacy_highpt'): return selection_legacy_highpt( v0object, extra )
    else:
	print('### ERROR ###: selection function '+selection_name+' not recognized.')
	return False

##### help functions #####

def cospointing( v0object, point ):
    
    x = v0object.vertex[0] - point[0]
    y = v0object.vertex[1] - point[1]
    px = v0object.fourmomentum.Px()
    py = v0object.fourmomentum.Py()
    return (x*px + y*py) / (np.sqrt(x**2+y**2)*np.sqrt(px**2+py**2))

##### selection functions #####

def selection_legacy( v0object, extra ):
    # extra must contain 'primaryVertex':(x,y,z) and 'beamSpot':(x,y,z)

    # track quality cuts
    if( v0object.postrack.nhits < 6 
	or v0object.negtrack.nhits < 6 ): return False
    if( v0object.postrack.fourmomentum.Pt() < 1
	or v0object.negtrack.fourmomentum.Pt() < 1): return False
    # dca cut
    if( v0object.vardict['_V0DCA'] > 0.2 ): return False
    # vertex fit chi2 cut
    if( v0object.vardict['_V0VtxNormChi2'] > 7 ): return False
    # cos pointing angle
    if( ('primaryVertex' not in extra.keys()) or ('beamSpot' not in extra.keys()) ):
	print('### ERROR ###: extra argument for selection_legacy must contain'
		+' primary vertex and beamspot')
	return False
    if( cospointing(v0object,extra['primaryVertex']) < 0.99
	    or cospointing(v0object,extra['beamSpot']) < 0.99): return False
    return True 

def selection_legacy_loosenhits( v0object, extra ):
    # same requirement and selection as for selection_legacy
    # only a bit looser on number of hits
    
    # track quality cuts
    if( v0object.postrack.nhits < 4
        or v0object.negtrack.nhits < 4 ): return False
    if( v0object.postrack.fourmomentum.Pt() < 1
        or v0object.negtrack.fourmomentum.Pt() < 1): return False
    # dca cut
    if( v0object.vardict['_V0DCA'] > 0.2 ): return False
    # vertex fit chi2 cut
    if( v0object.vardict['_V0VtxNormChi2'] > 7 ): return False
    # cos pointing angle
    if( ('primaryVertex' not in extra.keys()) or ('beamSpot' not in extra.keys()) ):
        print('### ERROR ###: extra argument for selection_legacy must contain'
                +' primary vertex and beamspot')
        return False
    if( cospointing(v0object,extra['primaryVertex']) < 0.99
            or cospointing(v0object,extra['beamSpot']) < 0.99): return False
    return True

def selection_legacy_nonhits( v0object, extra ):
    # same requirement and selection as for selection_legacy_loosenhits
    # but not requiring number of hits at all
    
    # track quality cuts
    if( v0object.postrack.fourmomentum.Pt() < 1
        or v0object.negtrack.fourmomentum.Pt() < 1): return False
    # dca cut
    if( v0object.vardict['_V0DCA'] > 0.2 ): return False
    # vertex fit chi2 cut
    if( v0object.vardict['_V0VtxNormChi2'] > 7 ): return False
    # cos pointing angle
    if( ('primaryVertex' not in extra.keys()) or ('beamSpot' not in extra.keys()) ):
        print('### ERROR ###: extra argument for selection_legacy must contain'
                +' primary vertex and beamspot')
        return False
    if( cospointing(v0object,extra['primaryVertex']) < 0.99
            or cospointing(v0object,extra['beamSpot']) < 0.99): return False
    return True

def selection_legacy_highpt( v0object, extra ):
    # same requirement and selection as for selection_legacy
    # but with higher pt threshold on the tracks

    # track quality cuts
    if( v0object.postrack.fourmomentum.Pt() < 5
        or v0object.negtrack.fourmomentum.Pt() < 5): return False
    # dca cut
    if( v0object.vardict['_V0DCA'] > 0.2 ): return False
    # vertex fit chi2 cut
    if( v0object.vardict['_V0VtxNormChi2'] > 7 ): return False
    # cos pointing angle
    if( ('primaryVertex' not in extra.keys()) or ('beamSpot' not in extra.keys()) ):
        print('### ERROR ###: extra argument for selection_legacy must contain'
                +' primary vertex and beamspot')
        return False
    if( cospointing(v0object,extra['primaryVertex']) < 0.99
            or cospointing(v0object,extra['beamSpot']) < 0.99): return False
    return True
