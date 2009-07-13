#!/usr/bin/python

import sys
sys.path.append('..')

import etl

input_part = etl.component.input.data([
    {'id': 1, 'name': 'Fabien', 'country_id': 3},
    {'id': 2, 'name': 'Luc', 'country_id': 3},
    {'id': 3, 'name': 'Henry', 'country_id': 1}
])
input_cty = etl.component.input.data([
    {'id': 1, 'name': 'Belgium'},
    {'id': 3, 'name': 'France'}
])
map_keys = {'main': {
    'id': "main['id']",
    'name': "main['name'].upper()",
    'country': "country[main['country_id']]['name']"
}}
join_keys = {
         'country': 'id'
    }    

join=etl.component.transform.join(map_keys,join_keys)
log=etl.component.transform.logger(name='Read Partner File')

tran=etl.transition(input_part,join, channel_destination='main')
tran1=etl.transition(input_cty,join, channel_destination='country')
tran4=etl.transition(join,log)

job=etl.job([log])
job.run()

