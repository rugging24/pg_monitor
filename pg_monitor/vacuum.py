#!/usr/bin/python

import sql 

def getFactor ( check_val ) :
        factor = 0
        val = ''
        unit = ''
        if check_val.lower().endswith('min') == True :
                factor = 1
                val = check_val.lower().replace('min','')
                unit = 'min'
        elif check_val.lower().endswith('hr') == True :
                factor = 60
                val = check_val.lower().replace('hr','')
                unit = 'hr'
        elif check_val.lower().endswith('day') == True or check_val.lower().endswith('days') == True :
                factor = 24*60
                val = check_val.lower().replace('day','').replace('s','')
                unit = 'day'
        elif check_val.lower().endswith('wk') == True :
                factor = 60 * 24 * 7
                val = check_val.lower().replace('wk','')
                unit = 'wk'
        elif check_val.lower().endswith('yr') == True or check_val.lower().endswith('yrs') == True:
                factor = 60 * 24 * 7 * 52
                val = check_val.lower().replace('yr','').replace('s','')
                unit = 'yr'

        return [val , factor, unit]


def getReturnIndex(check) :
	if check.lower() == 'vacuum' :
		return 1
	elif check.lower() == 'autovacuum' :
		return 2
	elif check.lower() == 'analyze' :
		return 3 
	elif check.lower() == 'autoanalyze' :
		return 4

def getVacuums( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
		check = param['check']
		item_name = item_name + check.upper()
		warning = getFactor( param['warning'])
		critical = getFactor( param['critical']) 
                query = "SELECT \
                              (schemaname || '.' || relname) table_name, \
                              date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_vacuum) / 60 last_vacuum_interval,\
                              date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_autovacuum) /60 last_autovacuum_interval,\
                              date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_analyze) /60 last_analyze_interval, \
                              date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_autoanalyze) /60 last_autoanalyze_interval \
                         FROM \
                             pg_stat_user_tables \
                         WHERE \
                             date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_vacuum)/60  >=  ( {0:d} * {1:d} ) OR \
                             date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_autovacuum)/60 >=  ( {0:d} * {1:d} ) OR \
                             date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_analyze)/60 >=  ( {0:d} * {1:d} ) OR  \
                             date_part('epoch',clock_timestamp() - pg_stat_user_tables.last_autoanalyze)/60 >= ( {0:d} * {1:d} ) ".format( int(warning[0]) , int(warning[1]) )


                rows = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )
		if len(rows) > 0 :
                	for row in rows :
				index =  getReturnIndex(check) 
                                out_unit = ''
				if row[index] != None :
                        		if int(row[index]) >= int(critical[0]) * int(critical[1]) :
                        			status.append(2)
                                		out_unit = [critical[1] , str(critical[2]) + ' ago ' ]
                        		elif int(row[index]) >= int(warning[0]) * int(warning[1]):
                        			status.append(1)
                                		out_unit = [ warning[1], str(warning[2]) + ' ago ' ]
					div = str( int(row[index]) / int(out_unit[0]) )
				else : 
					status.append(2)
                                        div = 'Never'
					out_unit = [critical[1] , str(critical[2]) + '  ' + check ]

                        	if perfdata == '-' :
                                	perfdata = row[0] + '=' + str(row[index]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                                	output =  '{0:s} last {1:s} time was {2:s} {3:s} '.format(row[0],check,div,out_unit[1])
                        	elif perfdata != '-'  :
                                	perfdata = perfdata + '|' + row[0] + '=' + str(row[index]) + ';' +  str(warning[0]) + ';' + str(critical[0]) 
                                	output =  output + '; {0:s} last {1:s} time was {2:s} {3:s}'.format(row[0],check,div,out_unit[1])
	        	status.sort( reverse=True )
                	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output 
		else :
			return str('0') + ' ' + item_name + ' ' + '-'  + ' ' + 'OK'
        else :
                return 2 + ' ' + 'POSTGRES_VACUUM_CHECKS' + ' ' + '-' + 'Invalid parameters passed to check'
## testing the function 
if __name__ == '__main__' :
        print ( getVacuums( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '2days'  , 'critical' : '4days', 'check' : 'autoanalyze'  } )  )
