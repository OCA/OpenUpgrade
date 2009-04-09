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

from osv import fields, osv

class res_currency(osv.osv):
    _name = "res.currency"
    _inherit = "res.currency"
    
    def compute_with_currency_rate(self, cr, uid, currency_rate, to_currency_id, from_amount, round=True, context={}):
        to_currency = self.browse(cr, uid, to_currency_id, context=context)
        if currency_rate == 0:
            raise osv.except_osv('Error', 'Please enter currency rate !')
        if currency_rate == 1:
            if round:
                return self.round(cr, uid, to_currency, from_amount)
            else:
                return from_amount
        else:
            if round:
                return self.round(cr, uid, to_currency, from_amount * currency_rate)
            else:
                return (from_amount * currency_rate)
    
    def personal_calc_currency_rate(self, cr, uid, account_id, currency_id):
        currency_pool = self.pool.get('res.currency')
        account_pool = self.pool.get('personal.base.account')
        currency_rate = 1
        if (account_id) and (currency_id):
            currency = currency_pool.browse(cr, uid, currency_id)
            account = account_pool.browse(cr, uid, account_id)
            if currency.rate:
                if (currency) and (account):
                    currency_rate = account.currency_id.rate / currency.rate
            else:
                currency_rate = 1
        return currency_rate

res_currency()
