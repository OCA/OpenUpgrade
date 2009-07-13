#!/usr/bin/python
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
import etl
import tools
from osv import osv, fields


class etl_component_schema_validation(osv.osv):
    _name='etl.component'
    _inherit='etl.component'
    _columns={
          'field_name' : fields.boolean('Check Field Name'),
          'field_extra' : fields.boolean('Refuse Extra Fields'),
          'field_type' : fields.boolean('Check Field Type'),
          'field_size' : fields.boolean('Check Field Size'),
          'field_format' : fields.boolean('Check Format'),
          'not_null' : fields.boolean('Check NOT NULL'),
          'field_key' : fields.boolean('Check Key'),
              }
    
    def create_instance(self, cr, uid, id, context={}, data={}):
        val=super(etl_component_schema_validation, self).create_instance(cr, uid, id, context, data)       
        cmp =self.browse(cr, uid, id,context=context)
        if cmp.type_id.name == 'transform.schema_validator':
            schema = {
                        'invalid_field' : cmp.field_extra,
                        'invalid_name' : cmp.field_name,
                        'invalid_key' : cmp.field_key,
                        'invalid_null' : cmp.not_null,
                        'invalid_type' : cmp.field_type,
                        'invalid_size' : cmp.field_size,
                        'invalid_format' : cmp.field_format
                      }
            val = etl.component.transform.schema_validator(schema, cmp.name)
        return val
    
etl_component_schema_validation()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: