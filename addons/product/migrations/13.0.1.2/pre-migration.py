# Copyright 2020 ForgeFLow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('sale.group_discount_per_so_line', 'product.group_discount_per_so_line'),
]


def fill_product_pricelist_item_prices(env):
    """These fields are now required. They were probably already populated,
    as they can't be empty through UI, but let's make sure putting these
    sane defaults.
    """
    # fill compute_price
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_pricelist_item
        SET compute_price = 'fixed'
        WHERE compute_price IS NULL
        """,
    )
    # delete records with empty pricelist_id, as they were
    openupgrade.logged_query(
        env.cr, "DELETE FROM product_pricelist_item WHERE pricelist_id IS NULL"
    )


def fill_product_pricelist_item_active_default(env):
    """Faster way to fill this new field"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE product_pricelist_item
        ADD COLUMN active boolean
        DEFAULT TRUE""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE product_pricelist_item ALTER COLUMN active DROP DEFAULT""",
    )


def calculate_product_product_combination_indices(env):
    """Avoid product_product_combination_unique constrain"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE product_product
        ADD COLUMN combination_indices varchar""",
    )
    openupgrade.logged_query(
        env.cr, """
        WITH pvc AS (
            SELECT pavppr.product_product_id,
                ptav.id AS product_template_attribute_value_id
            FROM product_attribute_value_product_product_rel pavppr
            JOIN product_product pp ON pp.id = pavppr.product_product_id
            JOIN product_template_attribute_value ptav
                ON ptav.product_attribute_value_id =
                    pavppr.product_attribute_value_id
                AND pp.product_tmpl_id = ptav.product_tmpl_id
        )
        UPDATE product_product pp
        SET combination_indices = grouped_pvc.indices
        FROM (
            SELECT pvc.product_product_id, STRING_AGG(
                pvc.product_template_attribute_value_id::varchar, ','
                ORDER BY pvc.product_template_attribute_value_id) indices
            FROM pvc
            JOIN product_product pp ON pp.id = pvc.product_product_id
            GROUP BY pvc.product_product_id
        ) grouped_pvc
        WHERE grouped_pvc.product_product_id = pp.id
        """,
    )


def add_product_template_attribute_value__attribute_id_column(env):
    """For avoiding that ORM fills it. We fill it later on post-migration."""
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE product_template_attribute_value "
        "ADD COLUMN attribute_id INT4",
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, _xmlid_renames)
    fill_product_pricelist_item_prices(env)
    fill_product_pricelist_item_active_default(env)
    calculate_product_product_combination_indices(env)
    add_product_template_attribute_value__attribute_id_column(env)
