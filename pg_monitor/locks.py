#!/usr/bin/python

import sql
import factors as fac
import checkStatus as st

def getVersionParam (version) :
        query = ''
        pid = ''
        if version >= 9.2 :
                query = 'query'
                pid = 'pid'
        elif version <= 9.1 :
                query = 'current_query'
                pid = 'procpid'

	return [query, pid]

def getNonBlockingVersionQuery (version,w1,w2) :
	query , pid = getVersionParam (version) 
	return "SELECT \
			l.relation::regclass::text as table_name ,\
			l.locktype,\
			pa.{0:s},\
			pa.{1:s}, \
			pa.usename ,\
			pa.client_addr,\
                        date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 running_time \
                FROM \
			 pg_catalog.pg_locks l \
                join pg_catalog.pg_stat_user_tables ut on ut.schemaname || '.' || ut.relname = l.relation::regclass::text \
                join pg_catalog.pg_database db on db.oid = l.database \
                join pg_catalog.pg_stat_activity pa on  l.pid = pa.{0:s} \
                where l.granted and lower(l.mode) = any ( \
                         values(lower('ExclusiveLock')),(lower('AccessExclusiveLock')), (lower('ShareLock')) , (lower('RowExclusiveLock')) , \
                         (lower('RowShareLock'))  ) \
                         And date_part('epoch',now()::timestamp - pa.query_start::timestamp)/60 >= ( {2:d} * {3:d} ) ".format(pid,query, int(w1), int(w2) ) 

def getBlockingVersionQuery (version) :
	query , pid = getVersionParam (version)
	return "SELECT \
			a.{0:s}	 	AS blocked_statement, \
			ka.{0:s}	AS blocking_statement,\
                        kl.locktype     AS blocking_type, \
                        bl.locktype     AS blocked_type, \
                        ka.usename      AS blocking_user, \
                        kl.pid		AS blocking_pid, \
                        date_part('epoch',clock_timestamp()::timestamp - ka.query_start::timestamp) blocking_time, \
                        bl.pid          AS blocked_pid, \
                        a.usename       AS blocked_user, \
                        date_part('epoch',clock_timestamp()::timestamp - a.query_start::timestamp)  waiting_time \
  		FROM  \
			pg_catalog.pg_locks         bl \
   		JOIN pg_catalog.pg_stat_activity a  ON a.{1:s} = bl.pid \
   		JOIN pg_catalog.pg_locks         kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid \
   		JOIN pg_catalog.pg_stat_activity ka ON ka.{1:s} = kl.pid \
  		WHERE NOT bl.GRANTED;".format( query , pid)

def getBlockingIterator(rows,item_name,findText) :
        perfdata = '-'
        output = ''
        for row in rows :
                if perfdata == '-' :
                        perfdata = row[0] + '=' + str(row[5]) + ';' +  str('1') + ';' + str('1')
                        output =  '{0:s}({1:s}) has been blocked({2:s}) by {3:s}({4:s}) for {5:d} \n Blocked Query : \n {6:s} \
                                   \n Blocking Query : \n {7:s }'.format(row[8], row[7], row[2], row[4], row[5],row[9], row[0], row[1]  )
                elif perfdata != '-'  :
                        perfdata = perfdata + '|' + row[0] + '=' + str(row[5]) + ';' +  str('1') + ';' + str('1')
			output =  output + ';{0:s}({1:s}) has been blocked({2:s}) by {3:s}({4:s}) for {5:d} \n Blocked Query : \n {6:s} \
                                   \n Blocking Query : \n {7:s }'.format(row[8], row[7], row[2], row[4], row[5],row[9], row[0], row[1]  )

		for txt in findText :
			if str(row[0]).find(txt) != -1 :
				status.append(2)
			else :
				status.append(1)
        status.sort( reverse=True )
        return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output


def getNonBlockingIterator(rows,item_name,warning,critical) :
	perfdata = '-'
	output = ''
	for row in rows :
		if perfdata == '-' :
                	perfdata = row[0] + '=' + str(row[5]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                        output =  '{0:s} has been locked({1:s}) by {2:s}({3:s}) for {4:d} \n Locking Query : {5:s}'.format(row[0],row[1],row[4],row[2],int(row[6]), row[3]  )
                elif perfdata != '-'  :
                	perfdata = perfdata + '|' + row[0] + '=' + str(row[5]) + ';' +  str(warning[0]) + ';' + str(critical[0])
                        output =  output + ';{0:s} has been locked({1:s}) by {2:s}({3:s}) for {4:d} \n Locking Query : {5:s}'.format(row[0],row[1],row[4],row[2],int(row[6]), row[3]  )
		status.append( st.getStatus( row[6],int(warning[0]) , int(critical[0])  ) )
	status.sort( reverse=True )
	return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output

def getLocks( param=None ) :
        item_name = 'POSTGRES_'
        status = []
        perfdata = '-'
        output = ''
        if param != None :
		check = (param['check']).lower()
		findText = param['find']
		item_name = item_name + check.upper() + '_LOCKS'
		
		host = param['host'][0]
		port = param['port'][0]

		query = "SELECT substring(version() FROM '(\d.\d)')::double precision"
                results = sql.getSQLResult ( {'host': host , 'port' : port, 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query )
		
		if results[0] == None :
                        return '2' + ' ' + item_name + ' ' + '-' + ' ' + results[1]
		

		version = (results[1])[0][0]
		
		warning = fac.getTimeFactor(  param['warning'] )
		critical = fac.getTimeFactor(  param['critical'] )
		
		results = ''

		if check == 'nonblocking' :
			results = sql.getSQLResult ( {'host': host , 'port' : port , 'dbname': 'postgres',\
				 'user' : param['user'] ,'password' : param['password'] } ,getNonBlockingVersionQuery(version,warning[0], warning[1])  )
		elif check == 'blocking' :
			results  = sql.getSQLResult ( {'host': host , 'port' : port , 'dbname': 'postgres',\
                                 'user' : param['user'] ,'password' : param['password'] } ,getBlockingVersionQuery(version)  )
		
		if results[0] == None :
			return '2' + ' ' + item_name + ' ' + '-' + ' ' + results[1]

		retval = []

		if len(results[1]) > 0 and check == 'nonblocking' : 	
			retval.append(getNonBlockingIterator(results[1],'POSTGRES_NONBLOCKING_LOCKS',warning,critical))
		elif len(results[1]) > 0 and check == 'blocking' :
			retval.append(getBlockingIterator(results[1],'POSTGRES_BLOCKING_LOCKS',findText))
		else :
			retval.append('0' + ' ' + item_name  + ' ' + '-' + ' ' + 'OK')

		if len(retval) > 0 :
			return retval[0]
	else :
		retval.append('0' + ' ' + item_name  + ' ' + '-' + ' ' + 'Invalid parameters passed to check')

		if len(retval) > 0 :
			return retval[0]
## testing the function 
#if __name__ == '__main__' :
#        print ( getLocks( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
#                         'warning' : '5min'  , 'critical' : '10min', 'check': 'blocking'   } )  )
# blocking
