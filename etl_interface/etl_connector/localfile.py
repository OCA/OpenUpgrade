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
from osv import osv, fields
import etl
import os
import shutil
import tools

class etl_connector_localfile(osv.osv):
    _name='etl.connector'
    _inherit='etl.connector'
    _path =  './filestore/etl_data/'
    
    _columns={
              'bufsize' : fields.integer('Buffer Size'),
              'mode' : fields.char('File Operation Mode', size=12),
              'local_name' : fields.char('Local Name', size=24, readonly=True),
    }

    _defaults = {
                    'mode': lambda *a: 'r+',
         }

    _sql_constraints = [
        ('local_name_uniq', 'UNIQUE(local_name)', 'The Local Name must be unique!'),
    ]

    def create(self, cr, uid, vals, context={}):
        if not vals['type'] == 'localfile':
            return super(etl_connector_localfile, self).create(cr, uid, vals, context)
        vals['local_name'] = self.copy_file(cr, uid, vals['uri'])
        return super(etl_connector_localfile, self).create(cr, uid, vals, context)
            
    def copy_file(self, cr, uid, uri):
        import random, string
        ext  = uri[uri.rfind('.'):]
        random.seed()
        d = [random.choice(string.ascii_letters) for x in xrange(10) ]
        filename = "".join(d) + ext
        if os.path.exists(uri):
            shutil.copyfile(uri, self._path+filename)
        else:
            f = open( self._path+filename, 'w')
            f.close()
        return filename
    
    def write(self, cr, uid, id ,vals, context={}):
        if 'uri' in vals:
            local = self.browse(cr, uid, id[0])
            if local.type == 'localfile':
                os.remove(self._path+local.local_name)
                vals['local_name'] = self.copy_file(cr, uid, vals['uri'])
        return super(etl_connector_localfile, self).write(cr, uid, id ,vals, context)
        
    def create_instance(self, cr, uid, id , context={}, data={}):
        val =  super(etl_connector_localfile, self).create_instance(cr, uid, id, context, data)
        con=self.browse(cr, uid, id)
        if con.type == 'localfile':
            uri = self._path+con.local_name
            val =  etl.connector.localfile(uri, con.mode, con.bufsize, encoding='utf-8', name=con.name)
        return val
    
etl_connector_localfile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
