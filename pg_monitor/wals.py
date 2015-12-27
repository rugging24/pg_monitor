#!/usr/bin/python

import sql 
import checkStatus as st

def getWALs( param=None ) :
        item_name = 'POSTGRES_WALS'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
                query = "SELECT count(bar.*) wal_count , \
				ceil(( ( 2 + current_setting('checkpoint_completion_target')::double precision)* current_setting('checkpoint_segments')::double precision) + 1) max_wal \
			FROM \
			( \
				SELECT  (pg_stat_file('pg_xlog/' || foo.files )).* FROM \
					( SELECT pg_ls_dir('pg_xlog') files  ) foo \
				WHERE  (pg_stat_file('pg_xlog/' || foo.files )).isdir IS FALSE \
			) bar \
			WHERE bar.size >= 16777216" 

                rows = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )

		if rows == None : 
			return '2' + ' ' + item_name + ' ' + '-' + ' ' + 'PostgreSQL Server is down !!!'

                warning = int (param['warning'])
                critical = int(  param['critical'] )
		if len(rows) > 0 :
                	for row in rows :
                        	if perfdata == '-' :
                                	perfdata = 'WALS' + '=' + str(row[0]) + ';' +  str(warning) + ';' + str(critical) + ';' + '1' + ';' + str(row[1])
                                	output =  '{0:s} WAL file(s) found'.format( str(row[0]) )
	                	status.append( st.getStatus( row[0],int(warning) , int(critical), int('1') , int(row[1])  ) )

                	status.sort( reverse=True )
                	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
		else :
			return '2' + ' ' + item_name + ' ' + '-' + ' ' + 'No WAL file found, at least One WAL file should be present.'
        else :
                return '2' + ' ' + 'POSTGRES_WALS' + ' ' + '-' + ' ' + 'Invalid parameters passed to check'
## testing the function 
if __name__ == '__main__' :
        print ( getWALs( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '20'  , 'critical' : '30'  } )  )

