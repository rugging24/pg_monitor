#!/usr/bin/python

import sys
import checkStatus as st
import sql
import math 

# var=val;warn;crit;min;max
# check_mk output format 
# status 	item_name	perfdata	output

def getLimits( limit, total ) :
	if limit != None :
		pLimit = limit.split('or')
		nperc = 0
		wperc = 0
		for ele in pLimit :
			if ele.find('%') == -1 :
				nperc = int( ele.replace(' ','') )
			elif ele.find('%') != -1 :
				wperc = math.ceil( ( float ( ele.replace('%','').replace(' ','') ) / 100 ) * total )
		
		return int (max( nperc, wperc ))


def getBackends( param=None ) :
	item_name = 'POSTGRES_BACKENDS'
	status = []
	perfdata = '-'
	output = ''
	if param != None :
                query = "SELECT \
			      datname, \
                              ( current_setting('max_connections')::int - current_setting('superuser_reserved_connections')::int ) as max_allowed_connect,\
                              coalesce( nullif((numbackends -1 ),-1), 0 ) as connect_count,\
                              ( coalesce( nullif((numbackends -1 ),-1), 0 ) * 100 ) / current_setting('max_connections')::int as percent_connect \
                         FROM \
                              pg_stat_database \
			 WHERE datname <> 'template0' AND datname <> 'template1'"
				
		rows = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query ) 
		connect_sum = 0
		max_connect = rows[0][1]
		warning = getLimits(  param['warning'] , max_connect )
		critical = getLimits(  param['critical'] , max_connect )
		for row in rows :
			if perfdata == '-' :
				perfdata = row[0] + '=' + str(row[2]) + ';' +  str(warning) + ';' + str(critical) + ';' + '0' + ';' + str(row[1]) 
				output =  '{0:s} has {1:d}% of the total connections used'.format(row[0],row[3])
			elif perfdata != '-'  :
				perfdata = perfdata + '|' + row[0] + '=' + str(row[2]) + ';' +  str(warning) + ';' + str(critical) + ';' + '0' + ';' + str(row[1])
				output =  output + ';{0:s} has {1:d}% of the total connections used'.format(row[0],row[3])
			connect_sum += int(row[2])
	
		
		status.append( st.getStatus( int(connect_sum),int(warning) , int(critical), int('0') , int(max_connect)  ) )

		status.sort( reverse=True )
		return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
	else :
		return None
## testing the function 
if __name__ == '__main__' :
	print ( getBackends( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '30'  , 'critical' : '45%'  } )  ) 


#	print ( getBackends( {'warning' : {'postgres' :0, 'gitlab' :10,'pgbench' : 0,'results' :10} , 'critical' : {'postgres' :0, 'gitlab' :10,'pgbench' : 0,'results' :10} , 'host' : {'postgres' :'localhost', 'gitlab' :'localhost','pgbench' : 'localhost','results' : 'localhost'},'dbname' : ['postgres', 'gitlab','pgbench', 'results'] , 'user' : {'postgres' :'postgres', 'gitlab' :'postgres','pgbench' : 'postgres','results' : 'postgres'} , 'password' : {'postgres' :'', 'gitlab' :'','pgbench' : '','results' : ''} }  ) )
