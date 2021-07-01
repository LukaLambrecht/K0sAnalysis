##############################################################################
# python classes corresponding to reconstructed V0 objects (K0s and Lambda0) #
##############################################################################

import ROOT.Math as R
from v0selections import pass_selection

# define constants
pimass = 0.13957

class Track:

    # properties:
    # self.fourmomentum		= ROOT.Math.LorentzVector
    # self.nhits
    # self.charge		= 1 for pos and -1 for neg
    # self.d0			= signed transverse impact parameter
    # self.dz			= signed longitudinal impact parameter
    # self.isolation		= isolation variable
    # additional parameters (not stored in older versions of the ntuples)
    # self.loosequality		= bool for loose quality criteria
    # self.transipsig		= transvers impact parameter significance
    
    def __init__( self, treeEntry, v0index, charge ):
	# constructor from an entry in a TTree at given V0 index and charge (1 or -1)
	suffix = 'Pos'
	if charge<0: suffix = 'Neg'
	self.fourmomentum = R.PtEtaPhiMVector( getattr(treeEntry,'_V0Pt'+suffix)[v0index],
					       getattr(treeEntry,'_V0Eta'+suffix)[v0index],
					       getattr(treeEntry,'_V0Phi'+suffix)[v0index],
					       pimass ) # dummy value for mass, maybe extend later
	self.nhits = getattr(treeEntry,'_V0NHits'+suffix)[v0index]
	self.charge = 1 if charge > 0 else -1
	self.d0 = getattr(treeEntry,'_V0D0'+suffix)[v0index]
	self.dz = getattr(treeEntry,'_V0Dz'+suffix)[v0index]
	self.isolation = getattr(treeEntry,'_V0Iso'+suffix)[v0index]
	# additional track parameters (not stored in older versions of the ntuples)
	self.loosequality = False
	if hasattr(treeEntry,'_V0LooseQuality'+suffix): 
	    self.loosequality = (getattr(treeEntry,'_V0LooseQuality'+suffix)[v0index]>0.5)
	self.transipsig = 0.
	if hasattr(treeEntry,'_V0TransIPSig'+suffix):
	    self.transipsig = getattr(treeEntry,'_V0TransIPSig'+suffix)[v0index]

    def copy( self ):
	# deep copy function
	track = Track()
	track.fourmomentum = R.PtEtaPhiMVector( self.fourmomentum.Pt(), self.fourmomentum.Eta(),
                                                self.fourmomentum.Phi(), self.fourmomentum.M() )
	track.nhits = self.nhits
	track.charge = self.charge
	track.d0 = self.d0
	track.dz = self.dz
	track.isolation = self.isolation
	track.loosequality = self.loosequality
	track.transipsig = self.transipsig

class V0Object:

    # properties:
    # - self.mass
    # - self.kind
    # - self.vertex		= (x,y,z) tuple
    # - self.fourmomentum	= ROOT.Math.LorentzVector
    # - self.postrack		= Track object
    # - self.negtrack		= Track object
    # - self.vardict		= a dict with additional v0 vars stored in the skimmed ntuples

    def __init__( self, treeEntry, v0index ):
	# constructor from an entry in a TTree at given V0 index
	if not hasattr(treeEntry,'_nV0s'):
	    print('### ERROR ###: tree does not seem to contain the branch _nV0s')
	    return 
	if v0index>=getattr(treeEntry,'_nV0s'):
	    print('### ERROR ###: requested v0index is >= _nV0s')
	self.mass = getattr(treeEntry,'_V0InvMass')[v0index]
	numtokind = {1:'k0s',2:'l0',3:'l0bar'}
	self.kind = numtokind[int(getattr(treeEntry,'_V0Type')[v0index])]
	self.vertex = ( getattr(treeEntry,'_V0X')[v0index], 
			getattr(treeEntry,'_V0Y')[v0index],
			getattr(treeEntry,'_V0Z')[v0index] )
	self.fourmomentum = R.PtEtaPhiMVector(	getattr(treeEntry,'_V0Pt')[v0index],
						getattr(treeEntry,'_V0Eta')[v0index],
						getattr(treeEntry,'_V0Phi')[v0index],
						getattr(treeEntry,'_V0InvMass')[v0index] )
	self.postrack = Track( treeEntry, v0index, 1 )
	self.negtrack = Track( treeEntry, v0index, -1 )
	self.vardict = {}
	for varname in ['_V0DCA','_V0VtxNormChi2']:
	    self.vardict[varname] = getattr(treeEntry,varname)[v0index]

    def copy( self ):
	# deep copy function
	v0obj = V0Ojbect()
	v0obj.mass = self.mass
        v0obj.kind = self.kind
        v0obj.vertex = ( self.vertex[0], self.vertex[1], self.vertex[2] )
        v0obj.fourmomentum = R.PtEtaPhiMVector( self.fourmomentum.Pt(), self.fourmomentum.Eta(),
						self.fourmomentum.Phi(), self.fourmomentum.M() )
        v0obj.postrack = self.postrack.copy()
        v0obj.negtrack = self.negtrack.copy()

    def passSelection( self, selection, extra=None ):
	# return a bool whether V0Object passes a selection
	return pass_selection( self, selection, extra )

    def trackdR( self ):
	# return dR between the two tracks
	return R.VectorUtil.DeltaR( self.postrack.fourmomentum, self.negtrack.fourmomentum )

class V0Collection:
    
    # properties:
    # self.v0collection = list of V0Objects
    # self.nv0 = number of V0Objects in self.v0collection
    # self.kind =   'all' for mixed, 
    #		    'k0s' for only K0s
    #		    'l0' for Lambda0 
    #		    'l0bar' for Lambda0Bar
    
    def __init__( self, v0list=None, kind='all' ):
	# constructor from a list of V0 objects
	self.v0collection = []
	self.nv0 = 0
	self.kind = kind
	if not kind in ['all','k0s','l0','l0bar']:
            print('### ERROR ###: argument kind='+kind+' passed to V0Collection not recognized')
            return
	if v0list==None: return
	for obj in v0list:
	    if not isinstance(obj,V0Object):
		print('### ERROR ###: object passed to V0Collection constructor not recognized')
		return
	    if(kind!='all' and obj.kind!=kind): continue
	    self.v0collection.append(obj)
	self.nv0 = len(self.v0collection)

    def initFromTreeEntry( self, treeEntry, kind='all' ):
	# constructor from an entry in a TTree
	# only v0s of kind 'kind' are taken into the collection
	self.v0collection = []
	self.nv0 = 0
	self.kind = kind
	if not hasattr(treeEntry,'_nV0s'):
	    print('### ERROR ###: tree does not seem to contain the branch _nV0s')
	    return
	if not kind in ['all','k0s','l0','l0bar']:
            print('### ERROR ###: argument kind='+kind+' passed to V0Collection not recognized')
            return
	for i in range(getattr(treeEntry,'_nV0s')):
	    v0obj = V0Object(treeEntry,i)
	    if(kind!='all' and v0obj.kind!=kind): continue
	    self.v0collection.append(v0obj) 
	self.nv0 = len(self.v0collection)

    def __getitem__( self, index ):
	# overload get item operator to return V0Object at index
	return self.v0collection[index]

    def __add__( self, other ):
	# overload addition operator
	kind = 'all'
	if self.kind==other.kind: kind = self.kind
	return V0Collection( self.v0collection+other.v0collection, kind=kind )
	
    def size( self ):
	# return number of elements in collection
	return self.nv0

    def getK0sCollection( self ):
	return V0Collection( self.v0collection, kind='k0s' )

    def getLambda0Collection( self ):
	return V0Collection( self.v0collection, kind='l0' )

    def getLambda0BarCollection( self ):
	return V0Collection( self.v0collection, kind='l0bar' )

    def applySelection( self, selection, extra=None ):
	newv0collection = []
	for v0obj in self.v0collection:
	    if v0obj.passSelection(selection,extra): newv0collection.append(v0obj)
	self.v0collection = newv0collection
	self.nv0 = len(self.v0collection)
