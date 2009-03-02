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

#######################################
# Catalog override
#######################################

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'magento_id': fields.integer('Magento product id'),
        'exportable': fields.boolean('Export to website'), 
        'updated': fields.boolean('Product updated on Magento'),
        'magento_tax_class_id': fields.integer('Magento tax class Id'),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'exportable': lambda *a: True,
        'updated': lambda *a: False,
        'magento_tax_class_id': lambda *a: 2,
    }
    
    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model']='product.product'
            datas['ids']=ids
            import wizard.magento_product_synchronize
            wizard.magento_product_synchronize.do_export(self, cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.product').write(cr, uid, ids, {'updated': False})
        return 1 

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

product_product()

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'magento_id': fields.integer('magento category id'),
        'exportable': fields.boolean('Export to website'),
        'updated': fields.boolean('Category updated on Magento'),
        'magento_product_type': fields.integer('Magento Product Type'), 
        'magento_product_attribute_set_id': fields.integer('Magento Product Attribute Set Id'), 
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'exportable':lambda *a: True,
        'updated': lambda *a: False,
        'magento_product_type': lambda *a: 0,
        'magento_product_attribute_set_id': lambda *a: 0,
    }
    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model']='product.category'
            datas['ids']=ids
            import wizard.magento_category_synchronize
            wizard.magento_category_synchronize.do_export(self, cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.category').write(cr, uid, ids, {'updated': False})
        return 1 

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)
    
product_category()

#######################################
# Sales override
#######################################

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'magento_id': fields.integer('magento order id'),
        'has_error': fields.integer('magento order error'),    
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'has_error': lambda *a: 0,
    }
sale_order()


class res_partner(osv.osv):
    _inherit = 'res.partner' 
    _columns = {
        'magento_id': fields.integer('magento partner id'), 
    }
    _defaults = {
        'magento_id': lambda *a: 0,
    }
res_partner()


class sale_shop(osv.osv):
    _inherit = 'sale.shop'
    _columns = {
        'magento_flag': fields.boolean('Magento webshop'),
    }
    _defaults = {
        'magento_flag': lambda *a: False,
    }  
sale_shop()

#######################################
# Connector
#######################################

class magento_web(osv.osv):
    _name = 'magento.web'
    _description = 'Magento Web'
    _columns = {
        'magento_flag'      : fields.boolean('magento web flag'),
        'magento_name'      : fields.char('Magento Web Name', size=64),
        'magento_url'       : fields.char('Magento Url', size=64), 
        'api_user'          : fields.char('Magento Api User', size=64),
        'api_pwd'           : fields.char('Magento Api Password', size=64),
        'auto_update'       : fields.boolean('Enhance auto update for products and category'),
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
    
    #Magento Connection
    def connect(self, cr, uid, ids, datas = {}, context = {} ):
        import xmlrpclib
        import netsvc
        connect_logger = netsvc.Logger()
        
        try:
            magento_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
            if len(magento_id) > 1 :
                raise osv.except_osv('UserError', 'You must have only one shop with Magento flag turned on')
            else :
                magento_web = self.pool.get('magento.web').browse(cr, uid, magento_id[0])
                server = xmlrpclib.ServerProxy("%sindex.php/api/xmlrpc" % magento_web.magento_url)
            
        except Exception, error:
            raise osv.except_osv("UserError", "You must have a declared website with a valid URL, a Magento username and password")   
            connect_logger.notifyChannel("Magento Connect", netsvc.LOG_ERROR, "Error : %s" % error)    
   
        try:
            session = server.login(magento_web.api_user, magento_web.api_pwd)
            
        except xmlrpclib.Fault,error:
            raise osv.except_osv("MagentoError", "Magento returned %s" % error)
        except Exception, error:
            raise osv.except_osv("ConnectionError", "Couldn't connect to Magento with URL %sindex.php/api/xmlrpc" % magento_web.magento_url)    

        return server, session

    
    #TODO Refactor with connect method
    def connect_custom_api(self, cr, uid, ids, datas = {}, context = {}):
        import xmlrpclib
        import netsvc
        connect_logger = netsvc.Logger()
        
        try:
            magento_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
            if len(magento_id) > 1 :
                raise osv.except_osv('UserError', 'You must have only one shop with Magento flag turned on')
            else :
                magento_web = self.pool.get('magento.web').browse(cr, uid, magento_id[0])
                server = xmlrpclib.ServerProxy("%sapp/code/local/Smile/OpenERPSync/openerp-synchro.php" % magento_web.magento_url)
            
        except Exception, error:
            raise osv.except_osv("UserError", "You must have a declared website with a valid URL, a Magento username and password")   
            connect_logger.notifyChannel("Magento Connect", netsvc.LOG_ERROR, "Error : %s" % error) 

        return server

magento_web()
