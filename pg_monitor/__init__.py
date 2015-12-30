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
		check_warning_critical = defaults.getDefaults (param['check'], param['warning'], param['critical'] )

		if check_warning_critical != None :
			param['warning'] = check_warning_critical['warning']
			param['critical'] = check_warning_critical['critical'] 
			print (monitor.getChecks (param))
		else : 
			print ('Invalid command line arguments')
			sys.exit(0)

if __name__ == '__main__' :
	getArgs()
	
