#!/usr/bin/python
# -*- coding: utf-8
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import time
import xmlrpclib
import pooler
import urllib
import base64
from osv.osv import except_osv

import wizard

_export_done_form = '''<?xml version="1.0"?>
<form string="Initial import">
  <separator string="Products exported" colspan="4" />
  <field name="prod_new"/>
  <newline/>
  <field name="prod_update"/>
   <newline/>
  <field name="prod_unlink"/>
   <newline/>
  <field name="prod_img"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string': 'New products', 'type': 'float', 'readonly': True},
    'prod_update': {'string': 'Updated products', 'type': 'float', 'readonly': True},
    'prod_unlink': {'string': 'Unpublish products', 'type': 'float', 'readonly': True},
    'prod_img': {'string': 'Publish Images', 'type': 'float', 'readonly': True},
}


def _do_export(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)
    web_ids = self.pool.get('esale_joomla.web').search(cr, uid, [('active', '=', 'True')])
    for website in self.pool.get('esale_joomla.web').browse(cr, uid, web_ids):
        prod_new_count = 0
        prod_update_count = 0
        prod_unlink_count = 0
        prod_img_count = 0
        logids = self.pool.get('esale_joomla.web.exportlog').search(cr, uid, [('web_id', '=', website.id), ('log_type', '=', 'product')], order='log_date desc')
        if len(logids):
            lastExportDate = self.pool.get('esale_joomla.web.exportlog').browse(cr, uid, logids)[0].log_date
        else:
            lastExportDate = 'False'
        webserver = xmlrpclib.ServerProxy("%s/tinyerp-synchro.php" % website.url)
        context['lang'] = website.language_id.code
        pricelist = website.shop_id.pricelist_id.id
        if not pricelist:
            raise wizard.except_wizard('UserError', 'You must define a pricelist in your shop !')

        for categ in website.category_ids:
            if not categ.category_id:
                continue

            cat_ids = [categ.category_id.id]
            if categ.include_childs:
                def _add_child(cat_ids, categ):
                    for child in categ.child_id:
                        if child.id not in cat_ids:
                            cat_ids.append(child.id)
                            _add_child(cat_ids, child)
                _add_child(cat_ids, categ.category_id)
            cr.execute("select product_product.id from product_product,product_template where " \
                    "(product_template.categ_id in (" + ','.join(map(str, cat_ids)) + ")) " \
                    "and (product_product.create_date > to_timestamp('" + lastExportDate + "','YYYY-MM-DD HH24:MI:SS') or product_product.write_date > to_timestamp('" + lastExportDate + "','YYYY-MM-DD HH24:MI:SS'))" \
                    "and (product_product.active = 'True') " \
                    "and (product_template.id = product_product.product_tmpl_id) order by id ")
            product_ids = map(lambda x: x[0], cr.fetchall())

            sql2 = "select product_product.id " \
                            "from product_product,product_template " \
                            "where (product_template.categ_id in (" + ','.join(map(str, cat_ids)) + ")) " \
                            "and (product_template.id = product_product.product_tmpl_id) " \
                            "and product_product.id in ( " \
                            "select res_id as product_id " \
                            "from ir_attachment "\
                            "where " \
                            "( " \
                            "ir_attachment.create_date > to_timestamp('" + lastExportDate + "','YYYY-MM-DD HH24:MI:SS') " \
                            "or ir_attachment.write_date > to_timestamp(' " + lastExportDate + "','YYYY-MM-DD HH24:MI:SS') " \
                            ") and res_model = 'product.product' ) "
            #print "sql2: %s" % sql2
            cr.execute(sql2)

            product_ids2 = map(lambda x: x[0], cr.fetchall())
            for id in product_ids2:
                if id not in product_ids:
                    product_ids.append(id)

            if len(product_ids) == 0:
                continue

            #code for unlink product
            unexport_products = self.pool.get('product.product').search(cr, uid, [('id', 'in', product_ids), ('exportable', '<>', 'True')])
            if len(unexport_products):
                unlink_pids = self.pool.get('esale_joomla.product').search(cr, uid, [('web_id', '=', website.id), ('product_id', 'in', unexport_products)])
                if len(unlink_pids):
                    joomla_ids = []
                    for webPro in self.pool.get('esale_joomla.product').read(cr, uid, unlink_pids):
                        joomla_ids.append(webPro['esale_joomla_id'])
                    res = webserver.unlink_products(joomla_ids)
                    prod_unlink_count = prod_unlink_count + len(joomla_ids)

            export_products = self.pool.get('product.product').search(cr, uid, [('id', 'in', product_ids), ('exportable', '=', 'True')])
            #print "1: %s" % len(export_products)

            #export_products = self.pool.get('product.product').search(cr, uid, [('categ_id','in',cat_ids)])
            for product in self.pool.get('product.product').browse(cr, uid, export_products, context=context):
                category_id = categ.esale_joomla_id
                esale_joomla_id2 = self.pool.get('esale_joomla.product').search(cr, uid, [('web_id', '=', website.id), ('product_id', '=', product.id)])
                esale_joomla_id = 0
                if esale_joomla_id2:
                    esale_joomla_id = self.pool.get('esale_joomla.product').browse(cr, uid, esale_joomla_id2[-1]).esale_joomla_id

                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product.id, 1, 'list')[pricelist]

                taxes_included = []
                web_taxes = []
                taxes_name = []
                for taxe in product.taxes_id:
                    esale_ids = self.pool.get('esale_joomla.tax').search(cr, uid, [('web_id', '=', website.id), ('tax_id', '=', taxe.id)])
                    taxes_ids = self.pool.get('esale_joomla.tax').browse(cr, uid, esale_ids)
                    if taxes_ids:
                        web_taxes.append({'id': taxes_ids[0].esale_joomla_id})
                    for t in website.taxes_included_ids:
                        # "website.taxes_included_ids" is defined in the "Taxes Mapping" tab, bottom half part.
                        if t.id == taxe.id:
                            taxes_included.append(taxe)


                for c in self.pool.get('account.tax').compute(cr, uid, taxes_included, price, 1, product=product):
                    price += c['amount']
                    taxes_name.append(c['name'])

                webproduct = {
                    'esale_joomla_id': esale_joomla_id,
                    'quantity': self.pool.get('product.product')._product_virtual_available(cr, uid, [product.id], '', False, {'shop': website.shop_id.id})[product.id],
                    'model': product.code or '',
                    #'price': product.list_price + product.contrib,
                    'price': price + product.contrib,
                    'weight': float(0.0),
                    'length': float(0.0),
                    'width': float(0.0),
                    'height': float(0.0),
                    'tax_rate_id': web_taxes,
                    'category_id': category_id,
                    'product_unit': product.uom_id.name,
                }

                attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model', '=', 'product.product'), ('res_id', '=', product.id)])
                data = self.pool.get('ir.attachment').read(cr, uid, attach_ids)
                if len(data):
                    webproduct['haspic'] = 1
                    if not data[0]['link']:
                        webproduct['picture'] = data[0]['datas']
                    else:
                        try:
                            webproduct['picture'] = base64.encodestring(urllib.urlopen(data[0]['link']).read())
                        except Exception, e:
                            print 'problem in image fetch :', e, data[0]['link']
                            webproduct['haspic'] = 0
                    webproduct['fname'] = data[0]['datas_fname']
                else:
                    webproduct['haspic'] = 0

                webproduct['product_packaging_qty'] = 0
                webproduct['product_packaging_type'] = ''
                for packaging in product.packaging:
                    res = packaging.qty
                    if packaging.name in ('U.V.', 'Unité de Vente') and res != 0:
                        webproduct['product_packaging_qty'] = res
                        webproduct['product_packaging_type'] = packaging.name

                webproduct['name'] = str(product.name or '')
                #print "webproduct['name']: %s" % (webproduct['name'])
                webproduct['code'] = str(product.default_code or '')
                webproduct['description'] = str((product.description_sale or '') + (len(taxes_name) and ("\n(" + (', '.join(taxes_name)) + ')') or ''))
                webproduct['short_description'] = str(product.description_sale or '')

                fr_product = self.pool.get('product.product').browse(cr, uid, product.id, context={'lang': 'fr_FR'})

                webproduct['description:fr_FR'] = str((fr_product.description_sale or '') + (len(taxes_name) and ("\n(" + (', '.join(taxes_name)) + ')') or ''))
                webproduct['short_description:fr_FR'] = str(fr_product.description_sale or '')
                webproduct['name:fr_FR'] = str(fr_product.name or '')
                #print "webproduct['name:fr_FR']: %s" % webproduct['name:fr_FR']

                en_product = self.pool.get('product.product').browse(cr, uid, product.id, context={'lang': 'en_US'})

                webproduct['description:en_US'] = str((en_product.description_sale or '') + (len(taxes_name) and ("\n(" + (', '.join(taxes_name)) + ')') or ''))
                webproduct['short_description:en_US'] = str(en_product.description_sale or '')
                webproduct['name:en_US'] = str(en_product.name or '')
                #print "webproduct['name:en_US']: %s" % webproduct['name:en_US']

                if product.contrib != 0.0:
                    webproduct['description'] = webproduct['description'] + " Recycling cost included."
                    webproduct['short_description'] = webproduct['short_description'] + " Recycling cost included."
                    webproduct['description:fr_FR'] = webproduct['description:fr_FR'] + " Contribution recyclage incluse."
                    webproduct['short_description:fr_FR'] = webproduct['short_description:fr_FR'] + " Contribution recyclage incluse."
                    webproduct['description:en_US'] = webproduct['description:en_US'] + " Recycling cost included."
                    webproduct['short_description:en_US'] = webproduct['short_description:en_US'] + " Recycling cost included."

                try:
                    osc_id = webserver.set_product(webproduct)
                    if webproduct['haspic']:
                        prod_img_count += 1
                    #print "osc_id: %s" % osc_id
                    #print "esale_joomla_id: %s" % esale_joomla_id
                    if osc_id != esale_joomla_id:
                        if esale_joomla_id and self.pool.get('esale_joomla.product').read(cr, uid, [esale_joomla_id]):
                            self.pool.get('esale_joomla.product').write(cr, uid, [esale_joomla_id], {'esale_joomla_id': osc_id})
                            prod_update_count += 1
                        else:
                            prod = {'product_id': product.id, 'web_id': website.id, 'esale_joomla_id': osc_id, 'name': product.name}
                            self.pool.get('esale_joomla.product').create(cr, uid, prod)
                        prod_new_count += 1
                    else:
                        prod_update_count += 1
                except Exception, e:
                    print e, " product : ", webproduct['name'], '(', webproduct['code'], ')'
                    raise except_osv('Error', e)

        export_dico = {'name': 'Product Export ' + time.strftime('%Y-%m-%d %H:%M:%S'), 'web_id': website.id, 'log_type': 'product'}
        self.pool.get('esale_joomla.web.exportlog').create(cr, uid, export_dico)

    return {'prod_new': prod_new_count, 'prod_update': prod_update_count, 'prod_unlink': prod_unlink_count, 'prod_img': prod_img_count}


class wiz_esale_joomla_products(wizard.interface):
    states = {
        'init': {
            'actions': [_do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')]}
        }
    }

wiz_esale_joomla_products('esale_joomla.products')

