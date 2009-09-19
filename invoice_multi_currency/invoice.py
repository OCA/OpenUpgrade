#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

from osv import osv
from osv import fields

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
    }
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def product_id_change(self, cr, uid, ids, product, uom, currency_id, company_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, context=None):
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty=qty, name=name, type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, address_invoice_id=address_invoice_id, context=context)

        if not company_id and not currency_id:
            return res
            
        company = self.pool.get('res.company').browse(cr, uid, company_id)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id)
        
        if company.currency_id.id != currency.id:
            new_price = res['value']['price_unit'] * currency.rate
            res['value']['price_unit'] = new_price
        return res
        
account_invoice_line()
