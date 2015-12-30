#!/usr/bin/python

# list of valid actions 
# backends 
#connections
# wals
# autovacuum
# vacuum
# autoanalyze 
# analyze 
# tale_bloat 
# index_bloat 
# table_size
# index_size 
# database_size 
# nonblocking
# blocking
# checkpoints 
# duplicate_indexes
# replica_lag

# find param : ipl_api.init_de_request
import defaults
import monitor
import sys


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
			if param['check'] in ['checkpoints','table_size','index_size', 'database_size','table_bloat','index_bloat' ] :
				print ('This check requires warning and/or critical value(s) to be correctly stated.')
			print ('Invalid command line arguments')
			sys.exit(0)

#if __name__ == '__main__' :
#	getArgs()
	
