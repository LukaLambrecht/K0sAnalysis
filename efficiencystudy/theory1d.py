###########################################################################
# plot some theoretical distributions of momentum-weighted profiles in 1D #
###########################################################################

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def profile( xax, momentum, mass, lifetime ):
    # input arguments
    # - xax: np array (units meter)
    # - momentum: np array with momentum values sampled from some momentum spectrum (units GeV/c)
    # - mass: mass of the particle (units GeV/c2)
    # - lifetime: proper lifetime of the particle (units seconds)
    nterms = len(momentum)
    npoints = len(xax)
    dists = np.zeros((nterms,npoints))
    for i,p in enumerate(momentum):
	const = p/mass*3e8*lifetime
	dists[i,:] = np.exp(-xax/const)
    dist = (1./nterms)*np.sum(dists,axis=0)
    return dist

def plotprofiles( xax, profiles, fig=None, ax=None, 
		    colorlist=[], labellist=[], transparencylist=[],
		    title=None, titlesize=None, 
		    xaxtitle=None, xaxtitlesize=None,
		    yaxtitle=None, yaxtitlesize=None, ymaxfactor=None, 
		    legendsize=None):
    ### plot profiles
    # initializations
    nprofiles = len(profiles)
    dolabel = True
    if len(labellist)==0:
        labellist = ['']*nprofiles
        dolabel = False
    if len(colorlist)==0:
        colorlist = ['red','blue','green','orange']
        if nprofiles>4:
            raise Exception('ERROR please specify the colors if you plot more than four profiles.')
    if len(transparencylist)==0:
        transparencylist = [1.]*nprofiles
    if fig is None or ax is None: fig,ax = plt.subplots()
    # plot the profiles
    for i in range(nprofiles):
        ax.plot(xax, profiles[i,:], color=colorlist[i], label=labellist[i], 
		alpha=transparencylist[i])
    # axis ranges and other post-editing
    if ymaxfactor is not None:
        ymin,ymax = ax.get_ylim()
        ax.set_ylim( (ymin, ymax*ymaxfactor) )
    if dolabel: 
        leg = ax.legend(loc='upper right', fontsize=legendsize)
    if title is not None: ax.set_title(title, fontsize=titlesize)
    if xaxtitle is not None: ax.set_xlabel(xaxtitle, fontsize=xaxtitlesize)
    if yaxtitle is not None: ax.set_ylabel(yaxtitle, fontsize=yaxtitlesize)
    return (fig,ax)

if __name__=='__main__':

    # make an x-axis
    xax = np.linspace(0., 1., num=100)

    # set particle properties
    mass = 0.5
    lifetime = 8.95e-11

    # define the momentum distributions
    momentumdists = []
    momentumdists.append( {'dist':np.array([3.]), 'label':'p = 3 GeV'} )
    momentumdists.append( {'dist':np.array([5.]), 'label':'p = 5 GeV'} )
    momentumdists.append( {'dist':np.array([10.]), 'label':'p = 10 GeV'} )
    momentumdists.append( {'dist':np.random.lognormal(mean=np.log(5), sigma=np.log(2), size=100), 
			    'label':'logN(5,2)'} )
    
    # make the profiles
    profiles = np.zeros((len(momentumdists),len(xax)))
    for i,p in enumerate(momentumdists):
	profiles[i,:] = profile( xax, p['dist'], mass, lifetime )
    
    # plot the profiles
    fig,ax = plotprofiles( xax, profiles, labellist=[el['label'] for el in momentumdists] )
    fig.savefig('test.png')
