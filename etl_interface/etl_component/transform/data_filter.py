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


class etl_component_filter_criteria(osv.osv):
     _name='etl.component.filter.criteria'
     _rec_neme='sequence'
     _columns={
      'sequence' : fields.integer('Sequence'),
      'field_name' : fields.char('Field Name', size=30),
      'operator': fields.selection([('equal','='), ('not_equal','<>'),('less_equalto','<='),('greater_equalto','>='),('in','in')], 'Operator' ),
      'operand' : fields.char('Operand', size=30),
      'condition': fields.selection([('or','OR'), ('xor','XOR'),('and','AND')], 'Condition'),
      'component_id' : fields.many2one('etl.component', 'Component'),

    }

etl_component_filter_criteria()

class etl_component_transform_filter(osv.osv):
     _name='etl.component'
     _inherit = 'etl.component'

     _columns={
      'criteria_ids' : fields.one2many('etl.component.filter.criteria','component_id', 'Filter Criteria'),
     }

etl_component_transform_filter()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: