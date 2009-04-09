# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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


class purchase(osv.osv):
    _inherit="purchase.order"
    _columns = {
        'journal_id': fields.many2one('purchase_journal.purchase.journal', 'Journal'),
    }
    def action_picking_create(self, cr, uid, ids, *args):
        result = super(purchase, self).action_picking_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids, context={}):
            pids = [ x.id for x in (order.picking_ids or [])]
            self.pool.get('stock.picking').write(cr, uid, pids, {
                'purchase_journal_id': order.journal_id.id
            })
        return result
purchase()

class picking(osv.osv):
    _inherit="stock.picking"
    _columns = {
        'purchase_journal_id': fields.many2one('purchase_journal.purchase.journal', 'Purchase Journal', select=True),
    }
picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

