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
import mx.DateTime
from mx.DateTime import RelativeDateTime

class account_payment_term(osv.osv):
    _name = "account.payment.term"
    _inherit = "account.payment.term"
    _columns = {
        'cash_discount_ids': fields.one2many('account.cash.discount', 'payment_id', 'Cash Discounts'),
    }
    def get_discounts(self,cr,uid,id,base_date, context={}):
        """
        return the list of (date,percentage) ordered by date for the
        payment term with the corresponding id. return [] if no cash
        discount are defined. base_date is the date from where the
        discounts are computed.
        """
        
        pt = self.browse(cr, uid, id, context)
        
        if not pt.cash_discount_ids:
            return []

        res=[]
        for d in pt.cash_discount_ids: 
            res.append(
                ((mx.DateTime.strptime(base_date,'%Y-%m-%d') +\
                  RelativeDateTime(days=d.delay+1)).strftime("%Y-%m-%d"),
                 d.discount)
                )
            
        res.sort(cmp=lambda x,y: cmp(x[0],y[0]))
        return res
account_payment_term()

class account_cash_discount(osv.osv):
    _name = "account.cash.discount"
    _description = "Cash Discount" #A reduction in the price  if payment is made within a stipulated period.
    _columns = {
        'name': fields.char('Name', size=32),
        'delay': fields.integer('Number of Days', required=True),
        'discount': fields.float('Discount (%)', digits=(16,6),required=True),
        'payment_id': fields.many2one('account.payment.term','Associated Payment Term'),
        'credit_account_id': fields.many2one('account.account', 'Credit Account'),
        'debit_account_id': fields.many2one('account.account', 'Debit Account'),
    }
account_cash_discount()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

