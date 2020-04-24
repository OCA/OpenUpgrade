# -*- coding: utf-8 -*-
# © 2014-2015 Microcom
# © 2015 Eficent Business and IT Consulting Services S.L. - Jordi Ballester
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openupgradelib import openupgrade_90

attachment_fields = {
    'product.template': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
    'product.product': [
        ('image_variant', None),
    ],
}


def map_base(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('base'),
        'base',
        [('-1', 'pricelist'), ('-2', 'standard_price')],
        table='product_pricelist_item', write='sql')
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_pricelist_item ppi
        SET base = ppt.field
        FROM product_price_type AS ppt
        WHERE ppt.id = %(base)s
        AND ppt.field in ('list_price', 'standard_price')""" % {
            'base': openupgrade.get_legacy_name('base'),
        })


def update_price_history(cr):
    # Create price history for all existing variants
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO product_price_history
        (company_id, product_id, datetime, cost, write_date, write_uid,
        create_date, create_uid)
        SELECT pph.company_id, pr.id, pph.datetime, pph.cost, pph.write_date,
        pph.write_uid, pph.create_date, pph.create_uid
        FROM product_price_history as pph
        INNER JOIN product_template as pt
        ON pt.id = pph.%(product_tmpl_id)s
        LEFT JOIN product_product pr
        ON pr.product_tmpl_id = pt.id
        """ % {
            'product_tmpl_id': openupgrade.get_legacy_name(
                'product_template_id')
        })

    # Delete the records that refer to the product template
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM product_price_history
        WHERE %(product_tmpl_id)s IS NOT NULL
        """ % {
            'product_tmpl_id': openupgrade.get_legacy_name(
                'product_template_id')
        })


def update_product_pricelist_item(cr):

    # Determine the pricelist_id looking at the previous link with pricelist
    # version
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_pricelist_item as ppi
        SET pricelist_id = ppv.pricelist_id,
        date_end = ppv.date_end,
        date_start = ppv.date_start
        FROM product_pricelist_version as ppv
        WHERE ppv.id = ppi.%(price_version_id)s
        """ % {
            'price_version_id': openupgrade.get_legacy_name(
                'price_version_id')
        })

    # Determine value of applied_on field, based on whether categ_id,
    # product_id or product_tmpl_id is filled in (or none). We go from more
    # generic to more specific.
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET applied_on = CASE
        WHEN categ_id IS NOT NULL then '2_product_category'
        WHEN product_tmpl_id IS NOT NULL then '1_product'
        WHEN product_id IS NOT NULL then '0_product_variant'
        ELSE applied_on
        END""")

    # compute_price: set to 'formula' for existing records (default is 'fixed')
    openupgrade.logged_query(cr, """
        UPDATE product_pricelist_item
        SET compute_price = 'formula'""")

    # but ones that arguably are meant to be fixed prices should be fixed
    openupgrade.logged_query(
        cr,
        "update product_pricelist_item "
        "set compute_price='fixed', fixed_price=price_surcharge "
        "where compute_price='formula' and price_discount=100 and "
        "price_surcharge > 0 and coalesce(price_min_margin, 0)=0 and "
        "coalesce(price_max_margin, 0)=0"
    )


def update_product_template(cr):

    # make ir.property records associated to 'standard_price' applicable to
    # product.product instead of product.template.

    cr.execute("""
        SELECT imf.id
        FROM ir_model_fields as imf
        INNER JOIN ir_model as im
        ON imf.model_id = im.id
        WHERE im.model = 'product.product'
        AND imf.name = 'standard_price'
        LIMIT 1
    """)

    standard_price_field = cr.fetchone()[0] or False

    openupgrade.logged_query(cr, """
        INSERT INTO ir_property
        (name, res_id, company_id, fields_id, value_float, value_integer,
        value_text, value_binary, value_reference, value_datetime, type)
        SELECT ip.name, CONCAT('product.product,', pp.id), ip.company_id,
        %s, ip.value_float, ip.value_integer, ip.value_text,
        ip.value_binary, ip.value_reference, ip.value_datetime, ip.type
        FROM product_product AS pp
        INNER JOIN product_template AS pt
        ON pp.product_tmpl_id = pt.id
        INNER JOIN ir_property AS ip
        ON ip.res_id = CONCAT('product.template,', pt.id)
        WHERE ip.name = 'standard_price'
        """ % standard_price_field)

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
            SELECT product_tmpl_id, count(id) as count
            FROM product_product
            WHERE active
            GROUP BY product_tmpl_id
        ) as q
        WHERE q.product_tmpl_id = product_template.id AND q.count > 1
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


def map_product_template_type(cr):
    """ See comments in method map_product_template_type in the pre-migration
    script."""
    if not openupgrade.logged_query(cr, """
        select id FROM product_template where {name_v8} = 'product'
    """.format(name_v8=openupgrade.get_legacy_name('type'))):
        return
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('product', 'product')],
        table='product_template', write='sql')


def update_product_supplierinfo(env):
    """ Merge obsolete partner_pricelistinfo with product_supplierinfo.
    Store the id of the original pricelistinfo on a custom integer field
    for later reference."""
    # Default currency for infos without a company
    default_currency_id = env['res.company'].search(
        [], order='id asc', limit=1).currency_id.id
    env.cr.execute(
        """ALTER TABLE product_supplierinfo
        ADD COLUMN openupgrade_migrated_from_pricelist_id INTEGER""")
    env.cr.execute(
        """UPDATE product_supplierinfo ps
        SET openupgrade_migrated_from_pricelist_id = pp.id,
        min_qty = pp.min_quantity,
        price = pp.price,
        currency_id = %s
        FROM pricelist_partnerinfo pp
        WHERE pp.suppinfo_id = ps.id
        """, (default_currency_id,))
    # Fix currency where company is set
    env.cr.execute(
        """UPDATE product_supplierinfo ps
        SET currency_id = rc.currency_id
        FROM res_company rc
        WHERE rc.id = ps.company_id """)
    openupgrade.logged_query(
        env.cr,
        """ INSERT INTO product_supplierinfo (
            company_id,
            create_date,
            create_uid,
            currency_id,
            delay,
            min_qty,
            name,
            openupgrade_migrated_from_pricelist_id,
            price,
            product_tmpl_id,
            product_code,
            product_name,
            sequence)
        SELECT
            ps.company_id,
            pp.create_date,
            pp.create_uid,
            ps.currency_id,
            ps.delay,
            pp.min_quantity,
            ps.name,
            pp.id,
            pp.price,
            ps.product_tmpl_id,
            ps.product_code,
            ps.product_name,
            ps.sequence
        FROM product_supplierinfo ps, pricelist_partnerinfo pp
        WHERE pp.id NOT IN (
                SELECT openupgrade_migrated_from_pricelist_id
                FROM product_supplierinfo
                WHERE openupgrade_migrated_from_pricelist_id IS NOT NULL)
            AND pp.suppinfo_id = ps.id
        """)

    # Set supplierinfo currencies when suppliers have a specific pricelist
    # that is not in the company currency
    openupgrade.logged_query(
        env.cr,
        """ UPDATE product_supplierinfo ps
        SET currency_id = pp.currency_id
        FROM product_pricelist pp
            JOIN ir_property ip
                ON ip.value_reference = 'product.pricelist,'||pp.id
            JOIN res_company rc ON ip.company_id = rc.id
            JOIN res_partner rp ON ip.res_id = 'res.partner,'||rp.id
        WHERE ip.name = 'property_product_pricelist_purchase'
            AND ps.company_id = rc.id
            AND rp.id = ps.name
            AND rc.currency_id != pp.currency_id """)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    map_base(env.cr)
    update_price_history(env.cr)
    update_product_pricelist_item(env.cr)
    update_product_product(env.cr)
    update_product_template(env.cr)
    map_product_template_type(env.cr)
    # this field's semantics was updated to its name
    env.cr.execute(
        'update product_pricelist_item set price_discount=-price_discount*100'
    )
    openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)
    openupgrade.load_data(
        env.cr, 'product', 'migrations/9.0.1.2/noupdate_changes.xml',
    )
    update_product_supplierinfo(env)
