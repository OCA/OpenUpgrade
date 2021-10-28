# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_empty_discount_policy(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_pricelist
        SET discount_policy = 'with_discount'
        WHERE discount_policy is null
        """,
    )


def copy_date_end_date_start_columns(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "product_pricelist_item": [
                ("date_end", None, None),
                ("date_start", None, None),
            ]
        },
    )


def assure_m2m_table_correct_values(env):
    # if you come migrating from older versions, you may have problems with this table
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM product_attribute_value_product_template_attribute_line_rel rel
        USING product_attribute_value_product_template_attribute_line_rel rel0
        LEFT JOIN product_attribute_value pav
            ON rel0.product_attribute_value_id = pav.id
        LEFT JOIN product_template_attribute_line ptal
            ON rel0.product_template_attribute_line_id = ptal.id
        WHERE (rel.product_attribute_value_id = rel0.product_attribute_value_id
            AND rel.product_template_attribute_line_id =
                rel0.product_template_attribute_line_id)
            AND (pav.id IS NULL OR ptal.id IS NULL)""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_empty_discount_policy(env)
    copy_date_end_date_start_columns(env)
    assure_m2m_table_correct_values(env)
