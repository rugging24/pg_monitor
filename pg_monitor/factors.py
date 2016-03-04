#!/usr/bin/python

import math
import re

def getTimeFactor ( check_val ) :
        factor = 0
        val = re.findall(r'\d.+\d+', check_val.lower() )[0]
        unit = ''
        if check_val.lower().find('min') != -1  :
                factor = 1
                unit = 'min'
        elif check_val.lower().find('hr') != -1 :
                factor = 60
                unit = 'hr'
        elif check_val.lower().find('day') != -1 :
                factor = 24*60
                unit = 'day'
        elif check_val.lower().find('wk') != -1 :
                factor = 60 * 24 * 7
                unit = 'wk'
        elif check_val.lower().find('yr')  != -1 :
                factor = 60 * 24 * 7 * 52
                unit = 'yr'

	if str(val).isdigit() :
        	return [val , factor, unit]
	else :
		return None


def getSizeFactor ( check_val ) :
        factor = 0
        val = re.findall(r'\d.+\d+', check_val.lower() )[0]
        unit = ''
        if check_val.lower().find('k') != -1 :
                factor = 1024
                unit = 'KB'
        elif check_val.lower().find('m') != -1 :
                factor = 1024 * 1024
                unit = 'MB'
        elif check_val.lower().find('g') != -1  :
                factor = 1024 * 1024 * 1024
                unit = 'GB'
        elif check_val.lower().find('t') != -1 :
                factor = 1024 * 1024 * 1024 * 1024
                unit = 'TB'
        elif check_val.lower().find('p') != -1  :
                factor = 1024 * 1024 * 1024 * 1024 * 1024
                unit = 'PB'

	if str(val).isdigit() :
                return [val , factor, unit]
        else :
                return None


def getNumberPercentLimits( limit, total ) :
        if limit != None :
                pLimit = limit.split('or')
                nperc = []
		
                for ele in pLimit :
			val = re.findall(r'\d+',ele)
			val = math.ceil( ( float ( val ) / 100 ) * total )  if ele.find('%') != -1 else int ( val ) 
			nperc.append (val) 
                return int (max( nperc))



def checkDigit (check_val) :
	retval = []
	for e in check_val :
        	retval.append( re.findall(r'\d.+\d+', e ) )
        return False not in  [True for element in retval if element.isdigit()]

	

def getNumberPercentMix (warning=None, critical=None, defaultWarn=None, defaultCritical=None ) :
        retval = {}
        warn = warning   if warning != None else defaultWarn
        crit = critical  if critical != None else defaultCritical
        retval.update ({'warning' : warn})
        retval.update ({'critical' : crit})

        if checkDigit(warn.split('or'))  or  checkDigit(crit.split('or'))  : 
                return retval
        else :
                return None


def warningAndOrCriticalProvided (warning,critical) :
        # as an heuristic 
        # warning = 0.8 * critical
        if warning == None and critical != None :
                critical = getSizeFactor ( critical )
                if critical == None :
                        return None
                return {'warning' : None , 'critical' : str(critical[0]) + critical[2][0] }
        elif warning != None and critical == None :
                warning = getSizeFactor ( warning )
                if warning == None :
                        return None
                return {'warning' : str(warning[0]) + warning[2][0] ,  'critical' : None }
	elif warning != None and critical != None :
		critical = getSizeFactor ( critical )
		warning = getSizeFactor ( warning )
		if warning == None or critical == None :
			return None
		return {'warning' : str(warning[0]) + warning[2][0] ,  'critical' : str( critical[0] ) + critical[2][0] }
        else :
                return None



def getTimeDefaults (warning, critical , defaultWarning, defaultCritical) :
                warn = warning if warning != None else defaultWarning
                crit = critical if critical != None else defaultCritical
                warn = getTimeFactor( warn )
                crit = getTimeFactor( crit )
                retval = {}
                if warn != None and crit != None :
			# check for the larger of the 2
                        retval.update( {'warning' : str(warn[0]) + str(warn[2]) }  )
                        retval.update( {'critical' : str(crit[0]) + str(crit[2]) }  )
                        return retval
                else :
                        return None

