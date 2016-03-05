#!/usr/bin/python 

# list of valid actions 
# backends 
#connections
# wals
# autovacuum
# vacuum
# autoanalyze 
# analyze 
# tale_bloat 
# index_bloat 
# table_size
# index_size 
# database_size 
# nonblocking
# blocking
# checkpoints 
# duplicate_indexes
# replica_lag

import factors as fac


def getDefaults (check , warning , critical ) :
	if check == 'backends' : 
		# only whole digits and percentages allowed, an or separator is also allowed 
		return fac.getNumberPercentMix (warning, critical, '80%', '85%' )
	elif check == 'connections' :
                return {'warning':'dummy', 'critical' :'dummy'}
	else :
		if warning != None or critical != None :
			warn = warning 
			crit = critical if critical != None else 0			


                        if crit != 0 and warning == None :
                        	warn = warning if warning != None else crit
			

			if check == 'wals' :
				# -- warning and/or critical must be supplied
				if str(warn).isdigit() and str(crit).isdigit()  :
					return {'warning' : warn , 'critical' : crit}
				else :
					return None  
			elif check == 'autovacuum' or check == 'vacuum' or check == 'autoanalyze' or check == 'analyze':
				# -- warning = 1 month
				if crit == 0 :
					crit = '0min'
				return fac.getTimeDefaults (warn, crit , '1month')
			elif check == 'table_bloat' or check == 'index_bloat' :
				#  Warning and/or Critical must be provided
				return fac.warningAndOrCriticalProvided (warn,crit)
			elif check == 'table_size' or check == 'index_size' or check == 'database_size' :
				# warning and/or critical value must be supplied
				return fac.warningAndOrCriticalProvided (warn,crit) 
			elif check == 'nonblocking' or check == 'blocking' :
				# --warning = 2min
				# critical = 3min
				return fac.getTimeDefaults (warn, crit , '1min', '2mins') 
			elif check == 'checkpoints' :
				# warning and/or critical value must be supplied
				return None
			elif check == 'replica_lag' :
				# -- warning = 5 wal files
				# -- critical = 10 wal files 
				return fac.getNumberPercentMix (warn, crit, '5', '10' ) 
		else :
			return None 
