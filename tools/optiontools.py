###################################################
# tools for parsing options from the command line #
###################################################
import os
import sys
import json

def parse_value( option_name, option_value, option_type ):
    if option_type=='str':
	return option_value
    elif option_type=='path':
	try: 
	    option_value = os.path.abspath(option_value)
	    return option_value
	except: 
	    raise Exception('ERROR in option {}:'.format(option_name)
			    +' value {} could not be converted'.format(option_value)
			    +' to absolute path.')
    elif option_type=='int':
	try: 
	    option_value = int(option_value)
	    return option_value
	except:
	    raise Exception('ERROR in option {}:'.format(option_name)
                            +' value {} could not be converted'.format(option_value)
                            +' to an integer.')
    elif option_type=='float':
        try:
            option_value = float(option_value)
            return option_value
        except:
            raise Exception('ERROR in option {}:'.format(option_name)
                            +' value {} could not be converted'.format(option_value)
                            +' to a float.')
    elif option_type=='bool':
	if isinstance(option_value,bool): return option_value
	if not (option_value=='True' or option_value=='true'
		or option_value=='False' or option_value=='false'):
	    raise Exception('ERROR in option {}:'.format(option_name)
			    +' value {} could not be converted'.format(option_value)
			    +' to a boolean.')
	return (option_value=='True' or option_value=='true')
    elif option_type=='list':
	# note: do not use '1.' notation, only '1.0' works in the json decoder!
	if isinstance(option_value,list): return option_value
	try:
	    option_value = json.loads(option_value)
	    return option_value
        except:
            raise Exception('ERROR in option {}:'.format(option_name)
                            +' value {} could not be converted'.format(option_value)
                            +' to a list.')
    else:
	raise Exception('ERROR in option {}:'.format(option_name)
                            +' requested type {} not recognized.'.format(option_type))


class Option(object):

    def __init__( self, name, value=None, default=None, 
		    vtype='str', explanation=None ):
	self.name = name
	self.vtype = vtype
	if default is not None:
	    default = parse_value(name, default, vtype)
	self.default = default
	self.value = default
	if value is not None:
	    self.set_value( value )
	self.explanation = explanation

    def set_value( self, value ):
	if value is not None:
	    value = parse_value(self.name, value, self.vtype)
	self.value = value

    def __str__( self ):
	info = 'name: {}'.format(self.name)
	info += ', value: {}'.format(self.value)
	info += ', default: {}'.format(self.default)
	if self.explanation is not None: 
	    info += ', explanation: {}'.format(self.explanation)
	return info

class OptionCollection(object):

    def __init__( self, options=[] ):
	self.option_names = [opt.name for opt in options]
	self.options = {}
	for opt in options:
	    setattr(self, opt.name, opt.value)
	    self.options[opt.name] = opt
	
    def parse_options( self, optstring ):
	### parse an option string
	# input arguments:
	# - optstring: expexted to have the format '--name1 value1 --name2 value2 ...'
	# - required: list of required option names
	# - valid: list of valid option names (default: no validity check)
	if len(optstring)==0: return
	if isinstance(optstring,list):
	    optstring = ' '.join(optstring)
	options = optstring.split('--')[1:]
	for opt in options:
	    opt = opt.strip(' ')
	    (name,value) = opt.split(' ',1)
	    if( name not in self.option_names ):
		raise Exception('ERROR: option {} not valid; valid options are {}'
				    .format(name,self.option_names))
	    self.options[name].set_value( value )
	    setattr(self, name, self.options[name].value)
   
    def __str__( self ):
	info = '--- Option collection ---\n'
	for opt in self.option_names:
	     info += str(self.options[opt])+'\n'
	info = info.strip('\n')
	return info
