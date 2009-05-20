#!/usr/bin/python
import threading
import sys
sys.path.append('..')

import etl

#this demo file shows how to design jobs when you want 
#to load data of many2many tables into OpenERP.

#Note that the csv files are the same as if you wished 
#to import them in a module.


#definition of the csv inputs
fileconnector_groups=etl.connector.localfile('input/res.groups.csv')
fileconnector_users=etl.connector.localfile('input/res.users.csv')
csv_in_groups= etl.component.input.csv_in(fileconnector_groups,name='Groups Data')
csv_in_users= etl.component.input.csv_in(fileconnector_users,name='Users Data')

#logger definition
log1=etl.component.transform.logger(name='Processed Data')

#definition of the openobject outputs
ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'etl', 'admin', 'admin', con_type='xmlrpc')
oo_out_groups = etl.component.output.openobject_out(
     ooconnector,
     'res.groups',
     {'id':'id','name':'name'}
            )
oo_out_users = etl.component.output.openobject_out(
     ooconnector,
     'res.users',
     {'id':'user_id','name':'user_name', 'login':'login','context_lang':'context_lang','groups_id:id':'groups_id:id'}
            )

#definition of the map component, for the user data
map_keys = {'main':{
    'user_id': "tools.uniq_id(main.get('login', 'anonymous'), prefix='user_')",
    'user_name': "main.get('name', 'anonymous')",
    'login': "main.get('login', 'anonymous')",
    'context_lang': "main.get('context_lang','en_US')",
    'groups_id:id': "main.get('groups_id:id','False')",
}}
map = etl.component.transform.map(map_keys)

#definition of the transitions
tran0=etl.transition(csv_in_groups, oo_out_groups)
tran1=etl.transition(csv_in_users, map)
tran2=etl.transition(map, oo_out_users)


job1=etl.job([oo_out_groups,oo_out_users])
#print job1
job1.run()
#print job1.get_statitic_info()
