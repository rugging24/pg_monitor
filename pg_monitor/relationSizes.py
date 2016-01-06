#!/usr/bin/python

import sql
import checkStatus as st
import factors as fac

def getQuery ( check, d0,d1,d2,d3 ) :
	query = ''
	if check == 'table_size' :
		query = "SELECT \
                              schemaname || '.' || relname, \
                              (pg_table_size(schemaname || '.' || relname) / {0:d}) as warn_size,\
			      (pg_table_size(schemaname || '.' || relname) / {1:d}) as crit_size,\
			      (pg_table_size(schemaname || '.' || relname) / 1024 )::double precision as display_size\
                         FROM \
                             pg_stat_user_tables\
                         WHERE \
                            ( pg_table_size(schemaname || '.' || relname) / {2:d} ) >= {3:d} ".format(int(d0) , int(d1) ,int(d2), int(d3) )
	elif check == 'index_size' :
		query = "SELECT \
	                       schemaname || '.' || relname || '.' || indexrelname, \
		               (pg_indexes_size(schemaname || '.' || indexrelname) / {0:d}) as warn_size,\
			       (pg_indexes_size(schemaname || '.' || indexrelname) / {1:d})  as crit_size,\
                               (pg_indexes_size(schemaname || '.' || indexrelname) / 1024 )::double precision  as display_size\
			FROM \
	                       pg_stat_user_indexes \
                        WHERE \
        	             ( pg_indexes_size(schemaname || '.' || indexrelname) / {2:d} ) >= {3:d}".format(int(d0) , int(d1) ,int(d2), int(d3) )
	elif check == 'database_size' :
		query = "SELECT \
	                      datname, (pg_database_size(datname) / {0:d} ) as warn_size, \
			      (pg_database_size(datname) / {1:d})  as crit_size, \
			      (pg_database_size(datname) / 1024 )::double precision  as display_size \
                         FROM \
	                      pg_database \
                         WHERE \
	                      datistemplate IS FALSE \
                         AND \
	                      ( pg_database_size(datname) / {2:d} ) >= {3:d}".format(int(d0) , int(d1) ,int(d2), int(d3) )

	return query 

def getRelationSizes( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = 'OK'
        if param != None :
		warning = fac.getSizeFactor( param['warning'] )
		critical = fac.getSizeFactor( param['critical'] )
		item_name = item_name + str(param['check']).upper()
                query = getQuery ( param['check'],warning[1],critical[1],warning[1] ,warning[0] ) 
                results = sql.getSQLResult ( {'host': param['host'][0] , 'port' : param['port'][0], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )
		
		if results[0] == None : 
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + results[1]

		rows = results[1]

		if len(rows) > 0 :
                	for row in rows :
				out_unit = ''
				if int(row[2]) >= int(critical[0]) :
					status.append(2)
					out_unit = [row[2] , critical[2] ]
				elif int(row[1]) >= int(warning[0]) :
					status.append(1)
					out_unit = [ row[1], warning[2] ]
                        	if perfdata == '-' :
                                	perfdata = row[0] + '=' + str(row[3]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                                	output =  '{0:s} is {1:d} {2:s} big'.format(row[0],out_unit[0],out_unit[1])
                        	elif perfdata != '-'  :
                                	perfdata = perfdata + '|' + row[0] + '=' + str(row[3]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                                	output =  output + ';{0:s} is {1:d} {2:s} big'.format(row[0],out_unit[0],out_unit[1])
			status.sort( reverse=True )
			return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
		elif len(rows) == 0 :
                	status.append(0)
                	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output

## testing the function 
#if __name__ == '__main__' :
#        print ( getRelationSizes( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
#                         'warning' : '3k'  , 'critical' : '5m'  , 'check' : 'table_size' } )  )

