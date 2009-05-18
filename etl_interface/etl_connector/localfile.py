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

class etl_connector_localfile(osv.osv):
    _name='etl.connector'
    _inherit='etl.connector'

    _columns={
              'bufsize' : fields.integer('Buffer Size'),
              'mode' : fields.char('File Operation Mode', size=12),
    }

    _defaults = {
                    'mode': lambda *a: 'r+',
         }
    
    def create_instance(self, cr, uid, id , context={}, data={}):
        val =  super(etl_connector_localfile, self).create_instance(cr, uid, id, context, data)
        con=self.browse(cr, uid, id)
        if con.type == 'localfile':
            val =  etl.connector.localfile(con.uri, con.mode, con.bufsize, encoding='utf-8', name=con.name)
        return val
    
etl_connector_localfile()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

