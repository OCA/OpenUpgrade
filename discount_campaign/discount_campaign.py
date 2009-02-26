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

from osv import fields,osv, orm
import time
import tools

class discount_campaign(osv.osv):
    _name = "discount.campaign"
    _columns = {
        'name': fields.char('Name', size=60),
        'date_start': fields.date('Start Date', required=True),
        'date_stop': fields.date('Stop Date', required=True),
        'line_ids': fields.one2many('discount.campaign.line','discount_id', 'Discount Lines'),
        'state' : fields.selection([('draft','Draft'),('open','Open'),('cancel','Canceled'),('done','Done')],'State',readonly=True)
    }

    _defaults = {
        'state': lambda *args: 'draft'
    }


    def action_open(self, cr, uid, ids, *args):
        return True

    def action_done(self, cr, uid, ids,group=True,type='out_refund', context=None):
        # need to make perfect checking
        # remaining to check sale condition
        # need Improvement
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        tax_obj=self.pool.get('account.invoice.tax')
        partner_obj = self.pool.get('res.partner')
        res = {}
        for campaign in self.browse(cr, uid, ids):
            invoices_group = {}
            invoices_line_group={}
            res[campaign.id]=[]
            cr.execute("""
                 SELECT invoice.id from account_invoice invoice
                 left join res_partner partner on invoice.partner_id=partner.id
                 where partner.discount_campaign=%d and (invoice.date_invoice BETWEEN %s AND %s) AND invoice.type = 'out_invoice' AND state = 'open'
                 """ , (campaign.id,campaign.date_start,campaign.date_stop,))
            invoice_ids = map(lambda x:x[0],cr.fetchall())

            for invoice in invoice_obj.browse(cr, uid, invoice_ids):
                for line in invoice.invoice_line:
                    if group and line.product_id.id in invoices_line_group:
                        invoice_line_id=invoices_line_group[line.product_id.id]
                        invoice_line=invoice_line_obj.browse(cr,uid,invoice_line_id)
                        quantity=invoice_line.quantity+line.quantity
                    else:
                        quantity=line.quantity
                    cr.execute("""
                        SELECT discount_line.discount from discount_campaign_line discount_line	where
                        (discount_line.discount_id = %d ) and
                        (discount_line.condition_product_id is null or discount_line.condition_product_id=%d ) and
                        (discount_line.condition_category_id is null or discount_line.condition_category_id=%d ) and
                        (discount_line.condition_quantity is null or discount_line.condition_quantity <=%f ) ORDER BY sequence
                        """ , (campaign.id,line.product_id.id,line.product_id.categ_id.id,quantity))
                    res_discount = cr.dictfetchone()
                    discount=res_discount and res_discount['discount'] or False

                    if discount:
                        if group and invoice.partner_id.id in invoices_group:
                            invoice_id = invoices_group[invoice.partner_id.id]
                        else:
                            new_invoice = invoice_obj.read(cr, uid, invoice.id, ['name', 'type', 'number', 'reference', 'comment', 'date_due', 'partner_id', 'address_contact_id', 'address_invoice_id', 'partner_contact', 'partner_insite', 'partner_ref', 'payment_term', 'account_id', 'currency_id',  'journal_id'])
                            del new_invoice['id']
                            fpos = partner_obj.browse(cr, uid, new_invoice['partner_id'][0]).account_fiscal_position
                            new_invoice.update({
                                'type': type,
                                'date_invoice': time.strftime('%Y-%m-%d'),
                                'state': 'draft',
                                'number': False,
                                'fiscal_position': fpos and fpos.id or False
                            })
                            for field in ('address_contact_id', 'address_invoice_id', 'partner_id','account_id', 'currency_id', 'payment_term', 'journal_id'):
                                new_invoice[field] = new_invoice[field] and new_invoice[field][0]
                            invoice_id = invoice_obj.create(cr, uid, new_invoice,context=context)
                            invoices_group[invoice.partner_id.id] = invoice_id
                            res[campaign.id] += [invoice_id]
                        if group and line.product_id.id in invoices_line_group:
                            invoice_line_id=invoices_line_group[line.product_id.id]
                            invoice_line=invoice_line_obj.browse(cr,uid,invoice_line_id)
                            invoice_line_obj.write(cr,uid,invoice_line_id,{'quantity':invoice_line.quantity+line.quantity})
                        else:
                            invoice_line_id = invoice_line_obj.create(cr, uid,  {
		                    'name': line.name,
		                    'invoice_id': invoice_id,
		                    'uos_id': line.uos_id.id,
		                    'product_id': line.product_id.id,
		                    'account_id': line.account_id.id,
		                    'price_unit': line.price_unit *(float(discount) /100) ,
		                    'discount': 0.0,
		                    'quantity': line.quantity,
		                    'account_analytic_id': line.account_analytic_id.id,
		                 }, context=context)
                            invoices_line_group[line.product_id.id]=invoice_line_id


        return res
discount_campaign()

class discount_campaign_line(osv.osv):
    _name = "discount.campaign.line"
    _columns = {
        'name': fields.char('Name', size=60),
        'sequence': fields.integer('Sequence', required=True),
        'condition_sale': fields.char('Sale Condition', size = 60),
        'condition_category_id': fields.many2one('product.category', 'Category'),
        'condition_product_id' : fields.many2one('product.product', 'Product'),
        'condition_quantity' : fields.float('Min. Quantity'),
        'discount' : fields.float('Discount'),
        'discount_id': fields.many2one('discount.campaign', 'Discount Lines'),
    }
    _defaults = {
        'sequence': lambda *a: 5,
    }
    _order = "sequence, condition_quantity desc"
discount_campaign_line()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'discount_campaign': fields.many2one('discount.campaign', 'Discount Campaign'),
    }
res_partner()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'discount_campaign': fields.many2one('discount.campaign', 'Discount Campaign'),
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False, 'payment_term' : False, 'discount_campaign' : False}}
        result =  super(sale_order, self).onchange_partner_id(cr, uid, ids, part)['value']
        campaign = self.pool.get('res.partner').browse(cr, uid, part).discount_campaign.id
        result['discount_campaign'] = campaign
        return {'value': result}


sale_order()
