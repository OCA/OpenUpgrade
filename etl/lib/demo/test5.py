#!/usr/bin/python

import sys
sys.path.append('..')

import etl
from etl import transformer

openobject_partner=etl.connector.openobject_connector.openobject_connector('http://localhost:8069', 'dms_20090205', 'admin', 'admin',con_type='xmlrpc')

transformer_description= {'title':transformer.transformer.STRING,'name':transformer.transformer.STRING,'street':transformer.transformer.STRING,'street2':transformer.transformer.STRING,'birthdate':transformer.transformer.DATE}    
transformer=transformer.transformer(transformer_description)

openobject_in1= etl.component.input.openobject_in.openobject_in('Partner Data',
                 openobject_partner,'res.partner.address',
                 fields=['partner_id','title', 'name', 'street', 'street2' , 'phone' , 'city' ,  'zip' ,'state_id' , 'country_id' , 'mobile', 'birthdate'],
                 transformer=transformer)
map_criteria=[
        {'name':'country_id','map':"%(country_id)s and %(country_id)s[1].upper() or ''",'destination':'Country Name'},
        {'name':'state_id','map':"%(state_id)s and %(state_id)s[1].upper() or ''",'destination':'State Name'},
        {'name':'partner_id','map':"%(partner_id)s and %(partner_id)s[1] or ''",'destination':'Partner'},
        {'name':"name",'destination':'Address Name'}
        ]

data_map_component=etl.component.transform.data_map.data_map('my map',map_criteria,transformer=transformer)

filter_criteria=[
        {'name':'Partner','filter':'"%(Partner)s".lower() or ""','operator':'==','operand':"'leclerc'",'condition':'or'},     
        {'name':'Address Name','operator':'==','operand':"'Fabien Pinckaers'"}
        ]

data_filter_component=etl.component.transform.data_filter.data_filter('my filter',filter_criteria,transformer=transformer)

log1=etl.component.transform.logger.logger(name='Read Partner')

tran1=etl.transition.transition(openobject_in1,data_map_component)
tran2=etl.transition.transition(data_map_component,data_filter_component)
tran3=etl.transition.transition(data_filter_component,log1)

job1=etl.job.job('job1',[log1])
job1.run()

