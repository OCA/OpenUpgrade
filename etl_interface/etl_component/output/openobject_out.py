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

class etl_component_openobject_lines(osv.osv):
    _name='etl.component.openobject.lines'
    _columns={
          'source_field' : fields.char('Source Field', size=124),
          'dest_field' : fields.char('Destination Field', size=124),
          'component_id' : fields.many2one('etl.component', 'Model'),
    }

etl_component_openobject_lines()

class etl_component_open_object_out(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _columns = {
          'openobject_field_ids' : fields.one2many('etl.component.openobject.lines', 'component_id', 'Fields'),
          'model_id' : fields.many2one('ir.model', 'Model'),
              }

    def create_instance(self, cr, uid, id, context={}, data={}):
        val=super(etl_component_open_object_out, self).create_instance(cr, uid, id, context, data)
        obj_connector=self.pool.get('etl.connector')
        obj_transformer = self.pool.get('etl.transformer')
        cmp=self.browse(cr, uid, id)

        if cmp.type_id.name == 'output.openobject_out':
            conn_instance=False
            trans_instance=False
            if cmp.connector_id:
                conn_instance=obj_connector.get_instance(cr, uid, cmp.connector_id.id , context, data)

            if cmp.transformer_id:
                trans_instance=obj_transformer.get_instance(cr, uid, cmp.transformer_id.id, context, data)

            field_ids={}
            for data in cmp.openobject_field_ids:
                field_ids[data.source_field] = data.dest_field
            val = etl.component.output.openobject_out(conn_instance, cmp.model_id.model, field_ids, 'component.output.openobject_out', trans_instance)
        return val

etl_component_open_object_out()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: