# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade
logger = logging.getLogger('OpenUpgrade')


def map_base(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('base'),
        'base',
        [('1', 'pricelist'), ('2', 'list_price')],
        table='product_pricelist_item', write='sql')


def update_price_history(cr):
    # Create price history for all existing variants
    openupgrade.logged_query(cr, """
        INSERT INTO product_price_history
        (company_id, product_id, datetime, cost, write_date, write_uid)
        SELECT pph.company_id, pr.id, pph.datetime, pph.cost, pph.write_date, pph.write_uid
        FROM product_price_history as pph
        INNER JOIN product_template as pt
        ON pt.id = pph.%(product_tmpl_id)s
        LEFT JOIN product_product pr
        ON pr.product_tmpl_id = pt.id
        """ % {'product_tmpl_id': openupgrade.get_legacy_name(
        'product_template_id')})

    # Delete the records that refer to the product template
    openupgrade.logged_query(cr, """
        DELETE FROM product_price_history
        WHERE %(product_tmpl_id)s IS NOT NULL
        """ % {'product_tmpl_id': openupgrade.get_legacy_name(
        'product_template_id')})


def update_product_pricelist_item(cr):

    # Determine the pricelist_id looking at the previous link with pricelist
    # version
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item as ppi
        SET pricelist_id = ppv.pricelist_id
        FROM product_pricelist_version as ppv
        WHERE ppv.id = ppi.%(price_version_id)s
        """ % {'price_version_id': openupgrade.get_legacy_name(
        'price_version_id')})

    # Apply date ranges on the item level, based on the dates that were set
    # on the pricelist version table.
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item as ppi
        SET date_end = ppv.date_end,
            date_start = ppv.date_start
        FROM product_pricelist_version as ppv
        WHERE ppv.id = ppi.%(price_version_id)s
        """ % {'price_version_id': openupgrade.get_legacy_name(
        'price_version_id')})

    # Determine value of applied_on field, based on whether categ_id,
    # product_id or product_tmpl_id is filled in (or none). We go from more
    # generic to more specific.
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET applied_on = '2_product_category'
        WHERE categ_id IS NOT NULL""")

    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item as ppi
        SET applied_on = '1_product'
        WHERE product_tmpl_id IS NOT NULL""")

    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET applied_on = '0_product_variant'
        WHERE product_id IS NOT NULL""")

    # Update base field

    # base: map standard_price
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET base = 'standard_price'
        FROM (
            SELECT ppi.id as ppi_id
            FROM product_pricelist_item AS ppi
            INNER JOIN product_price_type AS ppt
            ON ppt.id = ppi.id
            WHERE ppt.field = 'standard_price'
            ) as q
        WHERE id = q.ppi_id""")

    # base: map list_price
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET base = 'list_price'
        FROM (
            SELECT ppi.id as ppi_id
            FROM product_pricelist_item AS ppi
            INNER JOIN product_price_type AS ppt
            ON ppt.id = ppi.id
            WHERE ppt.field = 'list_price'
            ) as q
        WHERE id = q.ppi_id""")

    # base: map other pricelist
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET base = 'list_price'
        FROM (
            SELECT ppi.id as ppi_id
            FROM product_pricelist_item AS ppi
            INNER JOIN product_price_type AS ppt
            ON ppt.id = ppi.id
            WHERE ppt.id = '-1'
            ) as q
        WHERE id = q.ppi_id""")

    # Delete pricelist items based on supplier price set on the product form
    openupgrade.logged_query(cr, """
        DELETE FROM product_pricelist_item
        WHERE id IN (
            SELECT ppi.id as ppi_id
            FROM product_pricelist_item AS ppi
            INNER JOIN product_price_type AS ppt
            ON ppt.id = ppi.id
            WHERE ppt.id = '-2'
            )""")

    # compute_price: set to 'formula' for existing records (default is 'fixed')
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET compute_price = 'formula'""")

def update_product_supplierinfo(cr):
    # Create extra supplierinfo records when there were records in
    # pricelist_partnerinfo.
    openupgrade.logged_query(cr, """
        INSERT INTO product_supplierinfo
        (name, product_name, product_code, sequence, min_qty,
        price, product_tmpl_id, delay,
        company_id)
        SELECT ps.name, ps.product_name, ps.product_code,
        ps.sequence, pp.min_quantity, pp.price,
        ps.product_tmpl_id, ps.delay, ps.company_id
        FROM pricelist_partnerinfo as pp
        INNER JOIN product_supplierinfo as ps
        ON pp.suppinfo_id = ps.id
        """)

    # Delete supplierinfo records that had associated pricelist_partnerinfo
    # records, since we have now duplicated in the previous query.
    openupgrade.logged_query(cr, """
        DELETE FROM product_supplierinfo
        WHERE id IN (
            SELECT ps.id
            FROM pricelist_partnerinfo as pp
            INNER JOIN product_supplierinfo as ps
            ON pp.suppinfo_id = ps.id
        )""")


def update_product_template(cr):

    # make ir.property records associated to 'standard_price' applicable to
    # product.product instead of product.template.
    openupgrade.logged_query(cr, """
        INSERT INTO ir_property
        (name, res_id, company_id, fields_id, value_float, value_integer,
        value_text, value_binary, value_reference, value_datetime, type)
        SELECT ip.name, CONCAT('product.product,', pp.id), ip.company_id,
        ip.fields_id, ip.value_float, ip.value_integer, ip.value_text,
        ip.value_binary, ip.value_reference, ip.value_datetime, ip.type
        FROM product_product AS pp
        INNER JOIN product_template AS pt
        ON pp.product_tmpl_id = pt.id
        INNER JOIN ir_property AS ip
        ON ip.res_id = CONCAT('product.template,', pt.id)
        WHERE ip.name = 'standard_price'
        """)

    # Remove ir.property records associated to 'standard_price' for model
    # 'product.template'.
    openupgrade.logged_query(cr, """
        DELETE FROM ir_property
        WHERE name = 'standard_price'
        AND res_id like 'product.template%%'
        """)

    # On the template, set weight and volume to 0.0 on templates with more
    # than one (active?) variant as per _compute_product_template_field.
    openupgrade.logged_query(cr, """
        UPDATE product_template
        SET volume = 0.0, weight = 0.0
        FROM (
            SELECT pt.id, count(pp.id) as count
            FROM product_product as pp
            INNER JOIN product_template as pt
            ON pt.id = pp.product_tmpl_id
            GROUP BY pt.id
        ) as q
        WHERE q.id = product_template.id AND q.count > 0
        """)

def update_product_product(cr):
    # Move field values from product.template to product.product
    openupgrade.logged_query(cr, """
        UPDATE product_product
        SET volume = pt.volume,
        weight = pt.weight
        FROM product_template as pt
        WHERE pt.id = product_tmpl_id
        """)





@openupgrade.migrate()
def migrate(cr, version):
    map_base(cr)
    update_price_history(cr)
    update_product_pricelist_item(cr)
    update_product_supplierinfo(cr)
    update_product_template(cr)
    update_product_product(cr)


