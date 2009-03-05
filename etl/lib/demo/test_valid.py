#!/usr/bin/python

import sys
sys.path.append('..')

import etl
from etl import transformer

fileconnector_partner=etl.connector.localfile('input/partner.csv')
trans=transformer( { 
       'id':transformer.LONG,   
       'name':transformer.STRING,     
       'tel':transformer.STRING,
       })


csv_in1= etl.component.input.csv_in(fileconnector=fileconnector_partner,name='Partner Data',transformer=trans)


schema= {
         'id':{'type':'long','key':True,'Is_Null':True},
         'name':{'type':'unicode','size':'20','Is_NULL':False},
         'tel':{'type':'unicode','Is_NULL':False},
         
      }
schema_valid=etl.component.transform.schema_validator(schema)
log1=etl.component.transform.logger(name='invalid_field')
log2=etl.component.transform.logger(name='invalid_name')
log3=etl.component.transform.logger(name='invalid_type')
log4=etl.component.transform.logger(name='invalid_key')
log5=etl.component.transform.logger(name='invalid_null')
log6=etl.component.transform.logger(name='invalid_size')
log7=etl.component.transform.logger(name='invalid_format')
log8=etl.component.transform.logger(name='main')


tran=etl.transition(csv_in1,schema_valid)
tran1=etl.transition(schema_valid,log1,channel_source='invalid_field')
tran2=etl.transition(schema_valid,log2,channel_source='invalid_name')
tran3=etl.transition(schema_valid,log3,channel_source='invalid_type')
tran4=etl.transition(schema_valid,log4,channel_source='invalid_key')
tran5=etl.transition(schema_valid,log5,channel_source='invalid_null')
tran6=etl.transition(schema_valid,log6,channel_source='invalid_size')
tran7=etl.transition(schema_valid,log7,channel_source='invalid_format')
tran8=etl.transition(schema_valid,log8,channel_source='main')


job1=etl.job([log1,log2,log3,log4,log5,log6,log7,log8])


job1.run()

