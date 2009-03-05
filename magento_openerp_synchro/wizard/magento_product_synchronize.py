# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi
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

import wizard
import pooler
import xmlrpclib
import netsvc


def do_export(self, cr, uid, data, context):
    
    #===============================================================================
    #  Init
    #===============================================================================

    prod_new = 0
    prod_update = 0
    prod_fail = 0
    
    logger = netsvc.Logger()
    self.pool = pooler.get_pool(cr.dbname)
    product_pool = self.pool.get('product.product')
    
    mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
    mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
    (server, session) = mw.connect()
    
    #===============================================================================
    #  Getting ids
    #===============================================================================

    if data['model'] == 'ir.ui.menu':
        prod_ids = product_pool.search(cr, uid, [('exportable', '=', True)])#,('updated', '=', False)])
    else:
        prod_ids = []
        prod_not = []
        for id in data['ids']:
            exportable_product = product_pool.search(cr, uid, [('id', '=', id), ('exportable', '=', True)]) 
            if len(exportable_product) == 1:
                prod_ids.append(exportable_product[0])
            else:
                prod_not.append(id)   
            
        if len(prod_not) > 0:
            raise wizard.except_wizard(_("Error"), _("you asked to export non-exportable products : IDs %s") % prod_not)
        
    #===============================================================================
    #  Product packaging
    #===============================================================================
    #Getting the set attribute  
    #TODO: customize this code in order to pass custom attribute sets (configurable products), possibly per product
    sets = server.call(session, 'product_attribute_set.list')
    for set in sets:
        if set['name'] == 'Default':
            attr_set_id = set['set_id']
        else :
            attr_set_id = 1
    
    # splitting the prod_ids array in subarrays to avoid memory leaks in case of massive upload. Hint by Gunter Kreck
    import math
    l = 200
    f = lambda v, l: [v[i * l:(i + 1) * l] for i in range(int(math.ceil(len(v) / float(l))))]
    split_prod_id_arrays = f(prod_ids, l)
    
    for prod_ids in split_prod_id_arrays:
    
        for product in product_pool.browse(cr, uid, prod_ids, context=context):

            #Getting Magento categories
            category_tab = {'0':1}
            key = 1
            last_category = product.categ_id
            while(type(last_category.parent_id.id) == (int)):
                category_tab[str(key)] = last_category.magento_id
                last_category = self.pool.get('product.category').browse(cr, uid, last_category.parent_id.id)
                key += 1
            
            sku = (product.code or "mag") + "_" + str(product.id)
        
            product_data = {
                'name': product.name,
                'price' : product.list_price,
                'weight': (product.weight_net or 0),
                'category_ids': category_tab,
                'description' : (product.description or _("description")),
                'short_description' : (product.description_sale or _("short description")),
                'websites':['base'],
                'tax_class_id': product.magento_tax_class_id or 2,
                'status': 1,
            }
            
            stock_data = {
                'qty': product.virtual_available,
                'is_in_stock': product.virtual_available,
            }
            
            #===============================================================================
            #  Product upload to Magento
            #===============================================================================
            try:
                #Create
                if(product.magento_id == 0):
                    new_id = server.call(session, 'product.create', ['simple', attr_set_id, sku, product_data])
                    product_pool.write_magento_id(cr, uid, product.id, {'magento_id': new_id})
                    server.call(session, 'product_stock.update', [sku, stock_data])
                    logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully created product with OpenERP id %s and Magento id %s") % (product.id, new_id))
                    prod_new += 1
                #Or Update
                else:
                    server.call(session, 'product.update', [sku, product_data])
                    server.call(session, 'product_stock.update', [sku, stock_data])
                    logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully updated product with OpenERP id %s and Magento id %s") % (product.id, product.magento_id))
                    prod_update += 1
                     
            except xmlrpclib.Fault, error:
                #If fail, try to create
                if error.faultCode == 101: #turns out that the product doesn't exist in Magento (might have been deleted), try to create a new one.
                    try:
                        new_id = server.call(session, 'product.create', ['simple', attr_set_id, sku, product_data])
                        product_pool.write_magento_id(cr, uid, product.id, {'magento_id': new_id})
                        server.call(session, 'product_stock.update', [sku, stock_data])
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully created product with OpenERP id %s and Magento id %s") % (product.id, new_id))
                        prod_new += 1
                    except xmlrpclib.Fault, error:
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_ERROR, _("Magento API return an error on product id %s . Error %s") % (product.id, error))
                        prod_fail += 1
                else:
                    logger.notifyChannel(_("Magento Export"), netsvc.LOG_ERROR, _("Magento API return an error on product id %s . Error %s") % (product.id, error))
                    prod_fail += 1
            except Exception, error:
                raise wizard.except_wizard(_("OpenERP Error"), _("An error occured : %s ") % error)

        
    server.endSession(session)
    return {'prod_new':prod_new, 'prod_update':prod_update, 'prod_fail':prod_fail}


#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Product and Stock Synchronization">
    <separator string="Products exported" colspan="4" />
    <field name="prod_new"/>
    <field name="prod_update"/>
    <field name="prod_fail"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New products', 'readonly': True, 'type':'integer'},
    'prod_update': {'string':'Updated products', 'readonly': True, 'type':'integer'},
    'prod_fail': {'string':'Failed to export products', 'readonly': True, 'type':'integer'},
}

class wiz_magento_product_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_product_synchronize('magento.products.sync');
