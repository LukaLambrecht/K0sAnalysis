import sys
import os
import numpy as np
import json

var = {}
var["name"] =  "_mass"
var["variable"] = "_mass"
var["bins"] = list(np.linspace(0.44, 0.56, num=61, endpoint=True))
with open('variable_ks_invmass.json', 'w') as f:
    json.dump(var, f)


var = {}
var["name"] =  "_RPV"
var["variable"] = "_RPV"
var["bins"] = [0.0, 0.5, 1.0]
with open('variable_ks_rpv.json', 'w') as f:
    json.dump(var, f)
