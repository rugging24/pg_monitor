#!/usr/bin/python

import sql 
import factors as fac


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
        if param != None :
		check = param['check']
		item_name = item_name + check.upper()
		operator = '='
		if param.get('ignoreNever') != None :
			if param['ignoreNever']  == 0 :
				operator = '>'
		index =  getReturnIndex(check)
		warning = fac.getTimeFactor( param['warning'])
		critical = fac.getTimeFactor( param['critical']) 
		query = "SELECT \
				(schemaname || '.' || relname) table_name,\
				CASE WHEN {0:s} IS NULL THEN  \
					NULL \
				ELSE \
					date_part('epoch',clock_timestamp() - {0:s} ) /60 \
				END \
			FROM \
				pg_stat_user_tables \
		 	WHERE \
				( date_part('epoch',clock_timestamp() - {0:s} ) /60  >=  ( {2:d} * {3:d} ) )  OR \
				( {1:s} {4:s}  0 ) ".format( index[1] ,index[2] , int(warning[0]) , int(warning[1]), operator )


                results = sql.getSQLResult ( {'host': param['host'][0] , 'port' : param['port'][0], 'dbname': param['dbname'], 'user' : param['user'] ,'password' : param['password'] } ,query )
		
		if results[0] == None : 
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + results[1]
	
		rows = results[1]

		if len(rows) > 0 :
                	for row in rows : 
                                out_unit = ''
				if row[index[0]] != None :
                        		if int(row[index[0]]) >= int(critical[0]) * int(critical[1]) :
                        			status.append(2)
                                		out_unit = [critical[1] , str(critical[2]) + ' ago ' ]
                        		elif int(row[index[0]]) >= int(warning[0]) * int(warning[1]):
                        			status.append(1)
                                		out_unit = [ warning[1], str(warning[2]) + ' ago ' ]
					else :
						status.append(0)
						out_unit = [ warning[1], str(warning[2]) + ' ago '  ]

					div = str (int (row[index[0]])/ int(out_unit[0]) )
				else : 
					status.append(2)
                                        div = 'Never'
					out_unit = [critical[1] , '  ' + check ]

                        	if perfdata == '-' :
                                	perfdata = row[0] + '=' + str(row[index[0]]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                                	output =  '{0:s} last {1:s} time was {2:s} {3:s} '.format(row[0],check,div,out_unit[1])
                        	elif perfdata != '-'  :
                                	perfdata = perfdata + '|' + row[0] + '=' + str(row[index[0]]) + ';' +  str(warning[0]) + ';' + str(critical[0]) 
                                	output =  output + '; {0:s} last {1:s} time was {2:s} {3:s}'.format(row[0],check,div,out_unit[1])
	        	status.sort( reverse=True )
                	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output 
		else :
			return str('0') + ' ' + item_name + ' ' + '-'  + ' ' + 'OK'
## testing the function 
#if __name__ == '__main__' :
#        print ( getVacuums( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
#                         'warning' : '2 days'  , 'critical' : '4days', 'check' : 'autovacuum','ignoreNever': 0 } )  )
