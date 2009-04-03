#!/usr/bin/python
import etl

from etl.component import component
from etl.connector import connector

#facebook_conn=etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')
ooconnector = etl.connector.openobject_connector('http://mra.tinyerp.co.in:8069', 'test', 'admin', 'admin', con_type='xmlrpc')


facebook_conn=etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')

facebook_out_friends= etl.component.output.facebook_out(facebook_conn,'set_events',fields=['name'])

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='partner1_')",
    'name': " 'ERPOPEM'",
}})

oo_in_partner= etl.component.input.openobject_in(
     ooconnector,
     'res.partner',
      fields = ['id','name']
    # {'id':'id','name':'name'}
            )

tran=etl.transition(oo_in_partner, map)
tran=etl.transition(map, facebook_out_friends)
job1=etl.job([facebook_out_friends])
job1.run()

