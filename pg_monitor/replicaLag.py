#!/usr/bin/python

import sys
import checkStatus as st
import sql
import factors as fac
import hexa

# var=val;warn;crit;min;max
# check_mk output format 
# status 	item_name	perfdata	output


def getReplicaLags( param=None ) :
	item_name = 'POSTGRES_REPLICA_LAG'
	status = []
	perfdata = '-'
	output = ''
	if param != None :
		
		warning = int( param['warning'] )
		critical = int( param['critical'] )

                query = "SELECT pg_current_xlog_location() "
		
		master_host = param['host'][0]

		master = sql.getSQLResult ( {'host': master_host , 'port' : param['port'][0], 'dbname': param['dbname'], 'user' : param['user'] ,'password' : param['password'] } ,query ) 
		
		
		if master[0] == None :
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + str(master[1])

		counter = 1
		for rep_host in param['host'][1:] :
			replica = sql.getSQLResult ( {'host': rep_host , 'port' : param['port'][counter], 'dbname': param['dbname'] \
					, 'user' : param['user'] ,'password' : param['password'] } ,query )
			if replica[0] == 0 :
				wal_lag = hexa.computeMegaByteDiff ( master[1] , replica[1] ) / 16
			elif replica[0] == None :
				wal_lag = -1 
			if perfdata == '-' :
				perfdata = rep_host + '=' + str(wal_lag) + ';' +  str(warning) + ';' + str(critical) 
				output =  'replica on {0:s} lags behind master {1:s} by a total of {2:s} WALs. NOTE: a -1 lag value means the replica is not available !!! '\
					  .format( rep_host , master_host , str(wal_lag) )
			elif perfdata != '-'  :
				perfdata = perfdata + '|' + rep_host + '=' + str(wal_lag) + ';' +  str(warning) + ';' + str(critical)
				output =  output + ';replica on {0:s} lags behind master {1:s} by a total of {2:s} WALs. NOTE: a -1 lag value means the replica is not available !!!'\
						.format( rep_host , master_host , str(wal_lag) )
			if wal_lag != -1 :
				status.append( st.getStatus( wal_lag , warning , critical ) )
			elif wal_lag == -1 :
				status.append(2)
			counter += 1

		status.sort(reverse=True)
		return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
				



## testing the function 
#if __name__ == '__main__' :
#	print ( getReplicaLags( {'host' : ['localhost','localhost'], 'port' : ['5432','5432'] ,'user' : 'postgres' , 'password' : '',\
#                        'warning' : '3'  , 'critical' : '4'  } )  ) 


