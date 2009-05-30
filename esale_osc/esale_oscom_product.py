##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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

from osv import fields,osv,orm
import xmlrpclib

class esale_oscom_product_manufacturer(osv.osv):
    _name = 'product.manufacturer'
    _description = 'Product Manufacturer that produces the product'
    _columns = {
                'name':fields.char('Name', size=64, required=True, select="1"),
                'manufacturer_url':fields.char('URL', size=128, select="2", translate=True),
                }
esale_oscom_product_manufacturer()


class esale_oscom_product_inherit(osv.osv):
    _inherit = 'product.product'

    _columns = {
                'product_url':fields.char('URL', size=64, translate=True),
                'in_out_stock':fields.selection([('1','In Stock'), ('0','Out Stock')], 'In/Out Stock'),
                'product_picture':fields.char('Product Picture', size=64),
                'date_available':fields.date('Available Date'),
                'manufacturer_id':fields.many2one('product.manufacturer',' Manufacturer'),
                'spe_price':fields.char('Special price', size=8),
                'exp_date':fields.datetime('Expiry date'),
                'spe_price_status':fields.selection([('1','On'), ('0','Off')], 'Status'),
                'oscom_url':fields.char('URL to OScommerce', size=256, readonly=True),

                }
    _defaults = {
                 'in_out_stock' : lambda *a:'0',
                 'spe_price_status':lambda *a:'0',
                 }

    def create(self, cr, uid, vals, context=None):
        esale_web_obj = self.pool.get('esale.oscom.web')
        esale_category_obj = self.pool.get('esale.oscom.category')

        ret_create = super(esale_oscom_product_inherit,self).create(cr, uid, vals, context)
        if ret_create:
            category_id = self.browse(cr, uid, ret_create).categ_id.id
            category_maping_ids = esale_category_obj.search(cr, uid, [('category_id','=',category_id)])
            if len(category_maping_ids):
                #print "Product CREATED. New category is mapped to OScommerce => update OScommerce products"
                self.oscom_export(cr, uid, product_ids=[ret_create], context=context)
        return ret_create

    def write(self, cr, uid, ids, vals, context=None):
        esale_category_obj = self.pool.get('esale.oscom.category')
        esale_product_obj = self.pool.get('esale.oscom.product')

        ret_write = super(esale_oscom_product_inherit,self).write(cr, uid, ids, vals, context)
        esale_product_ids = esale_product_obj.search(cr, uid, [('product_id','in',ids)])
        esale_products = esale_product_obj.browse(cr, uid, esale_product_ids)
        category_id = vals.get('categ_id', False)

        # OpenERP products mapped to OScommerce
        product_ids = [x.product_id.id for x in esale_products]
        if len(product_ids) and ret_write:
            if category_id: # Updated product category field
                category_maping_ids = esale_category_obj.search(cr, uid, [('category_id','=',category_id)])
                if len(category_maping_ids):
                    #print "New category is mapped to OScommerce => update OScommerce products"
                    self.oscom_export(cr, uid, product_ids=product_ids, context=context)
                else:
                    #print "New category is not mapped to OScommerce => delete OScommerce products"
                    esale_product_obj.unlink(cr, uid, esale_product_ids, context)
            else:
                #print "No updated product category field (same category => update OScommerce products)"
                self.oscom_export(cr, uid, product_ids=product_ids, context=context)

        # OpenERP products not mapped to OScommerce
        product_no_ids = [x for x in ids if x not in product_ids]
        if len(product_no_ids) and ret_write:
            if category_id: # Updated product category field
                category_maping_ids = esale_category_obj.search(cr, uid, [('category_id','=',category_id)])
                if len(category_maping_ids):
                    #print "Previously NOT MAPPED. New category is mapped to OScommerce => update OScommerce products"
                    self.oscom_export(cr, uid, product_ids=product_no_ids, context=context)
        return ret_write

    def unlink(self, cr, uid, ids, context=None):
        esale_product_obj = self.pool.get('esale.oscom.product')
        esale_product_ids = esale_product_obj.search(cr, uid, [('product_id','in',ids)])
        if len(esale_product_ids):
            esale_product_obj.unlink(cr, uid, esale_product_ids, context)
        ret_del = super(esale_oscom_product_inherit,self).unlink(cr, uid, ids, context)
        return ret_del

    def _check_spe_price(self, cr, uid, ids):
        products = self.browse(cr, uid, ids)
        for p in products:
            try:
                spe_price = p.spe_price
                if spe_price!=False:
                    if spe_price.find('%') > 0:
                        float(spe_price[0:-1])
                    else:
                        float(spe_price)
            except:
                return False
        return True

    _constraints = [
        (_check_spe_price, _('You can not give other value in Special Price! Please enter number with % or decimal value'), ['spe_price'])
    ]

    def oscom_export(self, cr, uid, website=None, product_ids=[], context={}):
        """Export product_ids to OScommerce website (all the websites where there are product_ids if website is not defined)"""
        esale_web_obj = self.pool.get('esale.oscom.web')
        esale_category_obj = self.pool.get('esale.oscom.category')
        esale_product_obj = self.pool.get('esale.oscom.product')
        category_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        attach_obj = self.pool.get('ir.attachment')
        pricelist_obj = self.pool.get('product.pricelist')
        tax_obj = self.pool.get('account.tax')
        manufacturer_obj = self.pool.get('product.manufacturer')

        prod_new = 0
        prod_update = 0
        prod_delete = 0
        websites_objs = []
        websites = {}
        if not website:
            products = product_obj.browse(cr, uid, product_ids)
            category_ids = [x.categ_id.id for x in products]
            category_maping_ids = esale_category_obj.search(cr, uid, [('category_id','in',category_ids)])
            category_mapings = esale_category_obj.browse(cr, uid, category_maping_ids)
            web_ids = [x.web_id.id for x in category_mapings]
            for web_id in web_ids:
                websites[web_id] = product_ids
        else:
            websites[website.id] = product_ids

        # Main loop for the web shops
        websites_objs = esale_web_obj.browse(cr, uid, websites.keys())
        for website in websites_objs:
            # print "%s/openerp-synchro.php" % website.url
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            website_url = website.url.split("/")

            # Pricelist of the web shop
            pricelist = website.shop_id.pricelist_id.id
            if not pricelist:
                raise osv.except_osv(_('User Error'), _('You must define a pricelist in the sale shop associated to the web shop!'))

            # Taxes of the web shop
            tax_maping = {}
            for oscom_tax in website.tax_ids:
                tiny_tax_id = oscom_tax.tax_id and oscom_tax.tax_id.id
                if tiny_tax_id:
                    tax_maping[oscom_tax.esale_oscom_id] = tiny_tax_id

            # Loop for the OpenERP products
            esale_products_ids = []
            web_product_ids = websites.get(website.id, False)
            products = product_obj.browse(cr, uid, web_product_ids)
            #print website.id, web_product_ids
            for product in products:
                exist_esale_products_ids = esale_product_obj.search(cr, uid, [('web_id','=',website.id), ('product_id','=',product.id)])
                if not len(exist_esale_products_ids):
                    create_dict = {
                                'web_id':website.id,
                                'name':product.name,
                                'product_id':product.id,
                                'esale_oscom_id':0
                                }
                    new_esale_product_id = esale_product_obj.create(cr, uid, create_dict)
                    esale_products_ids.append(new_esale_product_id)
                else:
                    esale_products_ids.append(exist_esale_products_ids[0])

            # Loop for the web shop products
            esale_products = esale_product_obj.browse(cr, uid, esale_products_ids)
            for esale_product in esale_products:
                # Get category
                category_id = esale_product.product_id.categ_id.id
                category_ids = esale_category_obj.search(cr, uid, [('web_id','=', website.id), ('category_id', '=', category_id)])
                if len(category_ids) > 0:
                    category_id = esale_category_obj.browse(cr, uid, category_ids[0]).esale_oscom_id
                else:
                    category_id = 0

                # Get tax
                tax_ids = [x.id for x in esale_product.product_id.taxes_id]
                tax_class_id = 0
                if tax_ids:
                    if tax_ids[0] in tax_maping.values():
                        tax_class_id = tax_maping.keys()[tax_maping.values().index(tax_ids[0])]
                webproduct = {
                    'product_id'      : esale_product.esale_oscom_id,
                    'quantity'        : product_obj._product_available(cr, uid, [esale_product.product_id.id], ['virtual_available'], False, {'shop':website.shop_id.id})[esale_product.product_id.id]['virtual_available'],
                    'model'           : esale_product.product_id.code,
                    'weight'          : float(esale_product.product_id.weight),
                    'status'          : int(esale_product.product_id.in_out_stock),
                    'tax_class_id'    : tax_class_id,
                    'category_id'     : category_id,
                    'date_available'  : esale_product.product_id.date_available or 'NULL',
                    'exp_date'        : esale_product.product_id.exp_date or 'NULL',
                    'spe_price'       : esale_product.product_id.spe_price,
                    'spe_price_status': esale_product.product_id.spe_price_status
                }

                # Get price
                if website.price_type == '0':
                    webproduct['price'] = pricelist_obj.price_get(cr, uid, [pricelist], esale_product.product_id.id, 1, 'list')[pricelist].__str__()
                    #print "LIST PRICE:::::::::::::::::::",webproduct['price']
                else:
                    tax_ids = esale_product.product_id.taxes_id
                    #print "\TAX_IDS:::::::::::::::::",tax_ids
                    if tax_ids:
                        tax_amount = tax_obj.browse(cr, uid, tax_ids[0]).amount
                    else:
                        tax_amount = 0
                    #print"\TAX BROWSE:::::::::::::::::::",tax_amount
                    t_price = (pricelist_obj.price_get(cr, uid, [pricelist], esale_product.product_id.id, 1, 'list')[pricelist]) / (1 + tax_amount)
                    webproduct['price'] = round(t_price,5).__str__()
                    #print "FROM TAX PRICE:::::::::::::", webproduct['price']

                # Get attachment
                attach_ids = attach_obj.search(cr, uid, [('res_model','=','product.product'), ('res_id', '=',esale_product.product_id.id)])
                attachs = attach_obj.browse(cr, uid, attach_ids)
                if len(attachs):
                    webproduct['haspic'] = 1
                    webproduct['picture'] = attachs[0].datas
                    webproduct['fname'] = attachs[0].datas_fname
                elif esale_product.product_id.product_picture:
                    webproduct['haspic'] = 2
                    webproduct['fname'] = esale_product.product_id.product_picture
                else:
                    webproduct['haspic'] =0

                # Get multi language attributes
                langs = {}
                manufacturer_langs = {}
                for lang in website.language_ids:
                    if lang.language_id and lang.language_id.translatable:
                        product = product_obj.browse(cr, uid, esale_product.product_id.id, {'lang': lang.language_id.code})
                        langs[str(lang.esale_oscom_id)] = {
                            'name': product.name or '',
                            'description': product.description_sale or '',
                            'url': product.product_url or '',
                        }
                        if esale_product.product_id.manufacturer_id:
                            manufacturer = manufacturer_obj.browse(cr, uid, esale_product.product_id.manufacturer_id.id, {'lang': lang.language_id.code})
                            manufacturer_langs[str(lang.esale_oscom_id)] = {
                                'manufacturers_url': manufacturer.manufacturer_url or '',
                            }

                webproduct['langs'] = langs
                webproduct['name'] = esale_product.product_id.name
                webproduct['description'] = esale_product.product_id.description_sale or ''
                webproduct['url'] = esale_product.product_id.product_url or ''

                if esale_product.product_id.manufacturer_id:
                    webproduct['manufacturers_name'] = esale_product.product_id.manufacturer_id.name
                    webproduct['manufacturers_url'] = esale_product.product_id.manufacturer_id.manufacturer_url or ''
                    webproduct['manufacturer_langs'] = manufacturer_langs
                #print "webproduct:::::::::::",webproduct

                # Sends product to web shop
                prod_id = webproduct['product_id']
                if (prod_id != 0):
                    if webproduct['spe_price']:
                        price = float(webproduct['price'])
                        spe_price = webproduct['spe_price']
                        if spe_price.find('%') > 0:
                            spe_price = spe_price[0:-1]
                            spe_price = "%.4f" % (price - (price*float(spe_price)/100))
                            webproduct['spe_price'] = spe_price
                        oscom_id = server.set_product_spe(webproduct)
                    elif not webproduct['spe_price']:
                        oscom_id = server.set_product_classical(webproduct)
                        server.del_spe_price(prod_id)
                elif (prod_id == 0):
                    if (webproduct['spe_price'] == 0):
                        oscom_id = server.set_product_classical(webproduct)
                    elif (webproduct['spe_price'] != 0):
                        oscom_id = server.set_product_spe(webproduct)

                if oscom_id != esale_product.esale_oscom_id:
                    esale_product_obj.write(cr, uid, [esale_product.id], {'esale_oscom_id': oscom_id})
                    cr.commit()
                    prod_new += 1
                else:
                    prod_update += 1

                #####################PRODUCT URL IN OSCOMMERCE###################
                esale_prod_ids = esale_product_obj.search(cr, uid, [('esale_oscom_id','=',oscom_id)])
                esale_prod = esale_product_obj.browse(cr, uid, esale_prod_ids[0])
                #print "ESALE PROD DATA (id, web, product, category):",esale_prod.id, esale_prod.web_id.id, esale_prod.product_id.id, esale_prod.product_id.categ_id.id
                prod_url = website_url[0] + "//" + website_url[2] + "/" + website_url[3] + "/" + website_url[4] + "/" +"categories.php?cPath=" + str(category_id) + "&pID=" + str(oscom_id) + "&action=new_product"
                super(esale_oscom_product_inherit, self).write(cr, uid, esale_prod.product_id.id, {'oscom_url': prod_url})

            # Remove delete products
            delete_esale_products_ids = esale_product_obj.search(cr, uid, [('web_id','=',website.id),('product_id','=',False)])
            #esale_products = esale_product_obj.browse(cr, uid, delete_esale_products_ids)
            #delete_oscom_ids = tuple([x.esale_oscom_id for x in esale_products])
            prod_delete = len(delete_esale_products_ids)
            if prod_delete:
                #ret_delete = server.remove_product({'oscom_product_ids' : delete_oscom_ids})
                #if ret_delete:
                esale_product_obj.unlink(cr, uid, delete_esale_products_ids)

        return {'prod_new':prod_new, 'prod_update':prod_update, 'prod_delete': prod_delete}


    def oscom_update_stock(self, cr, uid, website = None, product_ids=[], context={}):
        """Update stock for product_ids to OScommerce website (all the websites where there are product_ids if website  is not defined)"""
        esale_web_obj = self.pool.get('esale.oscom.web')
        esale_product_obj = self.pool.get('esale.oscom.product')
        product_obj = self.pool.get('product.product')

        websites_objs = []
        websites = {}
        if not website:
            cr.execute('select distinct(web_id) from esale_oscom_product where product_id in (%s)'%','.join([str(x) for x in product_ids]))
            web_ids = [web[0] for web in cr.fetchall()]
            websites_objs = esale_web_obj.browse(cr, uid, web_ids)
        else:
            websites_objs.append(website)
        for website in websites_objs:
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            if not product_ids:
                esale_products = website.product_ids
            else:
                esale_product_ids = esale_product_obj.search(cr, uid, [('web_id','=',website.id), ('product_id','in',product_ids)])
                esale_products = esale_product_obj.browse(cr, uid, esale_product_ids)
            for esale_product in esale_products:
                webproduct = {
                    'product_id': esale_product.esale_oscom_id,
                    'quantity': product_obj._product_available(cr, uid, [esale_product.product_id.id], ['virtual_available'], False, {'shop':website.shop_id.id})[esale_product.product_id.id]['virtual_available']
                }
                oscom_id = server.set_product_stock(webproduct)

        return {}

##    def on_change_gross_price(self, cr, uid, ids, list_price):
##        if list_price:
##            if ids:
##                product = self.pool.get('product.product').browse(cr, uid, ids[0])
##                if not product.taxes_id:
##                    VAT = 0
##                else:
##                    VAT = product.taxes_id[0].amount
##                gr_pr = list_price *(1 + VAT)
##            else:
##                raise osv.except_osv(
##                                                'Could not change the price!',
##                                                'You must first save the record and then enter price.')
##                gr_pr = 0
##        else:
##            gr_pr = 0
##
##    	return {'value':{'gross_price':gr_pr,'list_price':list_price}}
##
##
##    def on_change_list_price(self, cr, uid, ids, gross_price):
##        if gross_price:
##            if ids:
##                product = self.pool.get('product.product').browse(cr, uid, ids[0])
##                if not product.taxes_id:
##                    VAT = 0
##                else:
##                    VAT = product.taxes_id[0].amount
##                l_pr = gross_price / (1 + VAT)
##            else:
##                raise osv.except_osv(
##                                                'Could not change the price!',
##                                                'You must first save the record and then enter price.')
##                l_pr = 1
##        else:
##            l_pr = 1
##
##        return {'value':{'list_price':l_pr, 'gross_price':gross_price}}

esale_oscom_product_inherit()


#class oscom_res_currency(osv.osv):
#    _inherit='res.currency'
#    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount, round=False, context={}):
#        return super(oscom_res_corrency,self).compute(cr, uid, from_currency_id, to_currency_id, from_amount, round,context)
#oscom_res_currency()
