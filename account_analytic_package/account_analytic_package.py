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
import operator
from osv import osv, fields


class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"
    _columns = {
        'package_ok': fields.boolean('Used in Package'),
    }
account_analytic_account()


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'package_weight': fields.float('Package Weight', digits=(16,2)),
    }
    _defaults = {
        'package_weight': lambda *args: 0.0
    }
product_product()

class crm_case_section(osv.osv):
    _inherit = "crm.case.section"
    _columns = {
        'package_product_id': fields.many2one('product.product', 'Package Product'),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Main Analytic Account'),
        'analytic_journal_id': fields.many2one('account.analytic.journal', 'Analytic Journal'),
    }
crm_case_section()

class crm_case(osv.osv):
    _inherit = "crm.case"
    def case_open(self, cr, uid, ids, *args):
        res = super(crm_case, self).case_open(cr, uid, ids, *args)
        for case in self.browse(cr,uid, ids):
            section = case.section_id
            if section.package_product_id and section.analytic_account_id and section.analytic_journal_id:
                partner = self.pool.get('res.users').browse(cr, uid, uid).address_id.partner_id.id
                aids = self.pool.get('account.analytic.account').search(cr, uid, [('partner_id','=',partner),('state','in',('open','draft','pending')),('parent_id','child_of',[section.analytic_account_id.id])])
                if not aids:
                    raise osv.except_osv('You can not open this case !', 'No valid analytic account defined for your user.\nPlease contact the administrator.')
                self.pool.get('account.analytic.line').create(cr, uid, {
                    'name': case.name,
                    'amount': 0.0,
                    'unit_amount': 1,
                    'product_uom_id': section.package_product_id.uom_id.id,
                    'product_id': section.package_product_id.id,
                    'account_id': aids[0],
                    'general_account_id': section.package_product_id.property_account_income.id or section.package_product_id.categ_id.property_account_income_categ.id,
                    'journal_id': section.analytic_journal_id.id,
                    'user_id': uid,
                    'ref': 'CASE'+str(case.id)
                })
        return res
crm_case()


class account_analytic_line_package(osv.osv):
    _name = "account.analytic.line.package"
    _auto = False
    _order = 'date desc'
    def init(self, cr):
        cr.execute("""
            CREATE OR REPLACE VIEW account_analytic_line_package AS (
                select
                    l.id,
                    l.name,
                    l.date,
                    a.partner_id,
                    a.id as account_id,
                    l.product_id,
                    p.package_weight as unit_weight,
                    p.package_weight*l.unit_amount as total_weight,
                    l.unit_amount 
                from 
                    account_analytic_line l 
                left join 
                    account_analytic_account a on (l.account_id=a.id) 
                left join 
                    product_product p on (p.id=l.product_id) 
                where 
                    l.product_id is not null and
                    p.package_weight<>0 and
                    a.package_ok
            )
        """)
    _columns = {
        'name': fields.char('Name', size=128, readonly=True, select=1),
        'date': fields.date('Date', readonly=True, select=1),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'account_id': fields.many2one('account.analytic.account', 'Account', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', select=2, readonly=True),
        'unit_amount': fields.float('Quantity', readonly=True),
        'unit_weight': fields.float('Unit Weight', readonly=True),
        'total_weight': fields.float('Total Weight', readonly=True),
    }
account_analytic_line_package()

class account_analytic_line_package_month(osv.osv):
    _name = "account.analytic.line.package.month"
    _auto = False
    def init(self, cr):
        cr.execute("""
            CREATE OR REPLACE VIEW account_analytic_line_package_month AS (
                select
                    min(l.id) as id,
                    to_char(l.date, 'YYYY-MM-01') as name,
                    a.partner_id,
                    l.product_id,
                    sum(p.package_weight*l.unit_amount) as total_weight,
                    sum(case when p.package_weight>0 then p.package_weight*l.unit_amount else 0 end) as total_activity,
                    sum(case when p.package_weight<0 then -p.package_weight*l.unit_amount else 0 end) as total_service
                from 
                    account_analytic_line l 
                left join 
                    account_analytic_account a on (l.account_id=a.id) 
                left join 
                    product_product p on (p.id=l.product_id) 
                where 
                    l.product_id is not null and
                    p.package_weight<>0 and
                    a.package_ok
                group by
                    l.product_id,
                    a.partner_id,
                    to_char(l.date, 'YYYY-MM-01')
            )
        """)
    _columns ={
        'name': fields.date('Date', readonly=True, select=1),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', select=2, readonly=True),
        'total_weight': fields.float('Total Weight', readonly=True),
        'total_activity': fields.float('Total Activity', readonly=True),
        'total_service': fields.float('Total Service', readonly=True),
    }
account_analytic_line_package_month()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

