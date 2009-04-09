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

import netsvc
import time
from osv import fields, osv


class credit_line(osv.osv):
    _name = 'credit.line'
    _description = 'Credit line'

    def get_available_amount(self, cr, uid, credit_line_id, base_amount, partner_id, context={}):
        this = self.browse(cr, uid, [credit_line_id])[0]

        #sum the eligible amounts for translation folder + embassy folder line for everyone and for this partner
        tot_sum = 0
        partner_sum = 0

        #translation folder
        list = self.pool.get('translation.folder').search(cr, uid, [('credit_line_id','=',this.id),('state','<>','cancel')])
        for item in self.pool.get('translation.folder').browse(cr, uid, list):
            #for everyone
            tot_sum += item.awex_amount
            if item.partner_id.id == partner_id:
                #for this partner
                partner_sum +=  item.awex_amount

        #embassy folder line 
        list2 = self.pool.get('cci_missions.embassy_folder_line').search(cr, uid, [('credit_line_id','=',this.id),('awex_eligible','=',True)])
        for item2 in self.pool.get('cci_missions.embassy_folder_line').browse(cr, uid, list2):
            #for everyone
            tot_sum += item2.awex_amount
            if item2.folder_id.crm_case_id.partner_id.id == partner_id:
                #for this partner
                partner_sum +=  item2.awex_amount

        partner_remaining_amount = this.customer_credit - partner_sum
        tot_remaining_amount = this.global_credit - tot_sum

        res = min(base_amount / 2, partner_remaining_amount, tot_remaining_amount)
        if res < 0:
            return 0
        return res

    _columns = {
        'name':fields.char('Name', size=32, required=True),
        'from_date':fields.date('From Date', required=True),
        'to_date':fields.date('To Date', required=True),
        'global_credit':fields.float('Global Credit', required=True),
        'customer_credit':fields.float('Customer Max Credit', required=True)
    }
credit_line()

class translation_folder(osv.osv):
    _name = 'translation.folder'
    _description = 'Translation Folder'

    def cci_translation_folder_confirmed(self, cr, uid, ids, *args):
        for id in self.browse(cr, uid, ids):
            data = {}
            data['state']='confirmed'
            if id.awex_eligible and id.partner_id.awex_eligible == 'yes':
                #look for an existing credit line in the current time
                credit_line = self.pool.get('credit.line').search(cr, uid, [('from_date','<=',time.strftime('%Y-%m-%d')), ('to_date', '>=', time.strftime('%Y-%m-%d'))])
                if credit_line:
                    #if there is one available: get available amount from it
                    amount = self.pool.get('credit.line').browse(cr, uid,[credit_line[0]])[0].get_available_amount(cr, uid, credit_line[0], id.base_amount, id.partner_id.id)
                    if amount > 0:
                        data['awex_amount'] = amount
                        data['credit_line_id'] =  credit_line[0]
                    else:
                        data['awex_eligible'] = False
            self.write(cr, uid, [id.id], data)
        return True

    _columns = {
        'order_desc':fields.char('Description', size=64, required=True, select=True),
        'name': fields.text('Name', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'base_amount': fields.float('Base Amount', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'awex_eligible':fields.boolean('AWEX Eligible', readonly=True, states={'draft':[('readonly',False)]}),
        'awex_amount':fields.float('AWEX Amount', readonly=True),
        'state':fields.selection([('draft','Draft'),('confirmed','Confirmed'),('invoiced','Invoiced'),('done', 'Done'),('cancel','Cancel')],'State',readonly=True),
        'credit_line_id': fields.many2one('credit.line', 'Credit Line', readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'purchase_order': fields.many2one('purchase.order', 'Purchase Order'),
        'order_date':fields.date('Order Date',required=True)
        }
    _defaults = {
        'state' : lambda *a : 'draft',
        'order_date': lambda *b: time.strftime('%Y-%m-%d'),
        'order_desc': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'translation.folder'),
    }
translation_folder()

class letter_credence(osv.osv):
    _name = 'letter.credence'
    _description = 'Letter of Credence'
    _columns = {
        'emission_date':fields.date('Emission Date', required=True),
        'asked_amount':fields.float('Asked Amount', required=True)
    }
letter_credence()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'Partner'
    _columns = {
        'awex_eligible':fields.selection([('unknown','Unknown'),('yes','Yes'),('no','No')], "AWEX Eligible"),
    }
    _defaults = {
        'awex_eligible' : lambda *a : 'unknown',
    }
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

