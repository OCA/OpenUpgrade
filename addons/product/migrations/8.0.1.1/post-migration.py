# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID

def load_data(cr):
    openupgrade.load_data(cr, 'product', 'migrations/8.0.1.1/modified_data.xml', mode='init')

def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = ["UPDATE product_supplierinfo "
               "SET product_tmpl_id=(SELECT product_tmpl_id "
               "          FROM product_product "
               "          WHERE product_product.id=product_supplierinfo.%s) " \
               % openupgrade.get_legacy_name('product_id'),
               #
               "UPDATE product_template as pt "
               "SET color=(SELECT pp1.%s "
               "      FROM product_product as pp1 "
               "      WHERE pp1.product_tmpl_id=pt.id ORDER BY pp1.id LIMIT 1), "
               "    image=(SELECT pp2.image_variant "
               "      FROM product_product as pp2 "
               "      WHERE pp2.product_tmpl_id=pt.id ORDER BY pp2.id LIMIT 1)"
               % (openupgrade.get_legacy_name('color'),
                  )
               #

               ]
    for sql in queries:
        execute(cr, sql)

def copy_fields(cr, pool):
    product_tmpl= pool['product.template']
    product_obj= pool['product.product']
    # copy the active field from product to template
    ctx = {'active_test': False}
    tmpl_ids = product_tmpl.search(cr, SUPERUSER_ID, [], context=ctx)
    for template in product_tmpl.browse(cr, SUPERUSER_ID, tmpl_ids, context=ctx):
        template.write({'active': any(variant.active
                                      for variant in template.product_variant_ids)
                        })

def migrate_packaging(cr, pool):
    """create 1 product UL for each different product packaging dimension
    and link it to the packagings
    """
    packaging_obj = pool['product.packaging']
    ul_obj = pool['product.ul']
    execute = openupgrade.logged_query
    legacy_columns = dict((key, openupgrade.get_legacy_name(key))
                          for key in ('height', 'width',
                                      'length', 'weight_ul'))
    execute(cr,
            'select ul, %(height)s, %(width)s, %(length)s, %(weight_ul)s '
            'from product_packaging' % legacy_columns)
    for ul_id, height, width, length, weight in cr.fetchall():
        ul_obj.write(cr, SUPERUSER_ID, [ul_id],
                     {'height': height,
                      'width': width,
                      'length': length,
                      'weight': weight,
                      })

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    copy_fields(cr, pool)
    migrate_packaging(cr, pool)
    load_data(cr)

