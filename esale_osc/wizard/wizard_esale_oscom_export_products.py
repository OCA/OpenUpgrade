# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
import wizard

_export_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Product Export">
    <separator string="Products exported" colspan="4" />
    <field name="prod_new"/>
    <newline/>
    <field name="prod_update"/>
    <newline/>
    <field name="prod_delete"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New products', 'type':'float', 'readonly': True},
    'prod_update': {'string':'Updated products', 'type':'float', 'readonly': True},
    'prod_delete': {'string':'Deleted products', 'type':'float', 'readonly': True},
}

def _do_export(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)
    esale_web_obj = self.pool.get('esale.oscom.web')
    esale_category_obj = self.pool.get('esale.oscom.category')
    product_obj = self.pool.get('product.product')

    if data['model'] == 'ir.ui.menu':
        website_ids = esale_web_obj.search(cr, uid, [('active', '=', True)])
    else:
        website_ids = []
        website_not = []
        for id in data['ids']:
            exportable_website = esale_web_obj.search(cr, uid, [('id', '=', id), ('active', '=', True)])
            if exportable_website:
                website_ids.append(exportable_website[0])
            else:
                website_not.append(id)

        if len(website_not) > 0:
            raise wizard.except_wizard(_("Error"), _("You asked to synchronize to non-active OScommerce web shop: IDs %s") % website_not)

    prod_new = 0
    prod_update = 0
    prod_delete = 0
    for website_id in website_ids:
        website = esale_web_obj.browse(cr, uid, website_id)
        esale_category_ids = esale_category_obj.search(cr, uid, [('web_id','=', website.id), ('category_id', '!=', False)])
        esale_categories = esale_category_obj.browse(cr, uid, esale_category_ids)
        product_ids = []
        for esale_category in esale_categories:
            product_ids.extend(product_obj.search(cr, uid, [('categ_id','=',esale_category.category_id.id)]))

        res = product_obj.oscom_export(cr, uid, website=website, product_ids=product_ids, context=context)
        prod_new = prod_new + res['prod_new']
        prod_update = prod_update + res['prod_update']
        prod_delete = prod_delete + res['prod_delete']

    return {'prod_new':prod_new, 'prod_update':prod_update, 'prod_delete':prod_delete}


class wiz_esale_oscom_products(wizard.interface):

    states = { 'init' : { 'actions' : [_do_export],
                          'result' : { 'type' : 'form',
                                       'arch' : _export_done_form,
                                       'fields' : _export_done_fields,
                                       'state' : [('end', 'End')]
                                     }
                        }
             }

wiz_esale_oscom_products('esale.oscom.products');
