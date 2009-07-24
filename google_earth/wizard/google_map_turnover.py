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
import cgi

import wizard
import pooler

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
def create_kml(self, cr, uid, data, context={}):
    # This wizard will be remove in future because it wll be merge with layer wizard
    # This function creates an XML document and adds the necessary
    # KML elements.
    pool = pooler.get_pool(cr.dbname)
    kml = pool.get('res.partner').get_kml(cr, uid, context=context)
    out = base64.encodestring(kml)#.encode('ascii', 'replace')
    fname = 'turnover' + '.kml'
    return {'kml_file': out, 'name': fname}

class customer_on_map(wizard.interface):

    states = {
         'init': {
            'actions': [create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                }
            }

customer_on_map('google.earth')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: