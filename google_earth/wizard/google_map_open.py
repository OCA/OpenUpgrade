# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from lxml import etree

import wizard
import pooler

_earth_form =  '''<?xml version="1.0"?>
<form string="Google Map/Earth" >
    <field name="path" colspan="4" height="30" width="450"/>
    <field name="map_model" />
</form>'''

_earth_fields = {
    'path': {'string': 'Path (URL)', 'type': 'char', 'readonly': False , 'default': lambda *x: 'http://maps.google.com/maps?q=http://yourserver.com:port/kml'
             , 'required': True, 'size':128, 'help':'URL for e.g: http://maps.google.com/maps?q=http://yourserver:port/kml/'},
    'map_model':{
        'string':"Map For",
        'type':'selection',
        'selection':[('partner','Partner'), ('partner-country','Partner-Country'), ('route','Delivery Route') ],
        'default': lambda *a:'partner',
                },
             }
def get_map_url(self, cr, uid, data, context={}):
    #http://maps.google.com/maps?q=http://jabber.tinyerp.co.in:8080/kml?model=res.partner%26mode=1
    if data['form']['map_model'] == 'partner':
        url_str = url = data['form']['path'] + '?model=res.partner'
    elif data['form']['map_model'] == 'partner-country':
        url_str = url = data['form']['path'] + '?model=res.country'
    elif data['form']['map_model'] == 'route':
        url_str = url = data['form']['path'] + '?model=stock.move'
    data['form']['url'] = url_str
    return {}

def _launch_map(self, cr, uid, data, context):
    return {
    'type': 'ir.actions.act_url',
    'url': data['form']['url'],
    'target': 'new'
    }

class google_map_open(wizard.interface):
    states = {
       'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end', 'Cancel'), ('launch','Open')]}
                },
      'launch': {
            'actions': [get_map_url],
            'result':{'type':'action', 'action': _launch_map, 'state':'end'}
                       }
            }
google_map_open('google.map.open')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: