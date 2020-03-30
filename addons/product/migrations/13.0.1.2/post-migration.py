# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_product_pricelist_item_prices(env):
    # fill compute_price
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_pricelist_item
        SET compute_price = 'fixed'
        WHERE compute_price IS NULL
        """,
    )
    # fill pricelist_id
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_pricelist_item ppi
        SET pricelist_id = (
            SELECT max(grouped_pp.id)
            FROM (
                SELECT max(id) as id, company_id
                FROM product_pricelist
                WHERE active = TRUE
                GROUP BY company_id
            ) grouped_pp
            WHERE grouped_pp.company_id IS NULL OR
                grouped_pp.company_id = ppi.company_id
        )
        WHERE ppi.pricelist_id IS NULL""",
    )


def fill_product_template_attribute_value_attribute_line_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template_attribute_value ptav
        SET attribute_line_id = ptal.id
        FROM product_template_attribute_line ptal
        JOIN product_template pt ON ptal.product_tmpl_id = pt.id
        JOIN product_attribute_value_product_template_attribute_line_rel
            avtalr ON avtalr.product_template_attribute_line_id = ptal.id
        WHERE ptal.active = TRUE AND ptav.product_tmpl_id = pt.id AND
            ptav.product_attribute_value_id = avtalr.product_attribute_value_id
        """,
    )


def fill_product_template_attribute_value_attribute_id_default(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template_attribute_value ptav
        SET attribute_id = ptal.attribute_id
        FROM product_template_attribute_line ptal
        WHERE ptav.attribute_line_id = ptal.id""",
    )


def fill_product_variant_combination_table(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_variant_combination pvc
        SET product_product_id = pavppr.product_product_id,
            product_template_attribute_value_id = ptav.id
        FROM product_attribute_value_product_product_rel pavppr
        JOIN product_template_attribute_value ptav ON
            ptav.product_attribute_value_id = pavppr.product_attribute_value_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_product_pricelist_item_prices(env)
    fill_product_template_attribute_value_attribute_line_id(env)
    fill_product_template_attribute_value_attribute_id_default(env)
    fill_product_variant_combination_table(env)
    openupgrade.load_data(
        env.cr, "product", "migrations/13.0.1.2/noupdate_changes.xml")
