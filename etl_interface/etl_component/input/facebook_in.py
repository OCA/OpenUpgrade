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


class etl_component_field(osv.osv):
    _name='etl.component.field'
    _columns={
              'source_field' : fields.char('Source Field', size=124), 
              'dest_field' : fields.char('Destination Field', size=124), 
              'component_id' : fields.many2one('etl.component', 'Model'), 
              }

etl_component_field()


class etl_component_facebook_in(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'    

    _columns={
              'field_ids' : fields.one2many('etl.component.field', 'component_id', 'Fields'), 
              'method' : fields.text('Method'), 
              'connector_id' : fields.many2one('etl.connector', 'Connector'), 
              'transformer_id' : fields.many2one('etl.transformer', 'Transformer'), 
     }
  
  
        
etl_component_facebook_in()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

