# Copyright 2020 ForgeFLow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('sale.group_discount_per_so_line', 'product.group_discount_per_so_line'),
]


def rename_image_attachments(env):
    for old, new in [("image_variant", "image_variant_1024")]:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_attachment SET res_field = %s
            WHERE res_field = %s AND res_model = 'product.product'""",
            (new, old),
        )
    for old, new in [("image", "image_1024"), ("image_medium", "image_128")]:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_attachment SET res_field = %s
            WHERE res_field = %s AND res_model = 'product.template'""",
            (new, old),
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
                ptav.id as product_template_attribute_value_id
            FROM product_attribute_value_product_product_rel pavppr
            JOIN product_template_attribute_value ptav ON
            ptav.product_attribute_value_id = pavppr.product_attribute_value_id
        )
        UPDATE product_product pp
        SET combination_indices = grouped_pvc.indices
        FROM (
            SELECT pvc.product_product_id, STRING_AGG(
                pvc.product_template_attribute_value_id::varchar, ','
                ORDER BY pvc.product_template_attribute_value_id) indices
            FROM pvc
            JOIN product_product pp ON pp.id = pvc.product_product_id
            GROUP BY pvc.product_product_id) grouped_pvc
        WHERE pp.active AND pp.product_tmpl_id IS NOT NULL
            AND grouped_pvc.product_product_id = pp.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, _xmlid_renames)
    rename_image_attachments(env)
    fill_product_pricelist_item_active_default(env)
    calculate_product_product_combination_indices(env)
