#!/usr/bin/python
import sys
sys.path.append('..')

import etl

sugarcrm_conn=etl.connector.sugarcrm_connector('admin','sugarpasswd',url='http://192.168.0.7/sugarcrm/soap.php')
sugarcrm_in1= etl.component.input.sugarcrm_in(sugarcrm_conn,'Contacts')

log=etl.component.transform.logger(name='After map')




tran=etl.transition(sugarcrm_in1,log,channel_source='Contacts')

job1=etl.job([sugarcrm_in1,log])
job1.run()
print job1.get_statitic_info()
#
## sugarcrm -> logger
##facebook -> mapping -> schema_valodator   -> openobject_out ('main')
##                                          -> logger1 ('invalid_field')
##                                                               -> logger2 invalid_name
##                                                               -> logger3 invalid_key
#                                                               -> logger4 invalid_null
#                                                               -> logger5 invalid_type
#                                                               -> logger6 invalid_size
#                                                               -> logger7 invalid_format












