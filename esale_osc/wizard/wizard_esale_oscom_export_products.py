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

import pooler
import wizard

_export_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Product Export">
    <separator string="Products exported" colspan="4" />
    <field name="prod_new"/>
    <newline/>
    <field name="prod_update"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New products', 'type':'float', 'readonly': True},
    'prod_update': {'string':'Updated products', 'type':'float', 'readonly': True},
}

def _do_export(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)

    if data['model'] == 'ir.ui.menu':
        website_ids = self.pool.get('esale.oscom.web').search(cr, uid, [('active', '=', True)])
    else:
        website_ids = []
        website_not = []
        for id in data['ids']:
            exportable_website = self.pool.get('esale.oscom.web').search(cr, uid, [('id', '=', id), ('active', '=', True)])
            if exportable_website:
                website_ids.append(exportable_website[0])
            else:
                website_not.append(id)

        if len(website_not) > 0:
            raise wizard.except_wizard(_("Error"), _("You asked to synchronize to non-active OScommerce web shop: IDs %s") % website_not)

    prod_new = 0
    prod_update = 0
    for website_id in website_ids:
        website = self.pool.get('esale.oscom.web').browse(cr, uid, website_id)
        esale_category_ids = self.pool.get('esale.oscom.category').search(cr, uid, [('web_id','=', website.id), ('category_id', '!=', False)])
        esale_category_objs = self.pool.get('esale.oscom.category').browse(cr,uid,esale_category_ids)
        product_ids = []
        for esale_category_obj in esale_category_objs:
            product_ids.extend(self.pool.get('product.product').search(cr,uid,[('categ_id','=',esale_category_obj.category_id.id)]))
        #end for esale_category_id in esale_category_ids:
        res = self.pool.get('product.product').oscom_export(cr, uid, website=website, product_ids=product_ids, context=context)
        prod_new = prod_new + res['prod_new']
        prod_update = prod_update + res['prod_update']

    return {'prod_new':prod_new, 'prod_update':prod_update}


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
