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

class account_move_line(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

account_move_line()

class account_move(osv.osv):
    _name = 'account.move'
    _inherit = 'account.move'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

account_move()

class account_journal(osv.osv):
    _name = "account.journal"
    _inherit = "account.journal"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_journal()

class account_analytic_journal(osv.osv):
    _name = "account.analytic.journal"
    _inherit = "account.analytic.journal"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_analytic_journal()

class account_budget_post(osv.osv):
    _name = 'account.budget.post'
    _inherit = 'account.budget.post'
    _columns ={
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_budget_post()

class account_period(osv.osv):
    _name = 'account.period'
    _inherit = 'account.period'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_period()

class account_fiscalyear(osv.osv):
    _name = 'account.fiscalyear'
    _inherit = 'account.fiscalyear'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_fiscalyear()

class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    _columns = {
               'product_id': fields.many2one('product.product', 'Product', ondelete='set null'), 
    }
    
    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False,  company_id=False, context=None):
        
        if context is None:
            context = {}
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {'categ_id': False}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0, 'categ_id': False}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id)
        fpos = fposition_id and self.pool.get('account.fiscal.position').browse(cr, uid, fposition_id) or False

        lang=part.lang
        context.update({'lang': lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)
        if company_id:
            in_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_income'),('res_id','=','product.template,'+str(res.product_tmpl_id.id)+''),('company_id','=',company_id)])
            if not in_pro_id:
                in_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_income_categ'),('res_id','=','product.template,'+str(res.categ_id.id)+''),('company_id','=',company_id)])
            exp_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_expense'),('res_id','=','product.template,'+str(res.product_tmpl_id.id)+''),('company_id','=',company_id)])
            if not exp_pro_id:
                exp_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_expense_categ'),('res_id','=','product.template,'+str(res.categ_id.id)+''),('company_id','=',company_id)])
            
            if not in_pro_id:
                in_acc = res.product_tmpl_id.property_account_income 
                in_acc_cate = res.categ_id.property_account_income_categ
                if in_acc:
                    app_acc_in = in_acc
                else:
                    app_acc_in = in_acc_cate
            else:
                app_acc_in = self.pool.get('account.account').browse(cr,uid,in_pro_id)[0]
            if not exp_pro_id:
                ex_acc = res.product_tmpl_id.property_account_expense
                ex_acc_cate = res.categ_id.property_account_expense_categ
                if ex_acc:
                    app_acc_exp = ex_acc
                else:
                    app_acc_exp = ex_acc_cate
            else:
                app_acc_exp = self.pool.get('account.account').browse(cr,uid,exp_pro_id)[0]
            if not in_pro_id and not exp_pro_id:
                in_acc = res.product_tmpl_id.property_account_income 
                in_acc_cate = res.categ_id.property_account_income_categ
                ex_acc = res.product_tmpl_id.property_account_expense
                ex_acc_cate = res.categ_id.property_account_expense_categ
                if in_acc or ex_acc:
                    app_acc_in = in_acc
                    app_acc_exp = ex_acc
                else:
                    app_acc_in = in_acc_cate
                    app_acc_exp = ex_acc_cate
#            else:
#                app_acc_in = self.pool.get('account.account').browse(cr,uid,in_pro_id)[0]
#                app_acc_exp = self.pool.get('account.account').browse(cr,uid,exp_pro_id)[0]
            if app_acc_in.company_id.id != company_id and app_acc_exp.company_id.id != company_id:
                in_res_id=self.pool.get('account.account').search(cr,uid,[('name','=',app_acc_in.name),('company_id','=',company_id)])
                exp_res_id=self.pool.get('account.account').search(cr,uid,[('name','=',app_acc_exp.name),('company_id','=',company_id)])
                if not in_res_id and not exp_res_id:
                    raise osv.except_osv(_('Configration Error !'),
                        _('Can not find account chart for this company, Please Create account.'))
                in_obj_acc=self.pool.get('account.account').browse(cr,uid,in_res_id)
                exp_obj_acc=self.pool.get('account.account').browse(cr,uid,exp_res_id)
                if in_acc or ex_acc:
                    res.product_tmpl_id.property_account_income = in_obj_acc[0]
                    res.product_tmpl_id.property_account_expense = exp_obj_acc[0]
                else:
                    res.categ_id.property_account_income_categ = in_obj_acc[0]
                    res.categ_id.property_account_expense_categ = exp_obj_acc[0]

        if type in ('out_invoice','out_refund'):
            a =  res.product_tmpl_id.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a =  res.product_tmpl_id.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id

        a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        taxep=None
        tax_obj = self.pool.get('account.tax')
        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid,a).tax_ids or False)
            tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid,a).tax_ids or False)
            tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
        if type in ('in_invoice', 'in_refund'):
            to_update = self.product_id_change_unit_price_inv(cr, uid, tax_id, price_unit, qty, address_invoice_id, product, partner_id, context=context)
            result.update(to_update)
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})

        if not name:
            result['name'] = res.name

        domain = {}
        result['uos_id'] = uom or res.uom_id.id or False
        if result['uos_id']:
            res2 = res.uom_id.category_id.id
            if res2 :
                domain = {'uos_id':[('category_id','=',res2 )]}

        prod_pool=self.pool.get('product.product')            
        result['categ_id'] = res.categ_id.id       
        return {'value':result, 'domain':domain}
   
#    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False,  company_id=False, context=None):
#        if context is None:
#            context = {}
#        if not partner_id:
#            raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )
#        if not product:
#            if type in ('in_invoice', 'in_refund'):
#                return {'domain':{'product_uom':[]}}
#            else:
#                return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
#        part = self.pool.get('res.partner').browse(cr, uid, partner_id)
#        fpos = fposition_id and self.pool.get('account.fiscal.position').browse(cr, uid, fposition_id) or False
#
#        lang=part.lang
#        context.update({'lang': lang})
#        result = {}
#        res = self.pool.get('product.product').browse(cr, uid, product, context=context)
#        if company_id:
#            in_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_income'),('res_id','=','product.template,'+str(res.product_tmpl_id.id)+''),('company_id','=',company_id)])
#            if not in_pro_id:
#                in_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_income_categ'),('res_id','=','product.template,'+str(res.categ_id.id)+''),('company_id','=',company_id)])
#            exp_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_expense'),('res_id','=','product.template,'+str(res.product_tmpl_id.id)+''),('company_id','=',company_id)])
#            if not exp_pro_id:
#                exp_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_expense'),('res_id','=','product.template,'+str(res.categ_id.id)+''),('company_id','=',company_id)])
#            if not in_pro_id and not exp_pro_id:
#                in_acc = res.product_tmpl_id.property_account_income 
#                in_acc_cate = res.categ_id.property_account_income_categ
#                ex_acc = res.product_tmpl_id.property_account_expense
#                ex_acc_cate = res.categ_id.property_account_expense_categ
#                if in_acc or ex_acc:
#                    app_acc_in = in_acc
#                    app_acc_exp = ex_acc
#                else:
#                    app_acc_in = in_acc_cate
#                    app_acc_exp = ex_acc_cate
#            else:
#                app_acc_in = self.pool.get('account.account').browse(cr,uid,in_pro_id)[0]
#                app_acc_exp = self.pool.get('account.account').browse(cr,uid,exp_pro_id)[0]
#            if app_acc_in.company_id.id != company_id and app_acc_exp.company_id.id != company_id:
#                in_res_id=self.pool.get('account.account').search(cr,uid,[('name','=',app_acc_in.name),('company_id','=',company_id)])
#                exp_res_id=self.pool.get('account.account').search(cr,uid,[('name','=',app_acc_exp.name),('company_id','=',company_id)])
#                if not in_res_id and not exp_res_id:
#                    raise osv.except_osv(_('Configration Error !'),
#                        _('Can not find account chart for this company, Please Create account.'))
#                in_obj_acc=self.pool.get('account.account').browse(cr,uid,in_res_id)
#                exp_obj_acc=self.pool.get('account.account').browse(cr,uid,exp_res_id)
#                if in_acc or ex_acc:
#                    res.product_tmpl_id.property_account_income = in_obj_acc[0]
#                    res.product_tmpl_id.property_account_expense = exp_obj_acc[0]
#                else:
#                    res.categ_id.property_account_income_categ = in_obj_acc[0]
#                    res.categ_id.property_account_expense_categ = exp_obj_acc[0]
#
#        if type in ('out_invoice','out_refund'):
#            a =  res.product_tmpl_id.property_account_income.id
#            if not a:
#                a = res.categ_id.property_account_income_categ.id
#        else:
#            a =  res.product_tmpl_id.property_account_expense.id
#            if not a:
#                a = res.categ_id.property_account_expense_categ.id
#
#        a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
#        if a:
#            result['account_id'] = a
#
#        taxep=None
#        tax_obj = self.pool.get('account.tax')
#        if type in ('out_invoice', 'out_refund'):
#            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid,a).tax_ids or False)
#            tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
#        else:
#            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid,a).tax_ids or False)
#            tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
#        if type in ('in_invoice', 'in_refund'):
#            to_update = self.product_id_change_unit_price_inv(cr, uid, tax_id, price_unit, qty, address_invoice_id, product, partner_id, context=context)
#            result.update(to_update)
#        else:
#            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
#
#        if not name:
#            result['name'] = res.name
#
#        domain = {}
#        result['uos_id'] = uom or res.uom_id.id or False
#        if result['uos_id']:
#            res2 = res.uom_id.category_id.id
#            if res2 :
#                domain = {'uos_id':[('category_id','=',res2 )]}
#        return {'value':result, 'domain':domain}

account_invoice_line()

class JournalPeriod(osv.osv):
    _inherit = 'account.journal.period'
    _columns = {
        'company_id' : fields.many2one('res.company', 'Company')
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
JournalPeriod()

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        invoice_addr_id = False
        contact_addr_id = False
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False

        opt = [('uid', str(uid))]
        if partner_id:
            opt.insert(0, ('id', partner_id))
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if p.property_account_receivable.company_id.id != company_id and p.property_account_payable.company_id.id != company_id:
                    rec_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id: 
                        rec_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = self.pool.get('ir.property').read(cr,uid,rec_pro_id,['name','value','res_id'])
                    pay_line_data = self.pool.get('ir.property').read(cr,uid,pay_pro_id,['name','value','res_id'])
                    rec_res_id = int(rec_line_data[0]['value'].split(',')[1]) or False
                    pay_res_id = int(pay_line_data[0]['value'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configration Error !'),
                            _('Can not find account chart for this company, Please Create account.'))
                    rec_obj_acc=self.pool.get('account.account').browse(cr,uid,[rec_res_id])
                    pay_obj_acc=self.pool.get('account.account').browse(cr,uid,[pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
            else:
                acc_id = p.property_account_payable.id
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

        result = {'value': {
            'address_contact_id': contact_addr_id,
            'address_invoice_id': invoice_addr_id,
            'account_id': acc_id,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position
            }
        }
        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank'] = bank_id
        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr,uid,ids,partner_payment_term,date_invoice)
                result['value'].update(to_update['value'])
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        return result
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True, states={'draft':[('readonly',False)]}),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
    
    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line):
        val={}
        if company_id and part_id and type:
            acc_id = False
            partner_obj = self.pool.get('res.partner').browse(cr,uid,part_id)
            if partner_obj.property_account_payable and partner_obj.property_account_receivable:
                if partner_obj.property_account_payable.company_id.id != company_id and partner_obj.property_account_receivable.company_id.id != company_id:
                    rec_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    pay_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id: 
                        rec_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = self.pool.get('ir.property').search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = self.pool.get('ir.property').read(cr,uid,rec_pro_id,['name','value','res_id'])
                    pay_line_data = self.pool.get('ir.property').read(cr,uid,pay_pro_id,['name','value','res_id'])
                    rec_res_id = int(rec_line_data[0]['value'].split(',')[1]) or False
                    pay_res_id = int(pay_line_data[0]['value'].split(',')[1]) or False
                    if not rec_res_id and not rec_res_id:
                        raise osv.except_osv(_('Configration Error !'),
                            _('Can not find account chart for this company, Please Create account.'))
                    if type in ('out_invoice', 'out_refund'):
                        acc_id = rec_res_id
                    else:
                        acc_id = pay_res_id
                    val= {'account_id': acc_id}
            if ids:
                if company_id:
                    inv_obj = self.browse(cr,uid,ids)
                    for line in inv_obj[0].invoice_line:
                        if line.account_id:
                            if line.account_id.company_id.id != company_id:
                                result_id = self.pool.get('account.account').search(cr,uid,[('name','=',line.account_id.name),('company_id','=',company_id)])
                                if not result_id:
                                    raise osv.except_osv(_('Configration Error !'),
                                        _('Can not find account chart for this company in invoice line account, Please Create account.'))
                                r_id = self.pool.get('account.invoice.line').write(cr,uid,[line.id],{'account_id': result_id[0]})
            else:
                if invoice_line:
                    for inv_line in invoice_line:
                        obj_l = self.pool.get('account.account').browse(cr,uid,inv_line[2]['account_id'])
                        if obj_l.company_id.id != company_id:
                            raise osv.except_osv(_('Configration Error !'),
                                _('invoice line account company is not match with invoice company.'))
                        else:
                            continue
        return {'value' : val }
account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

