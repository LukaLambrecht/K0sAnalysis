############################
# V0 selection definitions #
############################

### interface function mapping selection name to function

def selection(branches, selection_name, extra=None):
    if(selection_name=='legacy'): return selection_legacy(branches, extra=extra)
    else:
        msg = 'ERROR: in pass_selection:'
        msg += ' selection function '+selection_name+' not recognized.'
        raise Exception(msg)

### help functions for calculating additional variables

def cospointing(branches, reference='primaryVertex'):
  x = branches['_V0X'] - branches['_{}X'.format(reference)]
  y = branches['_V0Y'] - branches['_{}Y'.format(reference)]
  px = branches['_V0Px']
  py = branches['_V0Py']
  cospointing = (x*px + y*py) / ( (x**2+y**2)**(1./2) * (px**2+py**2)**(1./2) )
  return cospointing

### selection functions

def selection_legacy( branches, extra=None ):
  if 'cospointingPV' not in extra.keys():
    extra['cospointingPV'] = cospointing(branches, reference='primaryVertex')
  if 'cospointingBS' not in extra.keys():
    extra['cospointingBS'] = cospointing(branches, reference='beamSpot')
  selmask = (
    (branches['_V0NHitsPos'] >= 6)
    & (branches['_V0NHitsNeg'] >= 6)
    & (branches['_V0PtPos'] > 1.)
    & (branches['_V0PtNeg'] > 1.)
    & (branches['_V0DCA'] < 0.2)
    & (branches['_V0VtxNormChi2'] < 7)
    & (extra['cospointingPV'] > 0.99)
    & (extra['cospointingBS'] > 0.99)
  )
  return selmask
