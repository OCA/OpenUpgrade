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
    'country': "country_var[main['country_id']]['name']"
}}
def preprocess(self, channels):
    cdict = {}
    for trans in channels['country']:
        for d in trans:
            cdict[d['id']] = d
    return {'country_var': cdict}

map=etl.component.transform.map(map_keys,preprocess)
log=etl.component.transform.logger(name='Read Partner File')

tran=etl.transition(input_part,map, channel_destination='main')
tran1=etl.transition(input_cty,map, channel_destination='country')
tran4=etl.transition(map,log)

job=etl.job([log])
job.run()

