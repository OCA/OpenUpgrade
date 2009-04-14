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
#class esale_oscom_product_manyfacture(osv.osv):
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
    def write(self, cr, user, ids, vals, context=None):
        ret_write = super(esale_oscom_product_inherit,self).write(cr, user, ids, vals, context)
        esale_product_ids = self.pool.get('esale.oscom.product').search(cr, user, [('product_id','in',ids)])
        category_id = vals.get('categ_id', False)
        if len(esale_product_ids) and category_id and ret_write:
            category_maping_ids = self.pool.get('esale.oscom.category').search(cr, user, [('category_id','=',category_id)])
            if len(category_maping_ids):
                esale_product_datas = self.pool.get('esale.oscom.product').read(cr, user, esale_product_ids, ['product_id'])
                product_ids = [x.get('product_id')[0] for x in esale_product_datas]
                self.oscom_export(cr, user, product_ids=product_ids, context=context)
            else:
                self.pool.get('esale.oscom.product').unlink(cr, user, esale_product_ids, context)
        return ret_write

    def unlink(self, cr, uid, ids, context=None):
        esale_product_ids = self.pool.get('esale.oscom.product').search(cr, uid, [('product_id','in',ids)])
        ret_del = super(esale_oscom_product_inherit,self).unlink(cr, uid, ids, context)
        if len(esale_product_ids) and ret_del:
            self.pool.get('esale.oscom.product').unlink(cr, uid, esale_product_ids, context)
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
                    #end if spe_price.find('%'):
                #end if spe_price:
            except:
                return False
            #end try:
        #end for p in products:
        return True

    _constraints = [
        (_check_spe_price, _('You can not give other value in Special Price! Please enter number with % or decimal value'), ['spe_price'])
    ]

    def oscom_export(self, cr, uid, website=None, product_ids=[], context={}):
        """Export product_ids to OScommerce website (all the websites where there are product_ids if website is not defined)"""
        prod_new = 0
        prod_update = 0
        websites_objs = []
        websites = {}
        if not website:
            products_datas = self.pool.get('product.product').read(cr, uid, product_ids, ['categ_id'])
            category_ids = [x.get('categ_id')[0] for x in products_datas]
            category_maping_ids = self.pool.get('esale.oscom.category').search(cr, uid, [('category_id','in',category_ids)])
            category_maping_datas = self.pool.get('esale.oscom.category').read(cr, uid, category_maping_ids, ['web_id'])
            web_ids = [x.get('web_id')[0] for x in category_maping_datas]
            for web_id in web_ids:
                websites[web_id] = product_ids
            #end for web_id in web_ids:
        else:
            websites[website.id] = product_ids
        #end if not website:
        websites_objs = self.pool.get('esale.oscom.web').browse(cr, uid, websites.keys())
        for website in websites_objs:
            pricelist = website.shop_id.pricelist_id.id
            if not pricelist:
                raise osv.except_osv(_('User Error'), _('You must define a pricelist in the sale shop associated to the web shop!'))
            esale_products_ids = []
            # print "%s/openerp-synchro.php" % website.url
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)

            tax_maping = {}
            for oscom_tax in website.tax_ids:
                tiny_tax_id = oscom_tax.tax_id and oscom_tax.tax_id.id
                if tiny_tax_id:
                    tax_maping[oscom_tax.esale_oscom_id] = tiny_tax_id
                #end if tax_ids:
            #end for oscom_tax in website.tax_ids:
            web_product_ids = websites.get(website.id, False)
            product_objs = self.pool.get('product.product').browse(cr, uid, web_product_ids)
            for product in product_objs:
                exist_esale_products_ids = self.pool.get('esale.oscom.product').search(cr, uid, [('web_id','=',website.id), ('product_id','=',product.id)])
                if not len(exist_esale_products_ids):
                    create_dict = {
                                'web_id':website.id,
                                'name':product.name,
                                'product_id':product.id,
                                'esale_oscom_id':0
                                }
                    new_esale_product_id = self.pool.get('esale.oscom.product').create(cr, uid, create_dict)
                    esale_products_ids.append(new_esale_product_id)
                else:
                    esale_products_ids.append(exist_esale_products_ids[0])
                #end if not len(esale_products):
            #end for product in product_objs:

            esale_products_objs = self.pool.get('esale.oscom.product').browse(cr, uid, esale_products_ids)

            for oscom_product in esale_products_objs:
                attachs = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','product.product'), ('res_id', '=',oscom_product.product_id.id)])
                data = self.pool.get('ir.attachment').read(cr, uid, attachs)
                category_id = False
                if type(oscom_product.product_id.categ_id) == type(1):
                    category_id = self.pool.get('product.category').browse(cr, uid, oscom_product.product_id.categ_id).id
                else:
                    category_id = oscom_product.product_id.categ_id.id
                category_ids=self.pool.get('esale.oscom.category').search(cr, uid, [('web_id','=', website.id), ('category_id', '=', category_id)])

                if len(category_ids)>0:
                    category_id= self.pool.get('esale.oscom.category').read(cr, uid, category_ids, ['esale_oscom_id'])[0]['esale_oscom_id']
                else:
                    category_id=0

                print [pricelist], oscom_product.id, 1, 'list'

                tax_ids = []
                for x in oscom_product.product_id.taxes_id:
                    if type(x) == type(1):
                        tax_ids.append(x)
                    else:
                        tax_ids.append(x.id)

                tax_class_id = 0
                if tax_ids:
                    if tax_ids[0] in tax_maping.values():
                        tax_class_id = tax_maping.keys()[tax_maping.values().index(tax_ids[0])]
                    #end if tax_ids in tax_maping.values():
                #end if tax_ids:
                webproduct={
                    'product_id'      : oscom_product.esale_oscom_id,
                    'quantity'        : self.pool.get('product.product')._product_available(cr, uid, [oscom_product.product_id.id], ['virtual_available'], False, {'shop':website.shop_id.id})[oscom_product.product_id.id]['virtual_available'],
                    'model'           : oscom_product.product_id.code,
                    #'price'           : self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], oscom_product.product_id.id, 1, 'list')[pricelist].__str__(),
                    'weight'          : float(oscom_product.product_id.weight),
                    #'tax_class_id'    : oscom_product.esale_oscom_tax_id,
                    'status'          : int(oscom_product.product_id.in_out_stock),
                    'tax_class_id'    : tax_class_id,
                    'category_id'     : category_id,
                    'date_available'  : oscom_product.product_id.date_available or 'NULL',
                    'exp_date'        : oscom_product.product_id.exp_date or 'NULL',
                    'spe_price'       : oscom_product.product_id.spe_price,
                    'spe_price_status': oscom_product.product_id.spe_price_status
                }
                print "webproduct:::::::::::",webproduct
                oscom_prod_obj = self.pool.get('esale.oscom.product')
                oscom_prod_ids = oscom_prod_obj.search(cr, uid, [('id','=',oscom_product.id)])
                oscom_prod_data = oscom_prod_obj.read(cr, uid, oscom_prod_ids)
                if website.price_type == '0':
                    #print"HERE"
                    webproduct['price'] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], oscom_product.product_id.id, 1, 'list')[pricelist].__str__()
                    #print "LIST PRICE:::::::::::::::::::",webproduct['price']
                else:
                    #print"HERE2"
                    tax_ids = oscom_product.product_id.taxes_id
                    #print "\TAX_IDS:::::::::::::::::",tax_ids
                    if tax_ids:
                        tax_amount = self.pool.get('account.tax').browse(cr, uid, tax_ids[0]).amount
                    else:
                        tax_amount = 0
                    #print"\TAX BROWSE:::::::::::::::::::",tax_amount
                    t_price = (self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], oscom_product.product_id.id, 1, 'list')[pricelist]) / (1 + tax_amount)
                    webproduct['price'] = round(t_price,5).__str__()

                    #print "FROM TAX PRICE:::::::::::::", webproduct['price']

                if len(data):
                    webproduct['haspic'] = 1
                    webproduct['picture'] = data[0]['datas']
                    webproduct['fname'] = data[0]['datas_fname']
                elif oscom_product.product_id.product_picture:
                    webproduct['haspic'] = 2
                    webproduct['fname'] = oscom_product.product_id.product_picture
                else:
                    webproduct['haspic'] =0

                langs={}
                manufacturer_langs = {}
                products_pool=self.pool.get('product.product')
                for lang in website.language_ids:
                    if lang.language_id and lang.language_id.translatable:
                        langs[str(lang.esale_oscom_id)] = {
                            'name': products_pool.read(cr, uid, [oscom_product.product_id.id], ['name'], {'lang': lang.language_id.code})[0]['name'] or '',
                            'description': products_pool.read(cr, uid, [oscom_product.product_id.id], ['description_sale'], {'lang': lang.language_id.code})[0]['description_sale'] or '',
                            'url':products_pool.read(cr, uid, [oscom_product.product_id.id], ['product_url'],{'lang': lang.language_id.code})[0]['product_url'] or '',
                        }
                        if oscom_product.product_id.manufacturer_id:
                            manufacturer_langs[str(lang.esale_oscom_id)] = {
                            'manufacturers_url':self.pool.get('product.manufacturer').read(cr, uid, [oscom_product.product_id.manufacturer_id.id], ['manufacturer_url'], {'lang': lang.language_id.code})[0]['manufacturer_url'] or '',
                            }

                webproduct['langs'] = langs
                webproduct['name'] = oscom_product.product_id.name
                webproduct['description'] = oscom_product.product_id.description_sale or ''
                webproduct['url'] = oscom_product.product_id.product_url or ''

                if oscom_product.product_id.manufacturer_id:
                    webproduct['manufacturers_name'] = oscom_product.product_id.manufacturer_id.name
                    webproduct['manufacturers_url'] = oscom_product.product_id.manufacturer_id.manufacturer_url or ''
                    webproduct['manufacturer_langs'] = manufacturer_langs
                prod_id = webproduct['product_id']
                if (prod_id != 0):
                    if webproduct['spe_price']:
                        price = float(webproduct['price'])
                        spe_price = webproduct['spe_price']
                        if spe_price.find('%') > 0:
                            spe_price = spe_price[0:-1]
                            spe_price = "%.4f" % (price - (price*float(spe_price)/100))
                            webproduct['spe_price'] = spe_price
                        oscom_id=server.set_product_spe(webproduct)
                    elif not webproduct['spe_price']:
                        oscom_id=server.set_product_classical(webproduct)
                        server.del_spe_price(prod_id)
                elif (prod_id == 0):
                    if (webproduct['spe_price'] == 0):
                        oscom_id=server.set_product_classical(webproduct)
                    elif (webproduct['spe_price'] != 0):
                        oscom_id=server.set_product_spe(webproduct)

                if oscom_id!=oscom_product.esale_oscom_id:
                    self.pool.get('esale.oscom.product').write(cr, uid, [oscom_product.id], {'esale_oscom_id': oscom_id})
                    cr.commit()
                    prod_new += 1
                else:
                    prod_update += 1

                #####################PRODUCT URL IN OSCOMMERCE###################
                esale_prod_obj = self.pool.get('esale.oscom.product')
                esale_prod_ids = esale_prod_obj.search(cr, uid, [('esale_oscom_id','=',oscom_id)])
                esale_prod_data = esale_prod_obj.read(cr,uid,esale_prod_ids)
                #print ":::::::::::::::::::::::::::::::::::::::::::::::::::::"
                #print "ESALE PROD DATA:::::::::::",esale_prod_data

                prod_obj = self.pool.get('product.product')
                prod_ids = prod_obj.search(cr, uid, [('id','=',esale_prod_data[0]['product_id'][0])])
                prod_data = prod_obj.read(cr, uid, prod_ids)
                #print "PROD DATA:::::::::::",prod_data
                cat_map_obj = self.pool.get('esale.oscom.category')
                cat_id = prod_data[0]['categ_id'][0]
                cat_ids = cat_map_obj.search(cr, uid, [('category_id','=',cat_id)])
                cat_data = cat_map_obj.read(cr, uid, cat_ids)
                esale_cat_id = str(cat_data[0]['esale_oscom_id'])
                web_prod = self.pool.get ('esale.oscom.web')
                web_prod_ids = web_prod.search(cr, uid, [('id','=',esale_prod_data[0]['web_id'][0])])
                web_data = web_prod.read(cr, uid, web_prod_ids)
                prod_url = web_data [0]['url'].split("/")
                prod_url = prod_url[0] + "//" + prod_url[2] + "/" + prod_url[3] + "/" + prod_url[4] + "/" +"categories.php?cPath=" + esale_cat_id + "&pID=" + str(oscom_id) + "&action=new_product"
                prod_obj.write(cr, uid, [prod_data[0]['id']], {'oscom_url': prod_url})

            delete_esale_products_ids = self.pool.get('esale.oscom.product').search(cr, uid, [('web_id','=',website.id),('product_id','=',False)])
            esale_product_ids = self.pool.get('esale.oscom.product').read(cr, uid, delete_esale_products_ids, ['esale_oscom_id'])
            delete_oscom_ids = tuple([x['esale_oscom_id'] for x in esale_product_ids])
            if len(delete_oscom_ids):
                ret_delete = server.remove_product({'oscom_product_ids' : delete_oscom_ids})
                if ret_delete:
                    self.pool.get('esale.oscom.product').unlink(cr, uid, delete_esale_products_ids)
                #end if ret_delete:
            #end if len(delete_oscom_ids):

        return {'prod_new':prod_new, 'prod_update':prod_update}


    def oscom_update_stock(self, cr, uid, website = None, product_ids=[], context={}):
        """Update stock for product_ids to OScommerce website (all the websites where there are product_ids if website  is not defined)"""
        websites_objs = []
        websites = {}
        if not website:
            cr.execute('select distinct(web_id) from esale_oscom_product where product_id in (%s)'%','.join([str(x) for x in product_ids]))
            web_data = cr.fetchall()
            web_ids = []
            for web in web_data:
                web_ids.append(web[0])
            #end for web in web data
            websites_objs = self.pool.get('esale.oscom.web').browse(cr,uid,web_ids)
        else:
            websites_objs.append(website)
        for website in websites_objs:
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            if not product_ids:
                oscom_products = website.product_ids
            else:
                oscom_product_ids = self.pool.get('esale.oscom.product').search(cr, uid, [('web_id','=',website.id), ('product_id','in',product_ids)])
                oscom_products = self.pool.get('esale.oscom.product').browse(cr, uid, oscom_product_ids)
            for oscom_product in oscom_products:
                webproduct={
                        'product_id': oscom_product.esale_oscom_id,
                        'quantity': self.pool.get('product.product')._product_available(cr, uid, [oscom_product.product_id.id], ['virtual_available'], False, {'shop':website.shop_id.id})[oscom_product.product_id.id]['virtual_available']
                }
                oscom_id=server.set_product_stock(webproduct)

        return {}

##    def on_change_gross_price(self, cr, uid, ids, list_price):
##        if list_price:
##            if ids:
##                product=self.pool.get('product.product').browse(cr, uid, ids[0])
##                if not product.taxes_id:
##                    VAT=0
##                else:
##                    VAT=product.taxes_id[0].amount
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
##                product=self.pool.get('product.product').browse(cr, uid, ids[0])
##                if not product.taxes_id:
##                    VAT=0
##                else:
##                    VAT=product.taxes_id[0].amount
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


#end class esale_oscom_product(osv.osv):
esale_oscom_product_inherit()
#
#class oscom_res_corrency(osv.osv):
#    _inherit='res.currency'
#    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount, round=False, context={}):
#        return super(oscom_res_corrency,self).compute(cr, uid, from_currency_id, to_currency_id, from_amount, round,context)
##end class oscom_res_corrency(osv.osv):
#oscom_res_corrency()
