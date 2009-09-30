# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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


class tax_config_wizard(osv.osv_memory):
    _name = 'tax.config.wizard'
    _columns = {
               'name':fields.float('Tax(%) On Invoice',digits=(5,2), help="Normal tax percent to apply on invoices"),
               }
    _defaults = {
        'name': lambda *a: 1.0,
    }

    def action_cancel(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
    def action_create(self, cr, uid,ids, context=None):
        for res in self.read(cr,uid,ids):
            chart_id = self.pool.get('ir.model.data')._get_id(cr, uid, 'l10n_simple', 'simple_chart_template')
            chart_id = self.pool.get('ir.model.data').browse(cr, uid, chart_id, context=context).res_id

            invoice_tax_acc_id = self.pool.get('ir.model.data')._get_id(cr, uid, 'l10n_simple', 'vat_payable')
            invoice_tax_acc_id = self.pool.get('ir.model.data').browse(cr, uid, invoice_tax_acc_id, context=context).res_id

            refund_tax_acc_id = self.pool.get('ir.model.data')._get_id(cr, uid, 'l10n_simple', 'vat_refund')
            refund_tax_acc_id = self.pool.get('ir.model.data').browse(cr, uid, refund_tax_acc_id, context=context).res_id

            new_tax = self.pool.get('account.tax.template').create(cr,uid,
                                                          {'account_collected_id':invoice_tax_acc_id,
                                                            'account_paid_id':refund_tax_acc_id,
                                                            'name':str(res['name'])+'%','amount':res['name']/100,
                                                            'chart_template_id':chart_id })
            chart_obj = self.pool.get('account.chart.template').browse(cr,uid,chart_id)
            acc_ids = [ chart_obj.property_account_expense_categ.id,chart_obj.property_account_income_categ.id]
            acc_obj = self.pool.get('account.account.template')
            for acc in acc_ids:
                acc_obj.write(cr,uid,acc,{'tax_ids':[[6,0,[new_tax]]]})
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
tax_config_wizard()
