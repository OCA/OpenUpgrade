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

