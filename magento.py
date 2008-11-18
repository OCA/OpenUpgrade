# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Rapha�l Valyi
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

from osv import fields,osv

#===============================================================================
#   Overrides some OpenERP objects, mainly to add magento_id fields
#===============================================================================

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'magento_id'        : fields.integer('Magento product id'),
        'exportable'        : fields.boolean('Export to website'), 
        'magento_tax_class_id'  : fields.integer('Magento tax class Id'),
    }
    _defaults = {
         'exportable':lambda *a: True,
    }
    
    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        datas['model']='product.product'
        datas['ids']=ids
        import wizard.magento_product_synchronize
        wizard.magento_product_synchronize.do_export(self, cr, uid, datas, context)
        del datas['model']
        del datas['ids']
        return 1 

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

product_product()


class sale_order(osv.osv):
    _name ='sale.order'
    _inherit = 'sale.order'
    _columns = {
        'magento_id'        : fields.integer('magento order id'),
        'has_error'          : fields.integer('magento order error'),    
    }
sale_order()


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner' 
    _columns = {
        'magento_id'        : fields.integer('magento partner id'), 
    }
res_partner()


class product_category(osv.osv):
    _name = 'product.category'
    _inherit = 'product.category'
    _columns = {
        'magento_id'        : fields.integer('magento category id'),
        'exportable'        : fields.boolean('Export to website'),
        'magento_product_type'  : fields.integer('Magento Product Type'), 
        'magento_product_attribute_set_id'  : fields.integer('Magento Product Attribute Set Id'), 
    }
    _defaults = {
         'exportable':lambda *a: True,
    }
    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        datas['model']='product.category'
        datas['ids']=ids
        import wizard.magento_category_synchronize
        wizard.magento_category_synchronize.do_export(self, cr, uid, datas, context)
        del datas['model']
        del datas['ids']
        return 1 

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)
    
product_category()


class sale_shop(osv.osv):
    _name = 'sale.shop'
    _inherit = 'sale.shop'
    _columns = {
        'magento_id'        : fields.integer('magento webshop id'),
    }  
sale_shop()


class magento_web(osv.osv):
    _name = 'magento.web'
    _description = 'Magento Web'
    _columns = {
        'magento_id'        : fields.integer('magento web id'),
        'magento_name'      : fields.char('Magento Web Name', size=64),
        'magento_url'       : fields.char('Magento Url', size=64), 
        'api_user'          : fields.char('Magento Api User', size=64),
        'api_pwd'           : fields.char('Magento Api Password', size=64),
    }
    
    def _constraint_unique(self, cr, uid, ids):
        web = self.pool.get('magento.web').search(cr, uid,[])
        if len(web) > 1 :
            return False
        else :
            return True
    
    _constraints = [
        (_constraint_unique, 'Error: The module has been designed for only one Magento Web.', [])
    ]
    
    # for lack of a better place to put this    
    def createOrders(self, cr, uid, sale_order_array):
        import netsvc
        import magento_utils
        logger = netsvc.Logger()
        logger.notifyChannel("Magento Import", netsvc.LOG_INFO, "createOrder")    

        utils = magento_utils.magento_utils()
        results = utils.createOrders(cr, uid, sale_order_array)

        return results

magento_web()
