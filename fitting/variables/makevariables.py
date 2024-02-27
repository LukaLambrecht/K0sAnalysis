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
var["name"] =  "#Delta_{2D} (cm)"
var["variable"] = "_RPV"
var["bins"] = [0.0, 0.5, 1.0, 19.5, 20.0]
with open('variable_ks_rpv.json', 'w') as f:
    json.dump(var, f)

var = {}
var["name"] =  "_mass"
var["variable"] = "_mass"
var["bins"] = list(np.linspace(1.08, 1.15, num=71, endpoint=True))
with open('variable_la_invmass.json', 'w') as f:
    json.dump(var, f)


var = {}
var["name"] =  "#Delta_{2D} (cm)"
var["variable"] = "_RPV"
var["bins"] = [0.0, 0.5, 1.0, 19.5, 20.0]
with open('variable_la_rpv.json', 'w') as f:
    json.dump(var, f)
