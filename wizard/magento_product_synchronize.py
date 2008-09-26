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

import wizard
import pooler
import xmlrpclib
import netsvc



#===============================================================================
#    Information Form & Fields
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Product and Stock Synchronization">
    <separator string="Products exported" colspan="4" />
    <field name="prod_new"/>
    <field name="prod_update"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New products', 'readonly': True, 'type':'integer'},
    'prod_update': {'string':'Updated products', 'readonly': True, 'type':'integer'},
}


def _do_export(self, cr, uid, data, context):
    
    #===============================================================================
    #  Init
    #===============================================================================

    prod_new = 0
    prod_update = 0
    logger = netsvc.Logger()
    pool = pooler.get_pool(cr.dbname)

    if data['model'] == 'ir.ui.menu':
        prod_ids = pool.get('product.product').search(cr, uid, [('exportable','=',True)])
    else:
        prod_ids=[]
        prod_not=[]
        for id in data['ids']:
            exportable_product=pool.get('product.product').search(cr, uid, [('id','=',id),('exportable','=',True)]) 
            if len(exportable_product)==1: prod_ids.append(exportable_product[0])
            else : prod_not.append(id)   
            
        if len(prod_not) > 0: raise wizard.except_wizard("Error", "you asked to export non-exportable products : IDs %s" % prod_not)

    #===============================================================================
    # Server communication
    #===============================================================================
    
    magento_web_id=pool.get('magento.web').search(cr,uid,[('magento_id','=',1)])
    try:
        magento_web=pool.get('magento.web').browse(cr,uid,magento_web_id[0])
        server = xmlrpclib.ServerProxy("%sindex.php/api/xmlrpc" % magento_web.magento_url)   
    except:
        raise wizard.except_wizard("UserError", "You must have a declared website with a valid URL, a Magento username and password")
    try:
        try:
            session=server.login(magento_web.api_user, magento_web.api_pwd)
        except xmlrpclib.Fault,error:
            raise wizard.except_wizard("MagentoError", "Magento returned %s" % error)
    except:
        raise wizard.except_wizard("ConnectionError", "Couldn't connect to Magento with URL %sindex.php/api/xmlrpc" % magento_web.magento_url)
        
    #===============================================================================
    #  Product packaging
    #===============================================================================
    for product in pool.get('product.product').browse(cr, uid, prod_ids, context=context):
    
        #Getting Magento categories
        category_tab ={'0':1}
        key=1
        last_category = product.categ_id
        while(type(last_category.parent_id.id) == (int)):
            category_tab[str(key)]=last_category.magento_id
            last_category=pool.get('product.category').browse(cr, uid, last_category.parent_id.id)
            key=key+1

        #Getting tax class
        tax_class_id = 1    
        if(product.magento_tax_class_id != 0):
            tax_class_id=product.magento_tax_class_id
        
        #Getting the set attribute  
        #TODO: customize this code in order to pass custom attribute sets (configurable products)  
        sets = server.call(session, 'product_attribute_set.list')
        for set in sets:
            if set['name']=='Default':
                attr_set_id=set['set_id'] 
        
        #product Data        
        sku='mag'+str(product.id)  
        product_data={
            'name': product.name,
            'price' : product.list_price, 
            'weight': product.weight_net, 
            'category_ids': category_tab, #fix product.categ_id.magento_id ), 
            'description' : product.description,
            'short_description' : product.description_sale,
            'websites':['base'],
            'tax_class_id': tax_class_id,
            'status': 1,
        }
        
        stock_data={
            'qty': product.virtual_available,
            'is_in_stock': product.virtual_available,
        }
        
        #===============================================================================
        #  Product upload to Magento
        #===============================================================================
        try:
            if(product.magento_id == 0):
                new_id=server.call(session, 'product.create', ['simple',attr_set_id, sku, product_data])
                pool.get('product.product').write_magento_id(cr, uid, product.id, {'magento_id': new_id})
                server.call(session,'product_stock.update',[sku,stock_data])
                prod_new += 1
            else:
                server.call(session, 'product.update',[sku,product_data])
                server.call(session,'product_stock.update',[sku,stock_data])
                prod_update += 1
                 
        except xmlrpclib.Fault,error:
            logger.notifyChannel("Magento Export", netsvc.LOG_ERROR, "Magento API return an error on product id %s . Error %s" % (product.id,error))   
    
    server.endSession(session)            
    return {'prod_new':prod_new, 'prod_update':prod_update}

#===============================================================================
#   Wizard Declaration
#===============================================================================

class wiz_magento_product_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [_do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_product_synchronize('magento.products.sync');
