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

import netsvc
from osv import fields,osv,orm
import ir
import time
import xmlrpclib
from mx import DateTime

class esale_oscom_web(osv.osv):
    _name = "esale.oscom.web"
    _description = "OScommerce Website"
    _columns = {
        'name': fields.char('Name',size=64, required=True),
        'url': fields.char('URL', size=128, required=True),
        'shop_id': fields.many2one('sale.shop', 'Sale Shop', required=True),
#        'partner_anonymous_id': fields.many2one('res.partner', 'Anonymous', required=True),
        'active': fields.boolean('Active'),
        'product_ids': fields.one2many('esale.oscom.product', 'web_id', 'Web Products'),
        'language_ids': fields.one2many('esale.oscom.lang', 'web_id', 'Languages'),
        'tax_ids': fields.one2many('esale.oscom.tax', 'web_id', 'Taxes'),
        'category_ids': fields.one2many('esale.oscom.category', 'web_id', 'Categories'),
        'pay_typ_ids': fields.one2many('esale.oscom.paytype', 'web_id', 'Payment types'),
        'esale_account_id': fields.many2one('account.account', 'Dest Account', required=True, help="Payment account for web invoices."),
        'price_type': fields.selection([('0', 'Untaxed price'), ('1', 'Taxed price')], 'Price type', required=True),
    }
    _defaults = {
        'active': lambda *a: 1,
        'price_type': lambda *a:'0',
    }

    def add_all_products(self, cr, uid, ids, *args):
        esale_product_obj = self.pool.get('esale.oscom.product')
        for id in ids:
            cr.execute("select p.id from product_product as p left join esale_oscom_product as o on p.id=o.product_id and o.web_id=%d where o.id is NULL;" % id)
            for [product] in cr.fetchall():
                value = {
                    'product_id' : product,
                    'web_id' : id
                }
                value.update(esale_product_obj.onchange_product_id(cr, uid, [], product, id)['value'])
                esale_product_obj.create(cr, uid, value)
        return True

    def tax_import(self, cr, uid, ids, *args):
        esale_tax_obj = self.pool.get('esale.oscom.tax')
        for website in self.browse(cr, uid, ids):
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            taxes = server.get_taxes()
            for tax in taxes:
                update_taxes_ids = esale_tax_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',tax[0])])
                if len(update_taxes_ids):
                    esale_tax_obj.write(cr, uid, update_taxes_ids, {'name': tax[1]})
                else:
                    value = {
                        'web_id' : website.id,
                        'esale_oscom_id' : tax[0],
                        'name' : tax[1]
                    }
                    esale_tax_obj.create(cr, uid, value)
        return True

    def lang_import(self, cr, uid, ids, *args):
        esale_lang_obj = self.pool.get('esale.oscom.lang')
        for website in self.browse(cr, uid, ids):
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            languages = server.get_languages()
            for language in languages:
                update_language_ids = esale_lang_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',language[0])])
                if len(update_language_ids):
                    esale_lang_obj.write(cr, uid, update_language_ids, {'name': language[1]})
                else:
                    value = {
                        'web_id' : website.id,
                        'esale_oscom_id' : language[0],
                        'name' : language[1]
                    }
                    esale_lang_obj.create(cr, uid, value)
        return True

    def category_import(self, cr, uid, ids, *args):
        esale_category_obj = self.pool.get('esale.oscom.category')
        for website in self.browse(cr, uid, ids):
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            categories = server.get_categories()
            for category in categories:
                value = {
                    'web_id' : website.id,
                    'esale_oscom_id' : category[0],
                    'name' : category[1]
                }
                existing = esale_category_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id', '=', category[0])])
                if len(existing) > 0:
                    esale_category_obj.write(cr, uid, existing, value)
                else:
                    esale_category_obj.create(cr, uid, value)
        return True

    def category_import_create(self, cr, uid, ids, *args):
        category_obj = self.pool.get('product.category')
        esale_category_obj = self.pool.get('esale.oscom.category')

        for website in self.browse(cr, uid, ids):
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)

            # Search OScommerce languages mapped to OpenERP
            osc_langs = [lang.esale_oscom_id for lang in website.language_ids if lang.language_id and lang.language_id.translatable]
            oerp_langs = [lang.language_id for lang in website.language_ids if lang.language_id and lang.language_id.translatable]
            if not osc_langs:
                raise osv.except_osv(_('Warning'), _("First you must map OScommerce languages to OpenERP languages in the Web Shop!"))

            categories = server.get_categories_parent(osc_langs)
            for category in categories:
                # Search in intermediate esale.oscom.category object that maps OScommerce and OpenERP categories
                cat_oscom_id = esale_category_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',category[0])])
                if cat_oscom_id:
                    cat_oscom = esale_category_obj.browse(cr, uid, cat_oscom_id)[0]
                if category[1]: # Has a parent category
                    cat_oscom_p_id = esale_category_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',category[1])])
                    cat_oscom_p = esale_category_obj.browse(cr, uid, cat_oscom_p_id)[0]

                # Creates or updates product.category and esale.oscom.category objects
                value = {
                    'name' : category[2],
                    'parent_id': category[1] and cat_oscom_p.category_id.id
                }
                if not cat_oscom_id or not cat_oscom.category_id: # OpenERP category does not exist
                    cat_id = category_obj.create(cr, uid, value)
                    value_cat_oscom = {
                        'web_id' : website.id,
                        'esale_oscom_id' : category[0],
                        'name' : category[2],
                        'category_id' : cat_id,
                    }
                    if not cat_oscom_id:
                        cat_oscom_id = esale_category_obj.create(cr, uid, value_cat_oscom)
                    else:
                        esale_category_obj.write(cr, uid, cat_oscom_id, value_cat_oscom)
                else:  # OpenERP category exists
                    cat_id = cat_oscom.category_id.id
                    category_obj.write(cr, uid, cat_id, value)

                # Updates translations
                for trans, lang in zip(category[2:], oerp_langs):
                    #print trans, lang.code
                    category_obj.write(cr, uid, cat_id, {'name': trans}, {'lang': lang.code})
        return True

    def product_import_create(self, cr, uid, ids, *args):
        product_obj = self.pool.get('product.product')
        esale_product_obj = self.pool.get('esale.oscom.product')
        esale_category_obj = self.pool.get('esale.oscom.category')
        esale_tax_obj = self.pool.get('esale.oscom.tax')

        for website in self.browse(cr, uid, ids):
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            website_url = website.url.split("/")

            # Search OScommerce languages mapped to OpenERP
            osc_langs = [lang.esale_oscom_id for lang in website.language_ids if lang.language_id and lang.language_id.translatable]
            oerp_langs = [lang.language_id for lang in website.language_ids if lang.language_id and lang.language_id.translatable]
            if not osc_langs:
                raise osv.except_osv(_('Warning'), _("First you must map OScommerce languages to OpenERP languages in the Web Shop!"))

            products_osc = server.get_products(osc_langs)
            #print products_osc
            for product in products_osc:
                print "=============================================================================="
                print product
                info_prod = product['product']
                spec_prod = product['product_special']
                name_prod = product['product_description'] and product['product_description'][0]['products_name'] or '-'

                # Search mapped category. If not found the product is not added/modified
                esale_categ_ids = esale_category_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',info_prod['categ_id'])])
                if not esale_categ_ids:
                    continue
                esale_categ = esale_category_obj.browse(cr, uid, esale_categ_ids[0])
                if not esale_categ.category_id:
                    continue

                # Search mapped tax
                esale_tax_ids = esale_tax_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',info_prod['products_tax_class_id'])])
                tax = []
                if esale_tax_ids:
                    esale_tax = esale_tax_obj.browse(cr, uid, esale_tax_ids[0])
                    tax = esale_tax.tax_id and [(6, 0, [esale_tax.tax_id.id])] or []

                # Note:
                # info_prod['manufacturers_id'] (integer) must be placed in OpenERP 'manufacturer_id' field (creating the manufacturer if is needed)
                value = {
                    'name': name_prod,
                    'default_code': info_prod['products_model'],
                    'categ_id': esale_categ.category_id.id,
                    'taxes_id': tax,
                    'list_price': info_prod['products_price'],
                    'weight': info_prod['products_weight'],
                    'product_picture': info_prod['products_image'],
                    'in_out_stock': str(info_prod['products_status']),
                    'date_available': info_prod['products_date_available'] or False,
                    'spe_price_status': 'status' in spec_prod and str(spec_prod['status']) or False,
                    'spe_price': 'specials_new_products_price' in spec_prod and spec_prod['specials_new_products_price'] or False,
                    'exp_date': 'expires_date' in spec_prod and spec_prod['expires_date']!='0000-00-00 00:00:00' and spec_prod['expires_date'] or False,
                    'oscom_url': website_url[0] + "//" + website_url[2] + "/" + website_url[3] + "/" + website_url[4] + "/" +"categories.php?cPath=" + str(info_prod['categ_id']) + "&pID=" + str(info_prod['products_id']) + "&action=new_product"
                    #'ean13': info_prod['products_model'],
                    #'type': 'Stockable product',
                    #'supply_method': 'buy',
                    #'procure_method': 'make_to_stock',
                    #'cost_method': 'standard',
                    #'sale_ok': True,
                    #'purchase_ok': True,
                    #'active': 'True',
                    #'weight_net': info_prod['products_weight'],
                    #'standard_price': info_prod['products_price'],
                    #'volume': 0,
                }
                print value

                # Search in intermediate esale.oscom.product object that maps OScommerce and OpenERP products
                esale_product_ids = esale_product_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id','=',info_prod['products_id'])])
                if esale_product_ids:
                    esale_product = esale_product_obj.browse(cr, uid, esale_product_ids[0])

                # Creates or updates product.product and esale.oscom.product objects
                if not esale_product_ids or not esale_product.product_id: # OpenERP product does not exist
                    prod_id = super(osv.osv, product_obj).create(cr, uid, value)
                    value_esale_product = {
                            'name': name_prod,
                            'esale_oscom_id': info_prod['products_id'],
                            'esale_oscom_tax_id': esale_tax_ids and esale_tax_ids[0] or False,
                            'web_id': website.id,
                            'product_id': prod_id,
                    }
                    if not esale_product_ids:
                        esale_product_id = esale_product_obj.create(cr, uid, value_esale_product)
                    else:
                        esale_product_obj.write(cr, uid, [esale_product_ids[0]], value_esale_product)
                else: # OpenERP product exists
                    prod_id = esale_product.product_id.id
                    super(osv.osv, product_obj).write(cr, uid, [prod_id], value)

                # Updates translations
                for trans, lang in zip(product['product_description'], oerp_langs):
                    #print trans, lang.code
                    super(osv.osv, product_obj).write(cr, uid, [prod_id], {
                            'name': trans['products_name'] or '-',
                            'description': trans['products_description'],
                            'description_sale': trans['products_description'],
                            'product_url': trans['products_url'],
                        }, {'lang': lang.code})
        return True

    def get_payment_methods(self, cr, uid, ids, *args):
        esale_paytype_obj = self.pool.get('esale.oscom.paytype')
        for website in self.browse(cr, uid, ids):
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            payment_methods = server.get_payment_methods()
            for payment_method in payment_methods:
                value={
                    'web_id' : website.id,
                    'esale_oscom_id' : payment_method[0],
                    'name' : payment_method[1]
                }
                existing = esale_paytype_obj.search(cr, uid, [('web_id','=',website.id), ('esale_oscom_id', '=', payment_method[0])])
                if len(existing) > 0:
                    esale_paytype_obj.write(cr, uid, existing, value)
                else:
                    esale_paytype_obj.create(cr, uid, value)
        return True

esale_oscom_web()


#class esale_oscom_country(osv.osv):
#    _inherit = 'res.country'
#    _columns = {
#        'esale_oscom_id': fields.integer('esale_oscom ID',readonly=True),
#    }
#
#class esale_oscom_state(osv.osv):
#    _inherit = 'res.country.state'
#    _columns = {
#        'esale_oscom_id': fields.integer('esale_oscom ID',readonly=True),
#    }


class esale_oscom_tax(osv.osv):
    _name = "esale.oscom.tax"
    _description = "esale_oscom Tax"
    _columns = {
        'name': fields.char('Tax name', size=32, required=True, readonly=True),
        'esale_oscom_id': fields.integer('OScommerce Id'),
        'web_id': fields.many2one('esale.oscom.web', 'Website'),
        'tax_id': fields.many2one('account.tax', 'OpenERP Tax'),
    }
esale_oscom_tax()


class esale_oscom_category(osv.osv):
    _name = "esale.oscom.category"
    _description = "esale_oscom Category"
    _columns = {
        'name': fields.char('Name', size=64, reuired=True, readonly=True),
        'esale_oscom_id': fields.integer('OScommerce Id', required=True),
        'web_id': fields.many2one('esale.oscom.web', 'Website'),
        'category_id': fields.many2one('product.category', 'OpenERP Category'),
    }
esale_oscom_category()


class esale_oscom_paytype(osv.osv):
    _name = "esale.oscom.paytype"
    _description = "esale_oscom PayType"
    _columns = {
        'name': fields.char('Name', size=64, reuired=True, readonly=True),
        'esale_oscom_id': fields.integer('OScommerce Id', required=True),
        'web_id': fields.many2one('esale.oscom.web', 'Website'),
        'payment_id': fields.many2one('payment.type', 'OpenERP payment'),
        'paytyp': fields.selection([('type1','SO in State Draft'),('type2','SO Confirmed'),('type3','Invoice Draft'),('type4','Invoice Confirmed'),('type5','Invoice Payed')], 'Payment Type'),
    }
esale_oscom_paytype()


#class esale_oscom_payment_method(osv.osv):
#    _name = "esale.oscom.payment.method"
#    _description = "esale_oscom Paymant Type Methods"
#    _columns = {'name': fields.char('Name', size=64, reuired=True),
#        'web_id': fields.many2one('esale.oscom.web', 'Website'),
#    }
#esale_oscom_payment_method()


class esale_oscom_product(osv.osv):
    _name = "esale.oscom.product"
    _description = "esale_oscom Product"
    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True),
        'esale_oscom_id': fields.integer('OScommerce product Id'),
        'esale_oscom_tax_id': fields.many2one('esale.oscom.tax', 'OScommerce tax'),
        'web_id': fields.many2one('esale.oscom.web', 'Website'),
        'product_id': fields.many2one('product.product', 'OpenERP Product'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, web_id):
        value = {}
        if (product_id):
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            value['name'] = product.name
        return {'value': value}

    def unlink(self, cr, uid, ids, context=None):
        websites = {}
        for esale_product in self.browse(cr, uid, ids):
            web_product_ids = websites.get(esale_product.web_id and esale_product.web_id.id)
            if web_product_ids and len(web_product_ids):
                web_product_ids.append(esale_product.esale_oscom_id)
            else:
                websites[esale_product.web_id and esale_product.web_id.id] = [esale_product.esale_oscom_id]
        websites_objs = self.pool.get('esale.oscom.web').browse(cr, uid, [x for x in websites.keys() if type(x) is int])
        for website in websites_objs:
            server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)
            server.remove_product({'oscom_product_ids':websites.get(website.id)})
        return super(esale_oscom_product,self).unlink(cr, uid, ids, context)
esale_oscom_product()


class esale_oscom_language(osv.osv):
    _name = "esale.oscom.lang"
    _description = "esale_oscom Language"
    _columns = {
        'name': fields.char('Name', size=32, required=True, readonly=True),
        'esale_oscom_id': fields.integer('OScommerce Id', required=True),
        'web_id': fields.many2one('esale.oscom.web', 'Website'),
        'language_id': fields.many2one('res.lang', 'OpenERP Language'),
    }
esale_oscom_language()


class esale_oscom_saleorder_line(osv.osv):
    def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.product_uos.id:
                res[line.id] = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                res[line.id] = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        return res

    _inherit='sale.order.line'
    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits=(16, 2)),
        'price_net': fields.function(_amount_line_net, method=True, string='Net Price', digits=(16, 2)),
    }
esale_oscom_saleorder_line()


class esale_oscom_saleorder(osv.osv):
    _inherit='sale.order'
    _name='sale.order'
    _table='sale_order'
    _columns = {
        'esale_oscom_web': fields.many2one('esale.oscom.web', 'Website'),
        'esale_oscom_id': fields.integer('esale_oscom Id'),
    }
    _defaults = {
        'esale_oscom_id': lambda *a: False,
    }

    def onchange_esale_oscom_web(self, cr, uid, ids, esale_oscom_web):
        value={}
        if esale_oscom_web:
            web = self.pool.get('esale.oscom.web').browse(cr, uid, esale_oscom_web)
            value['shop_id'] = web.shop_id.id
            value['partner_id'] = web.partner_anonymous_id.id
            value.update(self.pool.get('sale.order').onchange_shop_id(cr, uid, ids, value['shop_id'])['value'])
            value.update(self.pool.get('sale.order').onchange_partner_id(cr, uid, ids, value['partner_id'])['value'])

        return {'value':value}

    def order_create(self, cr, uid, ids, context={}):
        partner_obj = self.pool.get('res.partner')
        saleorder_obj = self.pool.get('sale.order')
        for order in self.browse(cr, uid, ids, context):
            addr = partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery','invoice','contact'])
            pricelist_id = order.partner_id.property_product_pricelist[0]
            order_lines = []
            for line in order.order_lines:
                order_lines.append( (0,0,{
                    'name': line.name,
                    'product_qty': line.product_qty,
                    'date_planned': line.date_planned,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'type': line.product_id.procure_method
                 }) )
            order_id = saleorder_obj.create(cr, uid, {
                'name': order.name,
                'shop_id': order.web_id.shop_id.id,
                'origin': 'WEB:'+str(order.id),
                'date_order': order.date_order,
                'user_id': uid,
                'partner_id': order.partner_id.id,
                'partner_invoice_id': addr['invoice'],
                'partner_order_id': addr['contact'],
                'partner_shipping_id': addr['delivery'],
                'pricelist_id': pricelist_id,
                'order_line': order_lines
            })
            self.write(cr, uid, [order.id], {'state':'done', 'order_id': order_id})
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
        return True

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed','done']):
        ret_super = super(esale_oscom_saleorder,self).action_invoice_create(cr, uid, ids, grouped, states)
        sale_order = self.browse(cr, uid, ids[0])
        self.pool.get('account.invoice').write(cr, uid, [ret_super], {'esale_oscom_web': sale_order.esale_oscom_web.id})
        return ret_super
esale_oscom_saleorder()


class esale_oscom_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'esale_oscom_web': fields.many2one('esale.oscom.web', 'Website'),
    }
esale_oscom_invoice()


class esale_oscom_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'esale_oscom_id': fields.integer('OScommerce Id'),
    }
esale_oscom_partner()


class esale_oscom_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
        'esale_oscom_id': fields.integer('OScommerce Id'),
    }
esale_oscom_partner_address()
