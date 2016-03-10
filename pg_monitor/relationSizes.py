#!/usr/bin/python

import sql
import checkStatus as st
import factors as fac
import perfdataText as perf

def getQuery ( check ) :
	query = ''
	if check == 'table_size' :
		query = "SELECT \
                              schemaname || '.' || relname, \
			      (pg_table_size(schemaname || '.' || relname) / {0:d} ) as display_size\
                         FROM \
                             pg_stat_user_tables\
                         WHERE \
                            ( pg_table_size(schemaname || '.' || relname) / {0:d} ) >= {1:d} "
	elif check == 'index_size' :
		query = "SELECT \
	                       schemaname || '.' || relname || '.' || indexrelname, \
                               (pg_indexes_size(schemaname || '.' || indexrelname) / {0:d} )  as display_size\
			FROM \
	                       pg_stat_user_indexes \
                        WHERE \
        	             ( pg_indexes_size(schemaname || '.' || indexrelname) / {0:d} ) >= {1:d}"
	elif check == 'database_size' :
		query = "SELECT \
	                      datname, \
			      (pg_database_size(datname) / {0:d} ) as display_size \
                         FROM \
	                      pg_database \
                         WHERE \
	                      datistemplate IS FALSE \
                         AND \
	                      ( pg_database_size(datname) / {0:d} ) >= {1:d}"

	return query 

def getRelationSizes( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = 'OK'
	warning = []
	critical = []
        if param != None :
		retval = fac.warningAndOrCriticalProvided (param.get('warning'),param.get('critical')) 
		if retval != None :
			warning = retval.get('warning')
			critical = retval.get('critical')
		else :
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + 'Invalid parameters passed !'

		item_name = item_name + str(param['check']).upper()
                query = getQuery ( param['check']) 
		query = query.format( int(warning[1]),int(warning[0])  )
                results = sql.getSQLResult ( {'host': param['host'][0] , 'port' : param['port'][0], 'dbname': param['dbname'], 'user' : param['user'] ,'password' : param['password'] } ,query )
		
		if results[0] == None : 
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + results[1]

		rows = results[1]

		if len(rows) > 0 :
                	for row in rows :
				status.append( st.getStatus(row[1] , warning[0] , critical[0] )  )
                        	if perfdata == '-' :
                                	perfdata = perf.getPerfStm (row[0],row[1],warning[0],critical[0])
                                	output =  '{0:s} is {1:d} {2:s} big'.format(row[0],row[1],warning[2])
                        	elif perfdata != '-'  :
                                	perfdata = perfdata + '|' + perf.getPerfStm (row[0],row[1],warning[0],critical[0])
                                	output =  output + ';{0:s} is {1:d} {2:s} big'.format(row[0],row[1],warning[2])
			status.sort( reverse=True )
			return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
		else :
                	status.append(0)
                	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output

## testing the function 
#if __name__ == '__main__' :
#        print ( getRelationSizes( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
#                         'warning' : '3k'  , 'critical' : '5m'  , 'check' : 'table_size' } )  )

