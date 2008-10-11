# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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
    
    def action_done(self, cr, uid, ids, context=None):
		# need to make perfect checking
		# remaining to check sale condition
		# need Improvement
        for campaign in self.browse(cr, uid, ids):	
	        invoice_obj = self.pool.get('account.invoice')
	        cr.execute("SELECT id from account_invoice where (date_invoice BETWEEN %s AND %s) AND type = 'out_invoice' AND state = 'open'" , (campaign.date_start,campaign.date_stop,))
	        invoice_ids = cr.fetchall()
	        for invoice_id in invoice_ids:
	            invoice = invoice_obj.browse(cr, uid, invoice_id[0])
	            if invoice.partner_id.discount_campaign.id == campaign.id:
	                for line in invoice.invoice_line:
	                    for discount_line in campaign.line_ids:							
	                        if discount_line.condition_category_id.id== line.product_id.categ_id.id or discount_line.condition_product_id.id== line.product_id.id or discount_line.condition_quantity >= line.quantiny:	
	                            invoice_vals = {
	                                    'name': discount_line.name,
	                                    'origin': discount_line.name ,
	                                    'type': 'out_refund',
	                                    'account_id': invoice.account_id.id,
	                                    'partner_id': invoice.partner_id.id,
	                                    'address_invoice_id': invoice.address_invoice_id.id,
	                                    'address_contact_id': invoice.address_contact_id.id,
	                                    'comment': invoice.comment,
	                                    }
	                            new_invoice_id = invoice_obj.create(cr, uid, invoice_vals,
	                        context=context)
	                            invoice_line_id = self.pool.get('account.invoice.line').create(cr, uid,  {
	                                 'name': line.name,
	                                'invoice_id': new_invoice_id,
	                                'uos_id': line.uos_id.id,
	                                'product_id': line.product_id.id,
	                                'account_id': line.account_id.id,
	                                'price_unit': line.price_unit *(discount_line.discount /100) ,
	                                'discount': 0.0,
	                                'quantity': line.quantity,
	                                'account_analytic_id': line.account_analytic_id.id,
	                                }, context=context)
                               
        return True
discount_campaign()

class discount_campaign_line(osv.osv):
    _name = "discount.campaign.line"
    _columns = {
        'name': fields.char('Name', size=60),
        'condition_sale': fields.char('Sale Condition', size = 60),
        'condition_category_id': fields.many2one('product.category', 'Category'),
        'condition_product_id' : fields.many2one('product.product', 'Product'),
        'condition_quantity' : fields.float('Quantity'),
        'discount' : fields.float('Discount'),
        'discount_id': fields.many2one('discount.campaign', 'Discount Lines'),
    }
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
