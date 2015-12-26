#!/usr/bin/python

def getBackends( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
		query = "select  l.relation::regclass::text,l.locktype,pa.procpid,pa.usename ,pa.client_addr,
date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 running_time
from pg_catalog.pg_locks l
join pg_catalog.pg_stat_user_tables ut on ut.schemaname || '.' || ut.relname = l.relation::regclass::text
join pg_catalog.pg_database db on db.oid = l.database
join pg_catalog.pg_stat_activity pa on  l.pid = pa.procpid
where l.granted and lower(l.mode) = any (values(lower('ExclusiveLock')),(lower('AccessExclusiveLock')), (lower('ShareLock')) , (lower('RowExclusiveLock')) ,
(lower('RowShareLock'))  )
and date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 >= 1.0 "

                query2 = "select  l.relation::regclass::text as table_name ,l.locktype,pa.pid,pa.usename ,pa.client_addr, 
				date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 running_time
				from pg_catalog.pg_locks l
			join pg_catalog.pg_stat_user_tables ut on ut.schemaname || '.' || ut.relname = l.relation::regclass::text
			join pg_catalog.pg_database db on db.oid = l.database
			join pg_catalog.pg_stat_activity pa on  l.pid = pa.pid
			where l.granted and lower(l.mode) = any (
				values(lower('ExclusiveLock')),(lower('AccessExclusiveLock')), (lower('ShareLock')) , (lower('RowExclusiveLock')) ,
				(lower('RowShareLock'))  )
			and date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 >= 1.0 "

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
                return 2 + ' ' + 'POSTGRES_BACKENDS' + ' ' + '-' + 'Invalid parameters passed to check'
## testing the function 
if __name__ == '__main__' :
        print ( getBackends( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '30'  , 'critical' : '45%'  } )  )

