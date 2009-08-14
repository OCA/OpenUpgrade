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
import xmlrpclib

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'magento_id': fields.integer('Magento product id'),
        'exportable': fields.boolean('Export to website'),
        'updated': fields.boolean('Product updated on Magento'),
        'magento_tax_class_id': fields.integer('Magento tax class id'),
        'image': fields.binary('Image', help='Image of the product (jpg or png). The same image will be set as thumbnail, small image and normal image. To change the product image, first delete the old one and save the product and then add the new one and save the product. Note that this image is optional, it can be left empty and manage the product images from Magento.'),
        'image_name': fields.char('Image name', size=64, help="Image name created by Magento"),
        'image_label': fields.char('Image label', size=64, help="Image label in the website. Left empty to take the product name as image label."),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'exportable': lambda *a: True,
        'updated': lambda *a: False,
        'magento_tax_class_id': lambda *a: 2,
    }

    def write_magento(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        if not mw_id:
            return 1
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            for p in self.browse(cr, uid, ids, context=context):
                if p.exportable:
                    self.magento_export(cr, uid, [p.id], context)
                else:
                    if p.magento_id:
                        self.magento_delete(cr, uid, [p.id], context)
                    super(osv.osv, self).write(cr, uid, [p.id], {'updated': False, 'magento_id':0})
        else :
            super(osv.osv, self).write(cr, uid, ids, {'updated': False})
        return 1

    def create(self, cr, uid, datas, context = {}):
        id = super(osv.osv, self).create(cr, uid, datas, context=context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        if not mw_id:
            return id
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if datas.has_key('exportable') and not datas['exportable'] or not mw.auto_update :
            super(osv.osv, self).write(cr, uid, [id], {'updated': False})
        else :
            self.magento_export(cr, uid, [id], context)
        return id

    def unlink(self, cr, uid, ids, context = {}):
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        if mw_id:
            mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
            if mw.auto_update :
                self.magento_delete(cr, uid, ids, context)
        return super(osv.osv, self).unlink(cr, uid, ids)

    def magento_delete(self, cr, uid, ids, context):
        logger = netsvc.Logger()
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        (server, session) = mw.connect()
        for p in self.browse(cr, uid, ids, context=context):
            if p.magento_id:
                server.call(session, 'product.delete', [p.magento_id])
                logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully deleted product with OpenERP id %s and Magento id %s") % (p.id, p.magento_id))
        server.endSession(session)

    def magento_export(self, cr, uid, prod_ids, context):
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

        #===============================================================================
        #  Product pricelists
        #===============================================================================
        pricelist_obj = self.pool.get('product.pricelist')
        pl_default_id = pricelist_obj.search(cr, uid, [('magento_default', '=', True)])
        if len(pl_default_id) != 1:
            raise osv.except_osv(_("User Error"), _("You have not set any default pricelist to compute the Magento general prices (the standard prices of each product)"))
        pl_other_ids = pricelist_obj.search(cr, uid, [('magento_id', '<>', 0)])

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

                # Product data
                product_data = {
                    'name': product.name,
                    'price' : pricelist_obj.price_get(cr, uid, pl_default_id, product.id, 1.0)[pl_default_id[0]],
                    'weight': (product.weight_net or 0),
                    'category_ids': category_tab,
                    'description' : (product.description or _("description")),
                    'short_description' : (product.description_sale or _("short description")),
                    'websites':['base'],
                    'tax_class_id': product.magento_tax_class_id or 2,
                    'status': product.active and 1 or 2,
                    'meta_title': product.name,
                    'meta_keyword': product.name,
                    'meta_description': product.description_sale and product.description_sale[:255],
                }

                # Stock data
                stock_data = {
                    'qty': product.virtual_available,
                    'is_in_stock': product.virtual_available,
                }

                # Pricelist data (tier prices)
                prices_data = []
                for pl_id, price in pricelist_obj.price_get(cr, uid, pl_other_ids, product.id, 1.0).iteritems():
                    pl = pricelist_obj.browse(cr, uid, pl_id, context=context)
                    prices_data.append({'website': 'all', 'customer_group_id': pl.magento_id, 'qty': 1, 'price': price})

                # Image data
                image_name = ''
                image_data = {}
                if product.image:
                    image_data = {
                        'file': {'content': product.image, 'mime': 'image/jpeg'},
                        'label': product.image_label or product.name,
                        #'position': 0,
                        'types': ['image', 'small_image', 'thumbnail'],
                        'exclude': 0,
                    }

                updated = True
                #===============================================================================
                #  Product upload to Magento
                #===============================================================================
                try:
                    #Create
                    if(product.magento_id == 0):
                        new_id = server.call(session, 'product.create', ['simple', attr_set_id, sku, product_data])
                        server.call(session, 'product_stock.update', [sku, stock_data])
                        if prices_data:
                            server.call(session, 'product_tier_price.update', [sku, prices_data])
                        if image_data:
                            image_name = server.call(session, 'product_media.create', [sku, image_data])
                        self.write_magento(cr, uid, product.id, {'magento_id': new_id, 'image_name': image_name})
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully created product with OpenERP id %s and Magento id %s") % (product.id, new_id))
                        prod_new += 1
                    #Or Update
                    else:
                        server.call(session, 'product.update', [sku, product_data])
                        server.call(session, 'product_stock.update', [sku, stock_data])
                        server.call(session, 'product_tier_price.update', [sku, prices_data])
                        if image_data and not product.image_name: # Image added
                            image_name = server.call(session, 'product_media.create', [sku, image_data])
                            self.write_magento(cr, uid, product.id, {'image_name': image_name})
                        if not image_data and product.image_name: # Image removed
                            server.call(session, 'product_media.remove', [sku, product.image_name])
                            self.write_magento(cr, uid, product.id, {'image_name': ''})
                        logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully updated product with OpenERP id %s and Magento id %s") % (product.id, product.magento_id))
                        prod_update += 1

                except xmlrpclib.Fault, error:
                    #If fail, try to create
                    if error.faultCode == 101: #turns out that the product doesn't exist in Magento (might have been deleted), try to create a new one.
                        try:
                            new_id = server.call(session, 'product.create', ['simple', attr_set_id, sku, product_data])
                            server.call(session, 'product_stock.update', [sku, stock_data])
                            if prices_data:
                                server.call(session, 'product_tier_price.update', [sku, prices_data])
                            if image_data:
                                image_name = server.call(session, 'product_media.create', [sku, image_data])
                            self.write_magento(cr, uid, product.id, {'magento_id': new_id, 'image_name': image_name})
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
                    raise osv.except_osv(_("OpenERP Error"), _("An error occurred : %s ") % error)

                self.write_magento(cr, uid, product.id, {'updated': updated})

        server.endSession(session)
        return {'prod_new':prod_new, 'prod_update':prod_update, 'prod_fail':prod_fail}

product_product()


class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'magento_id': fields.integer('Magento category id'),
        'exportable': fields.boolean('Export to website'),
        'updated': fields.boolean('Category updated on Magento'),
        'magento_product_type': fields.integer('Magento product type'),
        'magento_product_attribute_set_id': fields.integer('Magento product attribute set id'),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'exportable':lambda *a: True,
        'updated': lambda *a: False,
        'magento_product_type': lambda *a: 0,
        'magento_product_attribute_set_id': lambda *a: 0,
    }

    def write_magento(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        if not mw_id:
            return 1
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            for c in self.browse(cr, uid, ids, context=context):
                if c.exportable:
                    self.magento_export(cr, uid, [c.id], context)
                else:
                    if c.magento_id:
                        self.magento_delete(cr, uid, [c.id], context)
                    super(osv.osv, self).write(cr, uid, [c.id], {'updated': False, 'magento_id':0})
        else :
            super(osv.osv, self).write(cr, uid, ids, {'updated': False})
        return 1

    def create(self, cr, uid, datas, context = {}):
        id = super(osv.osv, self).create(cr, uid, datas, context=context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        if not mw_id:
            return id
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if datas.has_key('exportable') and not datas['exportable'] or not mw.auto_update :
            super(osv.osv, self).write(cr, uid, [id], {'updated': False})
        else :
            self.magento_export(cr, uid, [id], context)
        return id

    def unlink(self, cr, uid, ids, context = {}):
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        if mw_id:
            mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
            if mw.auto_update :
                self.magento_delete(cr, uid, ids, context)
        return super(osv.osv, self).unlink(cr, uid, ids)

    def magento_delete(self, cr, uid, ids, context):
        logger = netsvc.Logger()
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        (server, session) = mw.connect()
        for c in self.browse(cr, uid, ids, context=context):
            if c.magento_id:
                server.call(session, 'category.delete', [c.magento_id])
                logger.notifyChannel(_("Magento Export"), netsvc.LOG_INFO, _("Successfully deleted category with OpenERP id %s and Magento id %s") % (c.id, c.magento_id))
        server.endSession(session)

    def magento_export(self, cr, uid, categ_ids, context):
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
                    'default_sort_by': 'name',
                    'available_sort_by': 'name',
            }
            updated = True
            #===============================================================================
            #  Category upload to Magento
            #===============================================================================
            try:
                if(category.magento_id == 0):
                    new_id = server.call(session,'category.create', [magento_parent_id, category_data])
                    self.write_magento(cr, uid, category.id, {'magento_id': new_id})
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
                        self.write_magento(cr, uid, category.id, {'magento_id': new_id})
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
                raise osv.except_osv(_("OpenERP Error"), _("An error occurred : %s ") % error)

            self.write_magento(cr, uid, category.id, {'updated': updated})

        server.endSession(session)
        return {'categ_new':categ_new, 'categ_update':categ_update, 'categ_fail':categ_fail }

product_category()