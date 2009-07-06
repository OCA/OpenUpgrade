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
import time

import netsvc
from osv import fields, osv

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _decription = 'purchase order'

    def wkf_temp_order0(self, cr, uid, ids, context={}):
        for po in self.browse(cr, uid, ids):
            self.write(cr, uid, [po.id], {'state' : 'wait_approve'})
        return True

    def button_purchase_temp(self, cr, uid, ids, context={}):
        wf_service = netsvc.LocalService('workflow')
        for po in self.browse(cr, uid, ids):
            if po.amount_total < 10000:
                wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_confirm', cr)
            else:
                wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_tempo', cr)
        return True

#    def wkf_write_approvator(self, cr, uid, ids, context={}):
#        wf_service = netsvc.LocalService('workflow')
#        for po in self.browse(cr, uid, ids):
#            self.write(cr, uid, [po.id], { 'validator' : uid})
#            wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_dummy_confirmed', cr)
#        return True

    def wkf_confirm_order(self, cr, uid, ids, context={}):
        for po in self.browse(cr, uid, ids):
            if self.pool.get('res.partner.event.type').check(cr, uid, 'purchase_open'):
                self.pool.get('res.partner.event').create(cr, uid, {'name':'Purchase Order: '+po.name, 'partner_id':po.partner_id.id, 'date':time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id':uid, 'partner_type':'retailer', 'probability': 1.0, 'planned_cost':po.amount_untaxed})
        current_name = self.name_get(cr, uid, ids)[0][1]
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid}) #'approvator' : uid
        return True


    _columns = {
        'internal_notes': fields.text('Internal Note'),
        'approvator' : fields.many2one('res.users', 'Approved by', readonly=True),
        'state': fields.selection([('draft', 'Request for Quotation'), ('wait', 'Waiting'), ('confirmed', 'Confirmed'),('wait_approve','Waiting For Approve'), ('approved', 'Approved'),('except_picking', 'Shipping Exception'), ('except_invoice', 'Invoice Exception'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Order State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
                }
purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

