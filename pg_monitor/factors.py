#!/usr/bin/python

def getFactor ( check_val ) :
        factor = 0
        val = ''
        unit = ''
        if check_val.lower().endswith('min') == True or  check_val.lower().endswith('mins') == True :
                factor = 1
                val = check_val.lower().replace('min','').replace('s','').replace(' ','')
                unit = 'min'
        elif check_val.lower().endswith('hr') == True or check_val.lower().endswith('hrs') == True  :
                factor = 60
                val = check_val.lower().replace('hr','').replace('s','').replace(' ','')
                unit = 'hr'
        elif check_val.lower().endswith('day') == True or check_val.lower().endswith('days') == True :
                factor = 24*60
                val = check_val.lower().replace('day','').replace('s','').replace(' ','')
                unit = 'day'
        elif check_val.lower().endswith('wk') == True or check_val.lower().endswith('wks') == True :
                factor = 60 * 24 * 7
                val = check_val.lower().replace('wk','').replace('s','').replace(' ','')
                unit = 'wk'
        elif check_val.lower().endswith('yr') == True or check_val.lower().endswith('yrs') == True:
                factor = 60 * 24 * 7 * 52
                val = check_val.lower().replace('yr','').replace('s','').replace(' ','')
                unit = 'yr'

        return [val , factor, unit]
