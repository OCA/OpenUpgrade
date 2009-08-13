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

from osv import fields, osv

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit="account.invoice"
    _columns = {
        'user_id': fields.many2one('res.users', 'Salesman'),
    }
    _defaults = {
        'user_id': lambda self,cr,uid,ctx: uid
    }

account_invoice()

class sale_order(osv.osv):
    _inherit="sale.order"

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed','done','exception']):
        salesman_ids = self.read(cr,uid,ids,['user_id'])
        for salesman in salesman_ids:
            result = super(sale_order, self).action_invoice_create(cr, uid,
                    ids, grouped, states)
            if result and salesman.get('user_id',False):
                self.pool.get('account.invoice').write(cr, uid, result, {'user_id':salesman['user_id'][0]})
        return result
    
sale_order()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cursor, user, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        result = super(stock_picking, self).action_invoice_create(cursor, user,
                ids, journal_id, group, type,
                context)
        invoice_ids = result.values()
        for picking in self.browse(cursor, user, ids, context=context):
            if not picking.sale_id:
                continue
            if picking.sale_id.user_id:
                self.pool.get('account.invoice').write(cursor, user, invoice_ids, {'user_id':picking.sale_id.user_id.id })
        return result
    
stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

