# -*- coding: utf-8 -*-
# Copyright 2014-2015 Microcom
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

# For 'base' map_values in post-migration
column_renames = {
    'product_pricelist_item': [
        ('base', None),
        ('price_version_id', None)
    ],
    'product_price_history': [
        ('product_template_id', None)
    ],
    'product_product': [
        ('image_variant', None),
    ],
    'product_template': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('product.product', 'product_product', 'ean13', 'barcode'),
    ('product.template', 'product_template', 'ean13', 'barcode'),
]

column_copies = {
    'product_template': [
        ('type', None, None),
    ],
}


def map_product_template_type(cr):
    """ The product template type value 'stockable' is not an option in the
    product module for v9. We need to assign a temporary 'dummy' value
    until module stock is installed. In post-migration we will
    restore the original value."""
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('product', 'consu')],
        table='product_template', write='sql')


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # Remove NOT NULL constraint on these obsolete required fields
    openupgrade.logged_query(cr, """
        ALTER TABLE product_price_history
        ALTER COLUMN product_template_id DROP NOT NULL
        """)
    # Remove NOT NULL constraint on these obsolete required fields
    openupgrade.logged_query(cr, """
        ALTER TABLE product_packaging ALTER COLUMN rows DROP NOT NULL
        """)

    # Remove NOT NULL constraint on these obsolete required fields
    openupgrade.logged_query(cr, """
        ALTER TABLE product_packaging ALTER COLUMN ul DROP NOT NULL
        """)

    # Remove NOT NULL constraint on these obsolete required fields
    openupgrade.logged_query(cr, """
        ALTER TABLE product_pricelist ALTER COLUMN type DROP NOT NULL
        """)

    # Remove NOT NULL constraint on these obsolete required fields
    openupgrade.logged_query(cr, """
        ALTER TABLE product_pricelist_item
        ALTER COLUMN price_version_id DROP NOT NULL
        """)

    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.copy_columns(cr, column_copies)

    # Add default value when it is null, as Product name / Package Logistic
    # Unit name
    openupgrade.logged_query(cr, """
        WITH q as (
        SELECT pp.id, pt.name as product_name, pu.name as ul_name
        FROM product_packaging as pp
        INNER JOIN product_template as pt
        ON pp.product_tmpl_id = pt.id
        INNER JOIN product_ul as pu
        ON pu.id = pp.ul)
        UPDATE product_packaging as pp
        SET name = q.product_name || '/' || q.ul_name
        FROM q
        WHERE pp.name IS NULL
        AND pp.id = q.id
        """)

    # Install module 'product_uos' if field 'uos_id' has a
    # value in the product.template.
    openupgrade.logged_query(cr, """
        UPDATE ir_module_module
        SET state = 'to install'
        FROM (
            SELECT True as to_install
            FROM product_template as pt
            WHERE uos_id is not NULL
            AND uos_id <> uom_id
            LIMIT 1
        ) AS q
        WHERE name = 'product_uos'
        and q.to_install = True
        """)

    cr.execute("update product_template set state=NULL where state=''")

    map_product_template_type(cr)

    # disable purchase price lists
    cr.execute(
        "update product_pricelist set active=False where type='purchase'"
    )

    # if weight_net != 0.0 in product_template, override weight
    # if not, do nothing
    openupgrade.logged_query(cr, """
            UPDATE product_template
            SET weight = weight_net
            WHERE weight_net != '0.0'
            """)
