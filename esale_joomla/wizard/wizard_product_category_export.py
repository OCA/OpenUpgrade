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

import wizard

_export_done_form = '''<?xml version="1.0"?>
<form string="Initial import">
    <separator string="Products Category exported" colspan="4" />
    <field name="category_new"/>
    <newline/>
    <field name="category_update"/>
</form>'''

_export_done_fields = {
    'category_new': {'string': 'New Product Categories', 'type': 'float', 'readonly': True},
    'category_update': {'string': 'Updated Product Categories', 'type': 'float', 'readonly': True},

}
category_new = 0
category_update = 0


def _do_export(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)
    ids = self.pool.get('esale_joomla.web').search(cr, uid, [])
    self.category_new = 0
    self.category_update = 0

    for website in self.pool.get('esale_joomla.web').browse(cr, uid, ids):
        logids = self.pool.get('esale_joomla.web.exportlog').search(cr, uid, [('web_id', '=', website.id), ('log_type', '=', 'category')], order='log_date desc')
        if len(logids):
            lastExportDate = self.pool.get('esale_joomla.web.exportlog').browse(cr, uid, logids)[0].log_date
        else:
            lastExportDate = 'False'

        server = xmlrpclib.ServerProxy("%s/tinyerp-synchro.php" % website.url)
#       server.delete_product_categories()
#       server.delete_products()
        cat_ids = self.pool.get('product.category').search(cr, uid, [('parent_id', '=', False)])

        def _add_category(category):
            esale_joomla_id2 = self.pool.get('esale_joomla.category').search(cr, uid, [('web_id', '=', website.id), ('category_id', '=', category.id)])
            esale_joomla_id = 0
            if esale_joomla_id2:
                esale_joomla_id = self.pool.get('esale_joomla.category').browse(cr, uid, esale_joomla_id2[0]).esale_joomla_id

            parent_id = 0
            if (category.parent_id):
                parent_id2 = self.pool.get('esale_joomla.category').search(cr, uid, [('web_id', '=', website.id), ('category_id', '=', category.parent_id.id)])


                if parent_id2:
                    parent_id = self.pool.get('esale_joomla.category').browse(cr, uid, parent_id2[0]).esale_joomla_id

            webcategory = {
                'esale_joomla_id': esale_joomla_id,
                'name': category.name,
                'parent_id': parent_id,

            }

            fr_cat = self.pool.get('product.category').browse(cr, uid, category.id, context={'lang': 'fr_FR'})
            if fr_cat:
                webcategory["name:fr_FR"] = fr_cat.name
            en_cat = self.pool.get('product.category').browse(cr, uid, category.id, context={'lang': 'en_US'})
            if en_cat:
                webcategory["name:en_US"] = en_cat.name

            osc_id = server.set_category(webcategory)
            if osc_id != esale_joomla_id:
                if esale_joomla_id:
                    self.pool.get('esale_joomla.category').write(cr, uid, [esale_joomla_id], {'esale_joomla_id': osc_id})
                    self.category_update += 1
                else:
                    cat_dict = {'category_id': category.id, 'web_id': website.id, 'esale_joomla_id': osc_id, 'name': category.name}
                    self.pool.get('esale_joomla.category').create(cr, uid, cat_dict)
                    self.category_new += 1
            else:
                self.category_update += 1

        def _recursive(category):
            _add_category(category)
            for child in category.child_id:
                _recursive(child)

        for category in self.pool.get('product.category').browse(cr, uid, cat_ids, context=context):
            _recursive(category)

        self.pool.get('esale_joomla.web.exportlog').create(cr, uid, {'name': 'Category Export ' + time.strftime('%Y-%m-%d %H:%M:%S'), 'web_id': website.id, 'log_type': 'category'})

    return {'category_new': self.category_new, 'category_update': self.category_update}


class wiz_esale_joomla_product_category(wizard.interface):
    states = {
        'init': {
            'actions': [_do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')]}
        }
    }
wiz_esale_joomla_product_category('esale_joomla.product.category')
