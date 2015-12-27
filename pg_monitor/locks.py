#!/usr/bin/python

import sql
import factors as fac
import checkStatus as st

def getNonBlockingVersionQuery (version,w1,w2) :
	if version >= 9.2 :
		return "SELECT \
				l.relation::regclass::text as table_name ,l.locktype,pa.pid,pa.usename ,pa.client_addr,\
                                date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 running_time \
                        FROM \
				 pg_catalog.pg_locks l \
                        join pg_catalog.pg_stat_user_tables ut on ut.schemaname || '.' || ut.relname = l.relation::regclass::text \
                        join pg_catalog.pg_database db on db.oid = l.database \
                        join pg_catalog.pg_stat_activity pa on  l.pid = pa.pid \
                        where l.granted and lower(l.mode) = any ( \
                                values(lower('ExclusiveLock')),(lower('AccessExclusiveLock')), (lower('ShareLock')) , (lower('RowExclusiveLock')) , \
                                (lower('RowShareLock'))  ) \
                        And date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 >= ( {0:d} * {1:d} ) ".format( int(w1), int(w2) ) 
	elif version <= 9.1 : 
		return "SELECT \
				l.relation::regclass::text,l.locktype,pa.procpid,pa.usename ,pa.client_addr, \
                        	date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 running_time \
                        FROM \
				 pg_catalog.pg_locks l \
                        join pg_catalog.pg_stat_user_tables ut on ut.schemaname || '.' || ut.relname = l.relation::regclass::text \
                        join pg_catalog.pg_database db on db.oid = l.database \
                        join pg_catalog.pg_stat_activity pa on  l.pid = pa.procpid \
                        WHERE \
			l.granted and lower(l.mode) = any (values(lower('ExclusiveLock')),(lower('AccessExclusiveLock')), (lower('ShareLock')) , (lower('RowExclusiveLock')) , \
                        (lower('RowShareLock'))  ) \
                        and date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 >= ( {0:d} * {1:d} ) ".format( int(w1), int(w2) )

def getBlockingVersionQuery (version) :
	if version >= 9.2 :
		return "SELECT \
				a.query 	AS blocked_statement, \
                                kl.locktype     AS blocking_type, \
                                bl.locktype     AS blocked_type, \
                                ka.usename      AS blocking_user, \
                                kl.pid          AS blocking_pid, \
                                date_part('epoch',now()::timestamp - ka.query_start::timestamp)/60 blocking_time, \
                                bl.pid          AS blocked_pid, \
                                a.usename       AS blocked_user, \
                                date_part('epoch',now()::timestamp - a.query_start::timestamp)/60  waiting_time \
  			FROM  \
				pg_catalog.pg_locks         bl \
   			JOIN pg_catalog.pg_stat_activity a  ON a.pid = bl.pid \
   			JOIN pg_catalog.pg_locks         kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid \
   			JOIN pg_catalog.pg_stat_activity ka ON ka.pid = kl.pid \
  			WHERE NOT bl.GRANTED;"
	elif version <= 9.1 :
		return "SELECT \
				a.current_query AS blocked_statement, \
				kl.locktype     AS blocking_type, \
				bl.locktype     AS blocked_type, \
				ka.usename      AS blocking_user, \
				kl.pid          AS blocking_pid, \
				date_part('epoch',now()::timestamp - ka.query_start::timestamp)/60 blocking_time, \
				bl.pid          AS blocked_pid, \
         			a.usename       AS blocked_user, \
	 			date_part('epoch',now()::timestamp - a.query_start::timestamp)/60  waiting_time \
  			FROM  \
				pg_catalog.pg_locks         bl \
   			JOIN pg_catalog.pg_stat_activity a  ON a.procpid = bl.pid \
   			JOIN pg_catalog.pg_locks         kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid \
   			JOIN pg_catalog.pg_stat_activity ka ON ka.procpid = kl.pid \
  			WHERE NOT bl.GRANTED;"

def iterator(rows,item_name,warning,critical) :
	perfdata = '-'
	output = ''
	for row in rows :
		if perfdata == '-' :
                	perfdata = row[0] + '=' + str(row[5]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                        output =  '{0:s} has been locked({1:s}) by {2:s}({3:s}) for {4:d}'.format(row[0],row[1],row[3],row[4],int(row[5])  )
                elif perfdata != '-'  :
                	perfdata = perfdata + '|' + row[0] + '=' + str(row[5]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                        output =  output + ';{0:s} has been locked({1:s}) by {2:s}({3:s}) for {4:d}'.format(row[0],row[1],row[3],row[4],int(row[5])  )
		status.append( st.getStatus( row[5],int(warning[0]) , int(critical[0])  ) )
	status.sort( reverse=True )
	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output

def getLocks( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
		query = "SELECT substring(version() FROM '(\d.\d)')"
                ver = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )
		
		if ver == None :
                        return '2' + ' ' + 'POSTGRES_NONBLOCKING_LOCKS' + ' ' + '-' + ' ' + 'PostgreSQL Server is down !!!'
		

		version = ver[0][0]
		
		warning = fac.getTimeFactor(  param['warning'] )
		critical = fac.getTimeFactor(  param['critical'] )
		rows_noblocks = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres',\
				 'user' : param['user'] ,'password' : param['password'] } ,getNonBlockingVersionQuery(version,warning[0], warning[1])  )
		rows_blocking = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres',\
                                 'user' : param['user'] ,'password' : param['password'] } ,getBlockingVersionQuery(version)  )
		retval = []
		if rows_noblocking == None and rows_blocking == None : 
			return '2' + ' ' + 'POSTGRES_NONBLOCKING_LOCKS' + ' ' + '-' + ' ' + 'PostgreSQL Server is down !!!'

		if len(rows_noblocks) > 0 : 	
			retval.append(iterator(rows_noblocks,'POSTGRES_NONBLOCKING_LOCKS',warning,critical))
		elif len(rows_blocking) > 0 :
			retval.append(iterator(rows_blocking,'POSTGRES_BLOCKING_LOCKS',warning,critical))
		else :
			retval.append('0' + ' ' + 'POSTGRES_NONBLOCKING_LOCKS' + ' ' + '-' + ' ' + 'OK')
			retval.append('0' + ' ' + 'POSTGRES_BLOCKING_LOCKS' + ' ' + '-' + ' ' + 'OK')

		if len(retval) > 0 :
			return [val for val in retval]
	else :
		retval.append('0' + ' ' + 'POSTGRES_NONBLOCKING_LOCKS' + ' ' + '-' + ' ' + 'Invalid parameters passed to check')
		retval.append('0' + ' ' + 'POSTGRES_BLOCKING_LOCKS' + ' ' + '-' + ' ' + 'Invalid parameters passed to check')
		if len(retval) > 0 :
			return [val for val in retval]
## testing the function 
if __name__ == '__main__' :
        print ( getLocks( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '5min'  , 'critical' : '10min', 'ignoreNonBlocking': 1  } )  )

