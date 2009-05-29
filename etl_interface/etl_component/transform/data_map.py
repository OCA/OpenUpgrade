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

class etl_component_map_field(osv.osv):
    _name='etl.component.field'
    _inherit ='etl.component.field'
    _rec_name = 'source_field'
    
    def _get_channels(self, cr, uid, context={}):
        c_obj = self.pool.get('etl.channel')
        ch_ids = c_obj.search(cr, uid, [('type', '=', 'transition')])
        result = c_obj.read(cr, uid, ch_ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in result]
    
    _columns = {
          'channel': fields.selection(_get_channels, 'Channel'),
              }

etl_component_map_field()

class etl_component_transform_map(osv.osv):
    _name = 'etl.component'
    _inherit = 'etl.component'
    _columns={
            'map_line_ids' : fields.one2many('etl.component.field', 'component_id', 'Map lines'),
            'preprocess' : fields.text('Preprocess'),
    }

    def create_instance(self, cr, uid, id, context={}, data={}):
        obj_transformer = self.pool.get('etl.transformer')
        cmp=self.browse(cr, uid, id)
        val=super(etl_component_transform_map, self).create_instance(cr, uid, id, context, data)
        if cmp.type_id.name == 'transform.map':
            trans_instance=False
            map_criteria={}
            if cmp.transformer_id:
                trans_instance=obj_transformer.create_instance(cr, uid, cmp.transformer_id.id, context, data)
            for line in cmp.map_line_ids:
                if not line.channel in map_criteria:
                    map_criteria[line.channel] = {}
                map_criteria[line.channel].update({line.source_field:line.dest_field})
            val = etl.component.transform.map(map_criteria, cmp.preprocess, cmp.name, trans_instance, cmp.row_limit)
        return val

etl_component_transform_map()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
