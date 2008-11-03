# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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

import time
import netsvc
from osv import fields, osv

class one2many_mod_advert(fields.one2many):
#this class is used to display crm.case with fields ref or ref2 which are related to the current object

    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
                values = {}
        res = {}
        for id in ids:
            res[id] = []
        for id in ids:
            temp = 'sale.order,'+str(id)
            query = "select id from crm_case where ref = '%s' or ref2 = '%s'" %(temp,temp)
            cr.execute(query)
            case_ids = [ x[0] for x in cr.fetchall()]
            ids2 = obj.pool.get('crm.case').search(cr, user, [(self._fields_id,'in',case_ids)], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    _columns= {
        'parent_so':fields.many2one("sale.order","Parent Sales Order"),
        'child_so':fields.one2many("sale.order","parent_so","Child Sales Order"),
        'case_ids': one2many_mod_advert('crm.case', 'id', "Related Cases"),
    }
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

