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

class etl_component_vcard_out(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'    

    _columns={
            'connector_id' :  fields.many2one('etl.connector', 'Connector', domain="[('type','=',localfile)]"), 
    }
    
    def create_instance(self, cr, uid, id, context={}):
        val=super(etl_component_vcard_out, self).create_instance(cr, uid, id, context)
        obj_connector=self.pool.get('etl.connector')
        obj_transformer = self.pool.get('etl.transformer')
        cmp=self.browse(cr, uid, id)
        if cmp.type_id.name=='input.vcard_out':      
            conn_instance=trans_instance=False            
            if cmp.connector_id:                
                conn_instance=obj_connector.get_instance(cr, uid, cmp.connector_id.id , context)                
            if cmp.transformer_id:                
                trans_instance=obj_transformer.get_instance(cr, uid, cmp.transformer_id.id, context)

            val =etl.component.input.vcard_out(conn_instance, 'component.input.vcard_out')        
            
        return val      
        
        
etl_component_vcard_out()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

