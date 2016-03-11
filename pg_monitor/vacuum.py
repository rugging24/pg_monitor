#!/usr/bin/python

import sql 
import factors as fac
import perfdataText as perf
import checkStatus as st


def getReturnIndex(check) :
	if check.lower() == 'vacuum' :
		return [1,"pg_stat_user_tables.last_vacuum","pg_stat_user_tables.vacuum_count"]
	elif check.lower() == 'autovacuum' :
		return [1,"pg_stat_user_tables.last_autovacuum","pg_stat_user_tables.autovacuum_count" ]
	elif check.lower() == 'analyze' :
		return [1,"pg_stat_user_tables.last_analyze", "pg_stat_user_tables.analyze_count" ] 
	elif check.lower() == 'autoanalyze' :
		return [1,"pg_stat_user_tables.last_autoanalyze", "pg_stat_user_tables.autoanalyze_count"]


def getVacuums( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = ''
	warning = []
	critical = []
        if param != None :
		check = param['check']
		item_name = item_name + check.upper()
		index =  getReturnIndex(check)
		retval = fac.getTimeDefaults ( param.get('warning'), param.get('critical') )
		if retval != None :
			warning = retval.get('warning') 
			critical = retval.get('critical') 
		else  :
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + 'Invalid Parameters supplied !'	 

		query = "SELECT table_name,calculated_time FROM ( \
				SELECT (schemaname || '.' || relname) table_name,\
				CASE WHEN {0:s} IS NULL THEN  \
					date_part('epoch',clock_timestamp() - '1970-01-01 00:00:00'::timestamp ) /60  \
				ELSE \
					date_part('epoch',clock_timestamp() - {0:s} ) /60 \
				END AS calculated_time \
			FROM \
				pg_stat_user_tables \
				) foo  \
		 	WHERE \
				( calculated_time /60 )  >=  ( {1:d} * {2:d} ) \
                                ORDER BY calculated_time DESC LIMIT 10 ".format( index[1] , int(warning[0]) , int(warning[1]) )


                results = sql.getSQLResult ( {'host': param['host'][0] , 'port' : param['port'][0], 'dbname': param['dbname'], 'user' : param['user'] ,'password' : param['password'] } ,query )
		
		if results[0] == None : 
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + results[1]
	
		rows = results[1]


		if len(rows) > 0 :
                	for row in rows : 
				status.append( st.getStatus( int(row[index[0]]) , int(warning[0]) * int(warning[1]) , int(critical[0]) * int(critical[1]) )  ) 
				out_unit = str ( int(row[1]/(60*24)) ) + ' days ago ' 
                        	if perfdata == '-' :
                                	perfdata = perf.getPerfStm (row[0],str(row[index[0]]),str(warning[0]),str(critical[0]))
                                	output =  '{0:s} last {1:s} time was {2:s} '.format(row[0],check,out_unit)
                        	elif perfdata != '-'  :
                                	perfdata = perfdata + '|' + perf.getPerfStm (row[0],str(row[index[0]]),str(warning[0]),str(critical[0])) 
                                	output =  output + '; {0:s} last {1:s} time was {2:s}'.format(row[0],check,out_unit)
	        	status.sort( reverse=True )
                	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output 
		else :
			return str('0') + ' ' + item_name + ' ' + '-'  + ' ' + 'OK'
