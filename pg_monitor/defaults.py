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
		return fac.getNumberPercentMix (warning, critical, '80%', '90%' )
	elif check == 'wals' :
		# -- warning 70%Max count
		# -- critical 80%Max count
		return fac.getNumberPercentMix (warning, critical, '70%', '80%' )
	elif check == 'autovacuum' or check == 'vacuum' or check == 'autoanalyze' or check == 'analyze':
		# -- warning = 1 week
		# -- critical = 2 weeks
		return fac.getTimeDefaults (warning, critical , '1wk', '2wks',0.8)
	elif check == 'table_bloat' or check == 'index_bloat' :
		#  Warning and/or Critical must be provided
		return fac.warningAndOrCriticalProvided (warning,critical,0.8)
	elif check == 'table_size' or check == 'index_size' or check == 'database_size' :
		# warning and/or critical value must be supplied
		return fac.warningAndOrCriticalProvided (warning,critical,0.5) 
	elif check == 'nonblocking' or check == 'blocking' :
		# --warning = 2min
		# critical = 3min
		return fac.getTimeDefaults (warning, critical , '1min', '2mins', 0.8) 
	elif check == 'checkpoints' :
		# warning and/or critical value must be supplied
		return None
	elif check == 'replica_lag' :
		# -- warning = 30 sec
		# -- critical = 1min
		return None 
