# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from report import report_sxw
from osv import osv
import pooler

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'so_number' : self.so_number,
        })

    def so_number(self,production):
        _so = []
        _parent_moveline=False
        if production.move_prod_id.id :
            _parent_moveline = self.get_parent_move(production.move_prod_id.id)
        if _parent_moveline:
            _smove = pooler.get_pool(self.cr.dbname).get('stock.move').browse(self.cr,self.uid,_parent_moveline)
            _soid = _smove.sale_line_id
            _so.append(_soid.order_id)
        return _so

    def get_parent_move(self,move_id):
        _smoveline = pooler.get_pool(self.cr.dbname).get('stock.move').browse(self.cr,self.uid,move_id)
        if _smoveline.move_dest_id:
            return self.get_parent_move(_smoveline.move_dest_id.id)
        return move_id


report_sxw.report_sxw('report.mrp.production.order','mrp.production','addons/mrp_production_report/report/order.rml',parser=order)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

