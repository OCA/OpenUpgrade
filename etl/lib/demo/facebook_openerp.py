#!/usr/bin/python
import etl

from etl.component import component
from etl.connector import connector
from datetime import datetime

#To do :
#       1. get_friends with all necessary fields and its addresses = done
#       2. events , notes = continue
#       3. add hometown_location(type=other) as like current_location = done
#       4. crm.case check and put data in event.event also...

facebook_conn=etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')

facebook_in_friends= etl.component.input.facebook_in(facebook_conn,'get_friends',fields=['name','first_name','birthday','current_location','hometown_location'])
facebook_in_events= etl.component.input.facebook_in(facebook_conn,'get_user_events')
log1=etl.component.transform.logger(name='After write')
log=etl.component.transform.logger(name='After map')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='partner_')",
    'address_id': "tools.uniq_id(main.get('first_name', 'anonymous'), prefix='contact_')",
    'name': "main.get('name',['anonymous'])",
    'contact_name': "main.get('first_name','anonymous')",

    # Address type = contact
    'city': "main.get('current_location',False) and main['current_location'].get('city',False) or ''",
    'state_id': "main.get('current_location',False) and main['current_location'].get('state','') or ''",
    'zip': "main.get('current_location',False) and main['current_location'].get('zip','') or ''",
    'country_id': "main.get('current_location',False) and main['current_location'].get('country','') or ''",
    'type': " 'contact' ",
    # Address type = other
    'home_address_id': "tools.uniq_id(main.get('first_name', 'anonymous'), prefix='other_')",
    'home_city': "main.get('hometown_location',False) and main['hometown_location'].get('city',False) or ''",
    'home_state_id': "main.get('hometown_location',False) and main['hometown_location'].get('state','') or ''",
    'home_zip': "main.get('hometown_location',False) and main['hometown_location'].get('zip','') or ''",
    'home_country_id': "main.get('hometown_location',False) and main['hometown_location'].get('country','') or ''",
    'home_type': " 'other'",
}})

map1 = etl.component.transform.map({'main':{
    'event_id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='event_')",
    'event_name': "main.get('name',['anonymous'])",
    'type': "'Seminar'",
    'partner_id': "main.get('user_name','') or '' ",

}})

#map2 = etl.component.transform.map({'main':{
 #   'event_id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='event_')",
  #  'event_name': "main.get('name',['anonymous'])",
   # 'section_id': "'Events'",
    #'date_begin':'''datetime.fromtimestamp("main.get('start_time')").strftime("%Y-%m-%d %H:%M:%S")''',
    #'date_end':'''datetime.fromtimestamp("main.get('end_time')").strftime("%Y-%m-%d %H:%M:%S")''',
    #'partner_id': "main.get('user_name','') or '' ",
    #'product_id': "[PC1] Basic PC"

#}})

ooconnector = etl.connector.openobject_connector('http://mra.tinyerp.co.in:8069', 'crm_test_facebook', 'admin', 'admin', con_type='xmlrpc')
oo_out_partner= etl.component.output.openobject_out(
     ooconnector,
     'res.partner',
     {'id':'id','name':'name'}
            )

oo_out_address= etl.component.output.openobject_out(
     ooconnector,
     'res.partner.address',
     {'name': 'contact_name', 'id':'address_id', 'partner_id:id':'id','city':'city','state_id':'state_id','zip':'zip','country_id':'country_id', 'type':'type'
        })

oo_out_address1= etl.component.output.openobject_out(
     ooconnector,
     'res.partner.address',
     {'name': 'contact_name', 'id':'home_address_id', 'partner_id:id':'id','city':'home_city','state_id':'home_state_id','zip':'home_zip','country_id':'home_country_id', 'type':'home_type'
        })

oo_out_event= etl.component.output.openobject_out(
     ooconnector,
     'crm.case',
     { 'id': 'event_id', 'name':'event_name', 'section_id':'section_id', 'partner_id':'partner_id'
        })

#oo_out_event1= etl.component.output.openobject_out(
 #    ooconnector,
  #   'event.event',
   #  { 'id': 'event_id', 'name':'event_name', 'section_id':'section_id', 'date_begin':'date_begin', 'date_end':'date_end', 'product_id':'product_id'
    #    })

tran=etl.transition(facebook_in_friends, map)
tran=etl.transition(facebook_in_events, map1)
#tran=etl.transition(facebook_in_events, map2)
#,channel_source='friends'
tran=etl.transition(facebook_in_friends, log)
tran=etl.transition(map, oo_out_partner)
tran=etl.transition(map, oo_out_address)
tran=etl.transition(map, oo_out_address1)
tran=etl.transition(map1, oo_out_event)
#tran=etl.transition(map1, oo_out_event1)
tran=etl.transition(oo_out_address,log1)
job1=etl.job([facebook_in_friends,facebook_in_events,map,map1,log1,oo_out_partner, oo_out_address, oo_out_address1, oo_out_event, log])
print job1
job1.run()
#print job1.get_statitic_info()
