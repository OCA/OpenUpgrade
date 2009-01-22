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
import datetime
import time
import netsvc
from osv import fields,osv
import ir
import pooler
import tools


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
                'product_logo': fields.binary('Product Logo'),
                'url': fields.char('Image URL', size=56, help="Add Product Image URL.")
}
product_product()

class specail_offer(osv.osv):
    _inherit = "product.pricelist.version"
    _columns = {
                'offer_name': fields.char('OfferName',size=64,translate=True)
	}

specail_offer()

class ecommerce_search(osv.osv):
        _name = "ecommerce.search"
        _description = "search parameters"
        _columns = {
                'name': fields.char('Search Parameter Name', size=56),
                'code': fields.char('Search Parameter Code', size=28)
                    }
        
        def searchProduct_ids(self, cr, uid, search_code):
            prd_ids =[]
            final_list = []
            obj = self.pool.get('product.product')
          
            for i in search_code.items():
                args = []
                if(i[1] != ''):
                    if(i[0] == 'name'):
                        final_list = (i[0],'ilike',str(i[1]))
                        args.append(final_list)
                        ids = obj.search(cr, uid, args)
                        prd_ids.extend(ids)
                       
                    else:
                        final_list = (i[0],'=',str(i[1]))
                        args.append(final_list)
                        ids = obj.search(cr, uid, args)
                        prd_ids.extend(ids)
       
            return prd_ids
       
ecommerce_search()

class reviews(osv.osv):
    _name="ecommerce.product.reviews"
    _rec_name="product"
    _description="Reviews about product"
    _columns={
              'product_id':fields.many2one('product.product','Product', required=True, ondelete='cascade'),
              'customer_id':fields.many2one('ecommerce.partner','Customer', required=True, ondelete='cascade'),
              'reviewdate':fields.date('Review Date'),
              'rating':fields.integer('Rating'),
              'review':fields.text('Review')
              }
    
    _defaults = {
        'reviewdate': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
reviews()

