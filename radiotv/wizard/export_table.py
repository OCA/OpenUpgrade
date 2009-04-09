# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Zikzakmedia SL (http://www.zikzakmedia.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import netsvc
import pooler
import time
import urllib
import base64
from osv import osv

def export_table(self, cr, uid, data, context, server, table, fields, filter = [], filterphp = ''):
    """Export (synchronize) the fields of the radiotv.table to Joomla PHP server.
       Only the records matching the filter are exported.
       filterphp is the same filter in SQL notation to used in the PHP code.
       New records are inserted, existing records are updated and removed records are deleted"""
    pool = pooler.get_pool(cr.dbname)
    obj = 'radiotv.'+table
    tbl = 'radiotv_'+table
    new = 0
    update = 0
    server.reset_table(tbl)
    elem_ids = pool.get(obj).search(cr, uid, filter)
    for elem in pool.get(obj).browse(cr, uid, elem_ids, context):

        vals = {}
        for field in fields:
            if field[-3:] == "_id":
                vals[field] = getattr(elem, field).id
            elif field[-4:] == "_ids":
                vals[field] = [c.id for c in getattr(elem, field)]
            else:
                vals[field] = getattr(elem, field)

        attach_ids = pool.get('ir.attachment').search(cr, uid, [('res_model','=',obj), ('res_id', '=',elem.id)])
        cont = 0
        for data in pool.get('ir.attachment').browse(cr, uid, attach_ids, context):
            s = data['datas_fname'].split('.')
            extension = s[-1].lower()
            s.pop()
            name = ".".join(s)
            #print name + " " + extension
            if extension in ['jpeg', 'jpe', 'jpg', 'gif', 'png']:
                if extension in ['jpeg', 'jpe', 'jpg']:
                    extension='jpeg'
                if not data['link']:
                    vals['picture'+str(cont)] = data['datas']
                else:
                    try:
                        vals['picture'+str(cont)] = base64.encodestring(urllib.urlopen(data['link']).read())
                    except:
                        continue
                vals['fname'+str(cont)] = name + '.' + extension
                cont = cont + 1
        #print vals

        if server.set_table(tbl, vals):
            new += 1
        else:
            update += 1

    delete = server.delete_table(tbl, filterphp)
    return (new, update, delete)


def export_write(self, cr, uid, server, table, ids, vals, context):
    """Synchronize the fields defined in vals of the radiotv.table to Joomla PHP server.
       Only the records with ids are exported.
       New records are inserted, existing records are updated"""
    pool = pooler.get_pool(cr.dbname)
    obj = 'radiotv.'+table
    tbl = 'radiotv_'+table
    new = 0
    update = 0
    for field in vals.keys():
        if field[-4:] == "_ids":
            vals[field] = vals[field][0][2]
    for id in ids:
        vals['id'] = id

        attach_ids = pool.get('ir.attachment').search(cr, uid, [('res_model','=',obj), ('res_id', '=',id)])
        cont = 0
        for data in pool.get('ir.attachment').browse(cr, uid, attach_ids, context):
            s = data['datas_fname'].split('.')
            extension = s[-1].lower()
            s.pop()
            name = ".".join(s)
            #print name + " " + extension
            if extension in ['jpeg', 'jpe', 'jpg', 'gif', 'png']:
                if extension in ['jpeg', 'jpe', 'jpg']:
                    extension='jpeg'
                if not data['link']:
                    vals['picture'+str(cont)] = data['datas']
                else:
                    try:
                        vals['picture'+str(cont)] = base64.encodestring(urllib.urlopen(data['link']).read())
                    except:
                        continue
                vals['fname'+str(cont)] = name + '.' + extension
                cont = cont + 1
        #print vals

        if server.set_table(tbl, vals):
            new += 1
        else:
            update += 1

    return (new, update)


def export_ulink(self, cr, uid, server, table, ids, table_rel=None, field_rel=None):
    """Synchronize the radiotv.table to Joomla PHP server.
       Only the records with ids are deleted.
       If table_rel and field_rel are defined, also deletes the records in the table_rel"""
    tbl = 'radiotv_'+table
    delete = server.delete_items(tbl, ids, "id")
    if table_rel != None:
        tbl = 'radiotv_'+table_rel
        server.delete_items(tbl, ids, field_rel)
    return delete
