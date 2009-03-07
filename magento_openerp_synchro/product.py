# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# Copyright (c) 2009 Zikzakmedia S.L. (http://www.zikzakmedia.com) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi, Jordi Esteve
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
import netsvc

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
            self.do_export(cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.product').write(cr, uid, ids, {'updated': False})
        return 1 

    def create(self, cr, uid, datas, context = {}):
        id = super(osv.osv, self).create(cr, uid, datas, context=context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model'] = 'product.product'
            datas['ids'] = [id]
            self.do_export(cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.product').write(cr, uid, [id], {'updated': False})
        return id

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

    def do_export(self, cr, uid, data, context):
        #===============================================================================
        #  Init
        #===============================================================================
        prod_new = 0
        prod_update = 0
        prod_fail = 0

        logger = netsvc.Logger()
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        (server, session) = mw.connect()

        #===============================================================================
        #  Getting ids
        #===============================================================================
        if data['model'] == 'ir.ui.menu':
            prod_ids = self.search(cr, uid, [('exportable', '=', True)])#,('updated', '=', False)])
        else:
            prod_ids = []
            prod_not = []
            for id in data['ids']:
                exportable_product = self.search(cr, uid, [('id', '=', id), ('exportable', '=', True)])
                if len(exportable_product) == 1:
                    prod_ids.append(exportable_product[0])
                else:
                    prod_not.append(id)

            # Produces an error when writting a non exportable product
            #if len(prod_not) > 0:
            #    raise osv.except_osv(_("Error"), _("you asked to export non-exportable products : IDs %s") % prod_not)

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

            for product in self.browse(cr, uid, prod_ids, context=context):

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
                updated = True
                #===============================================================================
                #  Product upload to Magento
                #===============================================================================
                try:
                    #Create
                    if(product.magento_id == 0):
                        new_id = server.call(session, 'product.create', ['simple', attr_set_id, sku, product_data])
                        self.write_magento_id(cr, uid, product.id, {'magento_id': new_id})
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
                            self.write_magento_id(cr, uid, product.id, {'magento_id': new_id})
                            server.call(session, 'product_stock.update', [sku, stock_data])
                            logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully created product with OpenERP id %s and Magento id %s") % (product.id, new_id))
                            prod_new += 1
                        except xmlrpclib.Fault, error:
                            logger.notifyChannel(_("Magento Export"), netsvc.LOG_ERROR, _("Magento API return an error on product id %s . Error %s") % (product.id, error))
                            updated = False
                            prod_fail += 1
                    else:
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_ERROR, _("Magento API return an error on product id %s . Error %s") % (product.id, error))
                        updated = False
                        prod_fail += 1
                except Exception, error:
                    raise osv.except_osv(_("OpenERP Error"), _("An error occured : %s ") % error)

                self.write_magento_id(cr, uid, product.id, {'updated': updated})

        server.endSession(session)
        return {'prod_new':prod_new, 'prod_update':prod_update, 'prod_fail':prod_fail}

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
            self.do_export(cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.category').write(cr, uid, ids, {'updated': False})
        return 1

    def create(self, cr, uid, datas, context = {}):
        id = super(osv.osv, self).create(cr, uid, datas, context=context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model'] = 'product.category'
            datas['ids'] = [id]
            self.do_export(cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.category').write(cr, uid, [id], {'updated': False})
        return id

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

    def do_export(self, cr, uid, data, context):
        #===============================================================================
        #  Init
        #===============================================================================
        categ_new = 0
        categ_update = 0
        categ_fail = 0

        logger = netsvc.Logger()
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        (server, session) = mw.connect()

        #===============================================================================
        #  Getting ids
        #===============================================================================
        if data['model'] == 'ir.ui.menu':
            categ_ids = self.search(cr, uid, [('exportable', '=', True)])
        else:
            categ_ids=[]
            categ_not=[]
            for id in data['ids']:
                exportable_category = self.search(cr, uid, [('id', '=', id), ('exportable', '=', True)])
                if len(exportable_category) == 1:
                    categ_ids.append(exportable_category[0])
                else:
                    categ_not.append(id)

            # Produces an error when writting a non exportable category
            #if len(categ_not) > 0:
            #    raise osv.except_osv(_("Error"), _("you asked to export non-exportable categories : IDs %s") % categ_not)

        #===============================================================================
        #  Category packaging
        #===============================================================================
        categories = self.browse(cr, uid, categ_ids, context=context)
        categories.sort(lambda x, y : (int(x.parent_id) or 0) - int(y.parent_id))

        for category in categories :

            path=''             #construct path
            magento_parent_id=1 #root catalog
            if(type(category.parent_id.id) == (int)): #if not root category
                last_parent=self.browse(cr, uid, category.parent_id.id)
                magento_parent_id=last_parent.magento_id
                path= str(last_parent.magento_id)

                while(type(last_parent.parent_id.id) == (int)):
                    last_parent=self.browse(cr, uid, last_parent.parent_id.id)
                    path=str(last_parent.magento_id)+'/'+path

            path='1/'+path
            path=path.replace("//","/")
            if path.endswith('/'):
                path=path[0:-1]

            category_data = {
                    'name' : category.name,
                    'path' : path,
                    'is_active' : 1,
            }
            updated = True
            #===============================================================================
            #  Category upload to Magento
            #===============================================================================
            try:
                if(category.magento_id == 0):
                    new_id = server.call(session,'category.create', [magento_parent_id, category_data])
                    self.write_magento_id(cr, uid, category.id, {'magento_id': new_id})
                    logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully created category with OpenERP id %s and Magento id %s") % (category.id, new_id))
                    categ_new += 1

                else:
                    # The path must include magento_id at the end when a category is updated
                    category_data['path'] = category_data['path'] + '/' + str(category.magento_id)
                    server.call(session,'category.update', [category.magento_id, category_data])
                    logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully updated category with OpenERP id %s and Magento id %s") % (category.id, category.magento_id))
                    categ_update += 1

            except xmlrpclib.Fault, error:
                if error.faultCode == 102: #turns out that the category doesn't exist in Magento (might have been deleted), try to create a new one.
                    try:
                        new_id = server.call(session,'category.create', [magento_parent_id, category_data])
                        self.write_magento_id(cr, uid, category.id, {'magento_id': new_id})
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully created category with OpenERP id %s and Magento id %s") % (category.id, new_id))
                        categ_new += 1

                    except xmlrpclib.Fault, error:
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_ERROR, _("Magento API return an error on category id %s . Error %s") % (category.id, error))
                        updated = False
                        categ_fail += 1
                else:
                    logger.notifyChannel(_("Magento Export"), netsvc.LOG_ERROR, _("Magento API return an error on category id %s . Error %s") % (category.id, error))
                    updated = False
                    categ_fail += 1

            except Exception, error:
                raise osv.except_osv(_("OpenERP Error"), _("An error occured : %s ") % error)

            self.write_magento_id(cr, uid, category.id, {'updated': updated})

        server.endSession(session)
        return {'categ_new':categ_new, 'categ_update':categ_update, 'categ_fail':categ_fail }

product_category()