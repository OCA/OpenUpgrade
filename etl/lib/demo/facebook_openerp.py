#!/usr/bin/python
import etl

from etl.component import component
from etl.connector import connector

#To do :
#       1. get_friends with all necessary fields and its addresses
#       2. events , notes...

facebook_conn=etl.connector.facebook_connector('modiinfo@gmail.com')
facebook_in1= etl.component.input.facebook_in(facebook_conn,'get_friends',fields=['name','first_name','birthday','current_location',])
log1=etl.component.transform.logger(name='After write')
log=etl.component.transform.logger(name='After map')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='partner_')",
    'address_id': "tools.uniq_id(main.get('first_name', 'anonymous'), prefix='contact_')",
    'name': "main.get('name',['anonymous'])",
    'contact_name': "main.get('first_name','anonymous')",
    'city': "main.get('current_location',False) and main['current_location'].get('city',False) or ''",
    'state_id': "main.get('current_location',False) and main['current_location'].get('state','') or ''",
    'zip': "main.get('current_location',False) and main['current_location'].get('zip','') or ''",
    'country_id': "main.get('current_location',False) and main['current_location'].get('country','') or ''",
}})

ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'db_name', 'admin', 'admin', con_type='xmlrpc')
oo_out= etl.component.output.openobject_out(
     ooconnector,
     'res.partner',
     {'id':'id','name':'name'}
)
oo_out2= etl.component.output.openobject_out(
     ooconnector,
     'res.partner.address',
     {'name': 'contact_name', 'id':'address_id', 'partner_id:id':'id','city':'city','state_id':'state_id','zip':'zip','country_id':'country_id'}
     )
tran=etl.transition(facebook_in1,map)#,channel_source='friends'
tran=etl.transition(facebook_in1,log)
tran=etl.transition(map,oo_out)
tran=etl.transition(map,oo_out2)
tran=etl.transition(oo_out2,log1)
job1=etl.job([log1,oo_out,oo_out2,log])
job1.run()
#facebook -> mapping -> schema_valodator   -> openobject_out ('main')
#                                          -> logger1 ('invalid_field')
#                                                               -> logger2 invalid_name
#                                                               -> logger3 invalid_key
#                                                               -> logger4 invalid_null
#                                                               -> logger5 invalid_type
#                                                               -> logger6 invalid_size
#                                                               -> logger7 invalid_format
