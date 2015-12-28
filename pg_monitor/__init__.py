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


import argparse
import defaults

def getArgs() :
	parse = argparse.ArgumentParser(prog='pg_monitor' ,description = 'Checks for a PostgreSQL server')
	parse.add_argument ('--port' , type=int , default=5432 , help='Port of the database to be accessed. Default:  %(default)s')
	parse.add_argument ( '--user' , type=str , default='postgres', help='Username allowed to access the database. Default:  %(default)s')
	parse.add_argument ('--password', type=str , default='' , help='Password of the supplied user. Default:  %(default)s' )
	parse.add_argument ( '--dbname', type=str , default='postgres', help='The name of the database to be accessed. Default:  %(default)s'  )
	parse.add_argument ( '--host', type=str , default='localhost', help='Host of the database. Default:  %(default)s' )
	parse.add_argument ( '--check', type=str, required=True, choices=['backends','connections','wals','vacuum','autovacuum','analyze','autoanalyze',\
                             'table_bloat','index_bloat','blocking','nonblocking','table_size','index_size','database_size','checkpoints',\
                              'duplicate_indexes','replica_lag'], help='Options to be passed as checks' )
	parse.add_argument ( '--warning', type=str, help='Values to be considered as warning signs ' )
	parse.add_argument ( '--critical', type=str , help='Values for the critical checks') 
	# assign all arguments to an array
	args = parse.parse_args()
	# Get the individual arguments
	param = {}
	param['host'] = args.host
	param['port'] = args.port 
	param['user'] = args.user 
	param['password'] = args.password 
	param['dbname'] = args.dbname 
	param['check'] = args.check 
	
	check_warning_critical = defaults.getDefaults (args.check, args.warning, args.critical )

	if check_warning_critical != None :
		param['warning'] = check_warning_critical['warning']
		param['critical'] = check_warning_critical['critical'] 
		print (param)
	else : 
		print ('bad')


if __name__ == '__main__' :
	getArgs()
	
