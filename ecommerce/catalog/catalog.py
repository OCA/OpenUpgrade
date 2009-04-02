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
import time

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'product_logo': fields.binary('Product Logo')
    }
product_product()

class ecommerce_specail_offer(osv.osv):
    _inherit = "product.pricelist.version"
    _columns = {
        'offer_name': fields.char('Offer Name', size=64, translate=True)
    }
ecommerce_specail_offer()

class ecommerce_search(osv.osv):
    _name = "ecommerce.search"
    _description = "search parameters"
    _columns = {
        'name': fields.char('Name', size=56, required= True, help="Search parameter name which you want to display at website"),
        'code': fields.many2one('ir.model.fields','Product fields', required=True, domain=[('model','=','product.template')])
    }
          
    def searchproducts(self, cr, uid, search_code):

        prd_ids = []
        final_list = []
        send_ids = []
        obj = self.pool.get('product.product')
        for i in search_code.items():
            args = []
            if(i[1] != ''):
                if(i[0] == 'name'):
                    final_list = (i[0], 'ilike', str(i[1]))
                    args.append(final_list)
                    ids = obj.search(cr, uid, args)
                    prd_ids.extend(ids)
                else:
                    final_list = (i[0], '=', str(i[1]))
                    args.append(final_list)
                    ids = obj.search(cr, uid, args)
                    prd_ids.extend(ids)
        for item in prd_ids:
            if not item in send_ids:
                send_ids.append(item) 
        return send_ids
    
ecommerce_search()

class ecommerce_reviews(osv.osv):
    _name = "ecommerce.product.reviews"
    _rec_name = "product_id"
    _description = "Reviews about product"
    _columns = {
        'product_id': fields.many2one('product.product','Product',
                                       required=True, ondelete='cascade'),
        'customer_id': fields.many2one('ecommerce.partner','Customer',
                                        required=True, ondelete='cascade'),
        'reviewdate': fields.date('Review Date'),
        'rating': fields.integer('Rating'),
        'review': fields.text('Review')
    }
    
    _defaults = {
        'reviewdate': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
ecommerce_reviews()

