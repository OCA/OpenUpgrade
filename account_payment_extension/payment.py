# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2009 Zikzakmedia S.L. (http://www.zikzakmedia.com) All Rights Reserved.
# Copyright (c) 2008 Pablo Rocandio (salbet@gmail.com) All Rights Reserved.
# Copyright (c) 2006 ACYSOS S.L. (http://acysos.com) All Rights Reserved.
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
from osv import fields, osv

class payment_type(osv.osv):
    _inherit='payment.type'
    _description='Payment types'
    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Payment Type', translate=True, select=True),
        'active': fields.boolean('Active', select=True),
        'note': fields.text('Description', translate=True, help="Description of the payment type that will be shown in the invoices"),
    }
    _defaults = {
        'active': lambda *a: 1,
    }
payment_type()


class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
        'payment_type_customer': fields.many2one('payment.type', 'Payment type', help="Payment type of the customer"),
        'payment_type_supplier': fields.many2one('payment.type', 'Payment type', help="Payment type of the supplier"),
    }
res_partner()


class res_partner_bank(osv.osv):

    def create(self, cr, uid, vals, context=None):
        if vals['default_bank'] and vals['partner_id'] and vals['state']:
            sql = "UPDATE res_partner_bank SET default_bank='0' WHERE partner_id=%i AND default_bank='1' AND state='%s'" % (vals['partner_id'], vals['state'])
            cr.execute(sql)
        return super(res_partner_bank, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'default_bank' in vals and vals['default_bank'] == True:
            partner_bank = self.pool.get('res.partner.bank').browse(cr, uid, ids)[0]
            partner_id = partner_bank.partner_id.id
            if vals['state']:
                state = vals['state']
            else:
                state = partner_bank.state
            sql = "UPDATE res_partner_bank SET default_bank='0' WHERE partner_id=%i AND default_bank='1' AND state='%s' AND id<>%i" % (partner_id, state, ids[0])
            cr.execute(sql)
        return super(res_partner_bank, self).write(cr, uid, ids, vals, context=context)

    _inherit="res.partner.bank"
    _columns = {
        'default_bank' : fields.boolean('Default'),
    }

res_partner_bank()


class payment_order(osv.osv):
    _name = 'payment.order'
    _inherit = 'payment.order'

    def _get_type(self, cr, uid, context={}):
        type = context.get('type', 'payable')
        print "type",type
        return type

    def _get_reference(self, cr, uid, context={}):
        type = context.get('type', 'payable')
        if type == 'payable':
            ref = self.pool.get('ir.sequence').get(cr, uid, 'payment.order')
        else:
            ref = self.pool.get('ir.sequence').get(cr, uid, 'rec.payment.order')
        return ref

    def _payment_type_name_get(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.mode and rec.mode.type.name or ""
        return result

    def _name_get(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.reference
        return result

    _columns = {
        'type': fields.selection([
            ('payable','Payable'),
            ('receivable','Receivable'),
            ],'Type', readonly=True, select=True),
        # invisible field to filter payment order lines by payment type
        'payment_type_name': fields.function(_payment_type_name_get, method=True, type="char", size="64", string="Payment type name"),
        # The field name is necessary to add attachement documents to payment orders
        'name': fields.function(_name_get, method=True, type="char", size="64", string="Name"),
    }
    _defaults = {
        'type': _get_type,
        'reference': _get_reference,
    }

    def unlink(self, cr, uid, ids):
        pay_orders = self.read(cr, uid, ids, ['state'])
        unlink_ids = []
        for t in pay_orders:
            if t['state'] in ('draft', 'cancel'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action!'), _('You cannot delete payment order(s) which are already confirmed or done!'))
        result = super(payment_order, self).unlink(cr, uid, unlink_ids, context=context)
#        osv.osv.unlink(self, cr, uid, unlink_ids)
        return result

payment_order()


class payment_line(osv.osv):
    _name = 'payment.line'
    _inherit = 'payment.line'

    _columns = {
        'move_line_id': fields.many2one('account.move.line','Entry line', domain="[('reconcile_id','=', False), ('amount_to_pay','<>',0), ('account_id.type','=',parent.type),('payment_type','ilike',parent.payment_type_name or '%')]", help='This Entry Line will be referred for the information of the ordering customer.'),
    }

    def onchange_move_line(self, cr, uid, ids, move_line_id, payment_type, date_prefered, date_planned, currency=False, company_currency=False, context=None):
        # Adds account.move.line name to the payment line communication
        res = super(payment_line, self).onchange_move_line(cr, uid, ids, move_line_id, payment_type, date_prefered, date_planned, currency, company_currency, context)
        if move_line_id:
            line = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
            if line.name != '/':
                res['value']['communication'] = res['value']['communication'] + '. ' + line.name
        return res

payment_line()