#!/usr/bin/python 

### In practice, this file shouldn't exists, it should be done at the point where the parameters are 
## passed to the tool
def getPrepareParameters ( param=None ) :

                dbname = ['postgres']
                if param.get('dbname') != None :
                        dbname = param['dbname']
                factor = len( dbname )
                minval = [0] * int( factor )
                if param.get('minval') != None :
                        minval = param['minval'] * int( factor )
                host = param['host'].split(',') * int( factor )
                user = param['user'].split(',') * int( factor )
                password = param['password'].split(',') * int( factor )
                port = [5432] * int( factor )
                if param.get('port') != None :
                        port = param['port'] * int( factor )
                # set warning and critical values to minval and maxvals if they are not givwen
                warn = minval
                crit = [0]* int( factor )
                if param.get('warning') != None :
                        warn = param['warning'] * int( factor )
                if param.get('critical') != None :
                        crit = param['critical'] * int( factor )
