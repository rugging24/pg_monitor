#!/usr/bin/python

# find param : ipl_api.init_de_request
import defaults, helpText 
import monitor
import sys


def getHelpText() :
	print ( helpText.getDescText() ) 

def getArgs(param) :
	if param != None :	
		warning = param.get('warning')
		critical = param.get('critical')
		check_warning_critical = defaults.getDefaults (param['check'], warning, critical )

		if check_warning_critical != None :
			param['warning'] = check_warning_critical['warning']
			param['critical'] = check_warning_critical['critical'] 
			print (monitor.getChecks (param))
		else : 
			getHelpText()
			sys.exit(0)
