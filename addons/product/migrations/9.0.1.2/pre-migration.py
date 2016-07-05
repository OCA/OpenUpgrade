# -*- coding: utf-8 -*-
# © 2014-Today Microcom
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
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
}


@openupgrade.migrate()
def migrate(cr, version):
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
