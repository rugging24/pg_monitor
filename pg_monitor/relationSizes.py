#!/usr/bin/python

import sql

def getRelationSizes( param=None ) :
        item_name = 'POSTGRES_BACKENDS'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
                query = "SELECT \
		              schemaname || '.' || relname, pg_relation_size(schemaname || '.' || relname)\
			 FROM \
		             pg_stat_user_tables\
			 WHERE \
			     pg_relation_size(schemaname || '.' || relname) >= {0:d} ".format(warning)
			

		warning = getDen(  param['warning'] , max_connect )
		critical = getLimits(  param['critical'] , max_connect )
                rows = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )
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
        print ( getRelationSizes( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '30K'  , 'critical' : '45K'  } )  )

