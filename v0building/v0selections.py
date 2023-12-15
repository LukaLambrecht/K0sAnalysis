############################
# V0 selection definitions #
############################

### interface function mapping selection name to function

def selection(branches, selection_name, **kwargs):
    if(selection_name=='legacy'): return selection_legacy(branches, **kwargs)
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

def selection_legacy( branches, extra=None, cutflow=False ):
  if 'cospointingPV' not in extra.keys():
    extra['cospointingPV'] = cospointing(branches, reference='primaryVertex')
  if 'cospointingBS' not in extra.keys():
    extra['cospointingBS'] = cospointing(branches, reference='beamSpot')
  allmasks = {
    #'nhitspos': (branches['_V0NHitsPos'] >= 6),
    #'nhitsneg': (branches['_V0NHitsNeg'] >= 6),
    'ptpos': (branches['_V0PtPos'] > 1.),
    'ptneg': (branches['_V0PtNeg'] > 1.),
    #'normchi2pos': (branches['_V0NormChi2Pos'] < 5.),
    #'normchi2neg': (branches['_V0NormChi2Neg'] < 5.),
    'dca': (branches['_V0DCA'] < 0.2),
    'normchi2vtx': (branches['_V0VtxNormChi2'] < 7),
    'cospointingpv': (extra['cospointingPV'] > 0.99),
    'cospointingbs': (extra['cospointingBS'] > 0.99),
  }
  selmask = list(allmasks.values())[0]
  for mask in allmasks.values():
    selmask = (selmask & mask)
  if not cutflow: return selmask
  else: return (selmask, allmasks)
