# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Sandas. (http://www.sandas.eu) All Rights Reserved.
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

import pooler

def base_delete_unit_test_records(obj, cr, uid):
    user_rec = obj.pool.get('res.users')
    for user in user_rec.search(cr, uid, [('unit_test','=',True)]):
        ids = obj.search(cr, user, [('unit_test','=',True)])
        for id in ids:
            data_ids = (obj.pool.get('ir.model.data')).search(cr, user, 
                [('model','=',obj._name), ('res_id','=',id)])
            (obj.pool.get('ir.model.data')).unlink(cr, user, data_ids)
            obj.unlink(cr, user, [id])
        cr.commit()
        
def base_get_default_currency(cr, uid, context):
    rec_usr = pooler.get_pool(cr.dbname).get('res.users')
    usr = rec_usr.read(cr, uid, [uid], ["currency_id"])
    if usr[0]["currency_id"]:
        return usr[0]["currency_id"][0]
    else:
        return usr[0]["currency_id"]
