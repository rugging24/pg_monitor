#!/usr/bin/python

import sql 


def getBackends( param=None ) :
        item_name = 'POSTGRES_DUPLICATE_INDEXES'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
                query ="WITH index_cols_ord as ( \
    				SELECT attrelid, attnum, attname \
    				FROM pg_attribute \
        			JOIN pg_index ON indexrelid = attrelid \
    				WHERE indkey[0] > 0 \
    				ORDER BY attrelid, attnum \
			), \
				index_col_list AS ( \
    				SELECT attrelid, \
        			array_agg(attname) as cols \
    				FROM index_cols_ord \
    				GROUP BY attrelid \
			), \
			dup_natts AS ( \
				SELECT indrelid, indexrelid \
				FROM pg_index as ind \
				WHERE EXISTS ( SELECT 1 \
    				FROM pg_index as ind2 \
    				WHERE ind.indrelid = ind2.indrelid \
    				AND ( ind.indkey @> ind2.indkey \
     				OR ind.indkey <@ ind2.indkey ) \
    				AND ind.indkey[0] = ind2.indkey[0] \
    				AND ind.indkey <> ind2.indkey \
    				AND ind.indexrelid <> ind2.indexrelid \
			) ) \
			SELECT \
				userdex.schemaname  || '.' || userdex.relname || '.' || userdex.indexrelname as relname,\
				array_to_string(cols, ', ') as index_cols, \
				indexdef, \
				idx_scan as index_scans \
			FROM  \
				pg_stat_user_indexes as userdex \
    			JOIN index_col_list ON index_col_list.attrelid = userdex.indexrelid \
    			JOIN dup_natts ON userdex.indexrelid = dup_natts.indexrelid \
    			JOIN pg_indexes ON userdex.schemaname = pg_indexes.schemaname \
        			AND userdex.indexrelname = pg_indexes.indexname \
			ORDER BY userdex.schemaname, userdex.relname, cols, userdex.indexrelname ;" 

                results = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )
		if results[0] == None : 
			return '2' + ' ' + item_name + ' ' + '-' + ' ' + results[1]
		
		rows = results[1]

		if len(rows) > 0 :
                	for row in rows :
                        	if output == '' :
                                	output =  '{0:s} with cols {1:s} appears to be a duplicate Index'.format(row[0],row[1])
                        	elif output != ''  :
                                	output =  output + ';{0:s} with cols {1:s} appears to be a duplicate Index'.format(row[0],row[1])

			return '1' + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
		else :
			return '0' + ' ' + item_name + ' ' + '-' + ' ' + 'OK'

        else :
                return '2' + ' ' + 'POSTGRES_DUPLICATE_INDEXES' + ' ' + '-' + 'Invalid parameters passed to check'
## testing the function 
#if __name__ == '__main__' :
#        print ( getBackends( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
#                         'warning' : '30'  , 'critical' : '45%'  } )  )
