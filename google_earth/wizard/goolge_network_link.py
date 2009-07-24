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
    <field name="path" colspan="4"/>
    <newline/>
    <field name="refresh_mode" />
    <field name="refresh_interval" />
    <field name="view_refresh_mode" />
    <field name="view_refresh_time" />
    <newline/>
    <separator string="Select option to make kml" colspan="4"/>
    <field name="partner_select" />
    <field name="country_select" />
    <field name="route_select"  />
</form>'''

_earth_fields = {
    'path': {'string': 'Path (URL)', 'type': 'char', 'readonly': False , 'default': lambda *x: 'http://yourserver.com:port/kml/'
             , 'required': True, 'size':64, 'help':'URL for e.g: http://yourserver:port/kml/'},
    'partner_select': {'string':'Partner', 'type': 'boolean', 'help':'KML with All Details of partners'},
    'country_select': {'string':'Country', 'type': 'boolean', 'help':'KML with All Details of partners and its country'},
    'route_select': {'string':'Delivery route', 'type': 'boolean', 'help':'Delivery route kml'},
    'refresh_mode':{
        'string':"RefreshMode",
        'type':'selection',
        'selection':[('onChange','onChange'),('onInterval','onInterval'),('onExpire','onExpire')],
        'default': lambda *a:'onInterval',
        'help': 'Specifies a time-based refresh mode'
    },
    'refresh_interval': {'string':'Refresh Interval', 'type': 'integer', 'default': lambda *a: 1, 'help':'Indicates to refresh the file every n seconds'},
    'view_refresh_mode':{
        'string':"ViewRefreshMode",
        'type':'selection',
        'selection':[('never','never'),('onStop','onStop'),('onRequest','onRequest'),('onRegion','onRegion')],
        'default': lambda *a:'onStop',
        'help': 'Specifies how the link is refreshed when the "camera" changes'
    },
    'view_refresh_time': {'string':'View Refresh Time', 'type': 'integer', 'default': lambda *a: 1, 'help': 'After camera movement stops, specifies the number of seconds to wait before refreshing the view'},
    }

_kml_form =  '''<?xml version="1.0"?>
<form string="Google Map/Earth">
    <separator string="Select path to store KML file" colspan="2"/>
    <newline/>
    <field name="name"/>
    <newline/>
    <field name="kml_file"/>
</form>'''

_kml_fields = {
        'name': {'string': 'KML File name', 'type': 'char', 'readonly': False , 'required': True},
        'kml_file': {'string': 'Save KML file', 'type': 'binary', 'required': True},
            }

_summary_form = '''<?xml version="1.0"?>
        <form string="Summary">
            <field name="summary" nolabel="1" height="200" width="300" />
        </form> '''

_summary_fields = {
            'summary': {'string': 'Summary', 'type': 'text', 'required': False, 'readonly': True,
                        'default': lambda *a: '''You can now upload this kml file on google Earth by Add/Networklink menu You will get refresh data (time specified in refresh interval), And you can also upload this kml to google map but refreshment of data might be not working google map'''},
        }

def _create_kml(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    models = []
    if data['form']['partner_select']:
        models.append('res.partner')
    if data['form']['country_select']:
        models.append('res.country')
    if data['form']['route_select']:
        models.append('stock.move')
    data['form']['models'] = models
    kml = pool.get('google.map').get_networklink_kml(cr, uid, data=data['form'], context=context)
    out = base64.encodestring(kml)
    fname = 'network' + '.kml'
    return {'kml_file': out, 'name': fname}

class google_network_kml(wizard.interface):
    states = {
       'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end', 'Cancel'), ('make','Generate KML')]}
                },
       'make': {
            'actions': [_create_kml],
            'result': {'type': 'form', 'arch':_kml_form, 'fields':_kml_fields,  'state':[('info','Ok')]}
                },
        'info': {
            'actions': [],
            'result': {'type': 'form', 'arch': _summary_form, 'fields': _summary_fields, 'state': [('end', 'Ok')]}
        }
            }
google_network_kml('google.network.link')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: