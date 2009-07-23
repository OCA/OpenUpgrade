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

import wizard
import pooler
from osv import osv,fields

_earth_form =  '''<?xml version="1.0"?>
<form string="Google Map/Earth">
    <separator string="Select path to store KML file" colspan="2"/>
    <newline/>
    <field name="name"/>
    <newline/>
    <field name="kml_file"/>
</form>'''

_earth_fields = {
        'name': {'string': 'KML File name', 'type': 'char', 'readonly': False , 'required': True},
        'kml_file': {'string': 'Save KML file', 'type': 'binary', 'required': True},
            }

def _create_kml(self, cr, uid, data, context={}):
    #Todo:
    #    1. should be work with different country cities currenly it takes strait path if cities are in differnt countries
    #    2. should be test for all cities (Shanghai -> Hongkong ) check to upper and lower possiblities to search
    #    3. packages needed : google.directions-0.3.tar.gz

    #Note: from google.directions import GoogleDirections : this package shuld be install in order to run the wizard
#    path = tools.config['addons_path']
#    fileName = path + '/google_earth/kml/route.kml'
    pool = pooler.get_pool(cr.dbname)
    kml = pool.get('stock.move').get_kml(cr, uid, mode=0, context=context)
    out = base64.encodestring(kml).encode('ascii', 'replace')
    fname = 'route' + '.kml'
    return {'kml_file': out, 'name': fname}

class delivery_route(wizard.interface):

    states = {
       'init': {
            'actions': [_create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                },
            }
delivery_route('google.find.route')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: