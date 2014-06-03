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
from itertools import groupby
from operator import itemgetter
from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID


def load_data(cr):
    openupgrade.load_data(cr, 'product',
                          'migrations/8.0.1.1/modified_data.xml',
                          mode='init')


def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = ["UPDATE product_supplierinfo "
               "SET product_tmpl_id=(SELECT product_tmpl_id "
               "          FROM product_product "
               "          WHERE product_product.id=product_supplierinfo.%s) " %
               openupgrade.get_legacy_name('product_id'),
               #
               "UPDATE product_template as pt "
               "SET color=(SELECT pp1.%s "
               "      FROM product_product as pp1 "
               "      WHERE pp1.product_tmpl_id=pt.id ORDER BY pp1.id LIMIT 1), "
               "    image=(SELECT pp2.image_variant "
               "      FROM product_product as pp2 "
               "      WHERE pp2.product_tmpl_id=pt.id ORDER BY pp2.id LIMIT 1)" %
               openupgrade.get_legacy_name('color')
               #

               ]
    for sql in queries:
        execute(cr, sql)


def copy_fields(cr, pool):
    product_tmpl = pool['product.template']
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


def create_properties(cr, pool):
    """ Fields moved to properties (standard_price).

    Write using the ORM so the prices will be written as properties.
    """
    template_obj = pool['product.template']
    company_obj = pool['res.company']
    company_ids = company_obj.search(cr, SUPERUSER_ID, [])
    sql = ("SELECT id, %s FROM product_template" %
           openupgrade.get_legacy_name('standard_price'))
    cr.execute(sql)
    for template_id, std_price in cr.fetchall():
        for company_id in company_ids:
            ctx = {'force_company': company_id}
            template_obj.write(cr, SUPERUSER_ID, [template_id],
                               {'standard_price': std_price},
                               context=ctx)
    # product.price.history entries have been generated with a value for
    # today, we want a value for the past as well, write a bogus date to
    # be sure that we have an historic value whenever we want
    cr.execute("UPDATE product_price_history SET "
               # calling a field 'datetime' is not really a good idea
               "datetime = '1970-01-01 00:00:00+00'")


def migrate_variants(cr, pool):
    template_obj = pool['product.template']
    attribute_obj = pool['product.attribute']
    attribute_value_obj = pool['product.attribute.value']
    attribute_line_obj = pool['product.attribute.line']
    fields = {'variant': openupgrade.get_legacy_name('variants'),
              'price': openupgrade.get_legacy_name('price_extra')}
    sql = ("SELECT id, %(variant)s, %(price)s, product_tmpl_id "
           "FROM product_product "
           "WHERE %(variant)s IS NOT NULL "
           "OR %(price)s IS NOT NULL AND %(price)s <> 0"
           "ORDER BY product_tmpl_id, id" % fields)
    cr.execute(sql)
    rows = cr.dictfetchall()
    for tmpl_id, variants in groupby(rows, key=itemgetter('product_tmpl_id')):
        # create an attribute shared by all the variants
        template = template_obj.browse(cr, SUPERUSER_ID, tmpl_id)
        attr_id = attribute_obj.create(cr, SUPERUSER_ID,
                                       {'name': template.name})
        for variant in variants:
            # create an attribute value for this variant
            price_extra = variant[fields['price']] or 0
            name = variant[fields['variant']]
            # active_id needed to create the 'product.attribute.price'
            ctx = {'active_id': tmpl_id}
            values = {
                'name': name or '%.2f' % price_extra,
                'attribute_id': attr_id,
                'product_ids': [(6, 0, [variant['id']])],
                # a 'product.attribute.price' is created when we write
                # a price_extra on an attribute value
                'price_extra': price_extra,
            }
            value_id = attribute_value_obj.create(cr, SUPERUSER_ID, values,
                                                  context=ctx)
            values = {'product_tmpl_id': tmpl_id,
                      'attribute_id': attr_id,
                      'value_ids': [(6, 0, [value_id])]}
            attribute_line_obj.create(cr, SUPERUSER_ID, values)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    copy_fields(cr, pool)
    migrate_packaging(cr, pool)
    create_properties(cr, pool)
    migrate_variants(cr, pool)
    load_data(cr)
