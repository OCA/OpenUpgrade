# Copyright 2020 ForgeFLow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.tools import sql

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


def insert_missing_product_template_attribute_line(env):
    """Given this situation in v12:

    - Template T with attribute A and values A1, and A2, and attribute B with value B1.
    - Generated variants V1 and V2 for attribute values A1/B1 and A2/B2 respectively.
    - Generated product.template.attribute.line records for T/A and T/B.
    - V2 is used in a quotation.
    - Remove B attribute from the template. Result:
      * V2 is archived
      * product.template.attribute.line T/B is removed.

    On v13, the record is not removed, but marked with active = False.

    From the current data status we find on v12 for these cases, we need to
    reintroduce missing product.template.attribute.line records with
    active = False needed later on next steps for DB integrity.
    """
    openupgrade.add_fields(env, [(
        "active", "product.template.attribute.line",
        "product_template_attribute_line", "boolean", False, "product", True,
    )])
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO product_template_attribute_line
            (active, product_tmpl_id, attribute_id)
        SELECT False, pp.product_tmpl_id, pav.attribute_id
        FROM product_attribute_value_product_product_rel pavppr
        JOIN product_product pp ON pp.id = pavppr.product_product_id
        JOIN product_attribute_value pav ON pav.id = pavppr.product_attribute_value_id
        LEFT JOIN product_template_attribute_line ptal
            ON ptal.product_tmpl_id = pp.product_tmpl_id
                AND ptal.attribute_id = pav.attribute_id
        WHERE ptal.id IS NULL
        GROUP BY pav.attribute_id, pp.product_tmpl_id""",
    )


def insert_missing_product_template_attribute_value(env):
    """Given this situation in v12:

    - Template T with attribute A and values A1, and A2.
    - Generated variants V1 and V2 for attribute values A1 and A2 respectively.
    - Generated product.template.attribute.value for T/A1 and T/A2.
    - V2 is used in a quotation.
    - Remove A2 attribute value from the template. Result:
      * V2 is archived
      * product.template.attribute.value T/A2 is removed.

    On v13, the record is not removed, but marked with ptav_active = False. That's
    because there's a field in product.product called combination_indices that
    stores the ID of such line and serves for quick search/indexing on it.

    From the current data status we find on v12 for these cases, we need to
    reintroduce missing product.template.attribute.value records with
    ptav_active = False for not having later unique constraint errors and
    proper DB integrity.

    This is also the second step for amending the situation described in
    ``insert_missing_product_template_attribute_line`` method.
    """
    openupgrade.add_fields(env, [(
        "ptav_active", "product.template.attribute.value",
        "product_template_attribute_value", "boolean", False, "product", True,
    )])
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO product_template_attribute_value
            (ptav_active, product_attribute_value_id, product_tmpl_id)
        SELECT
            False, pavppr.product_attribute_value_id, pp.product_tmpl_id
        FROM product_attribute_value_product_product_rel pavppr
        JOIN product_product pp ON pp.id = pavppr.product_product_id
        LEFT JOIN product_template_attribute_value ptav
            ON ptav.product_attribute_value_id = pavppr.product_attribute_value_id
            AND ptav.product_tmpl_id = pp.product_tmpl_id
        WHERE ptav.id IS NULL
        GROUP BY pavppr.product_attribute_value_id, pp.product_tmpl_id""",
    )


def calculate_product_product_combination_indices(env):
    """Avoid product_product_combination_unique constraint + pre-compute
    combination_indices field.
    """
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE product_product
        ADD COLUMN combination_indices varchar""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_product pp
        SET combination_indices = grouped_pvc.indices
        FROM (
            SELECT pavppr.product_product_id,
                STRING_AGG(ptav.id::varchar, ',' ORDER BY ptav.id) indices
            FROM product_attribute_value_product_product_rel pavppr
            JOIN product_product pp ON pp.id = pavppr.product_product_id
            JOIN product_template_attribute_value ptav
                ON (ptav.product_attribute_value_id =
                    pavppr.product_attribute_value_id
                AND pp.product_tmpl_id = ptav.product_tmpl_id)
            GROUP BY pavppr.product_product_id
        ) grouped_pvc
        WHERE grouped_pvc.product_product_id = pp.id""",
    )


def fill_product_template_attribute_value_attribute_line_id(env):
    """Done in pre because the field attribute_line_id of ptav is required."""
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE product_template_attribute_value "
        "ADD COLUMN attribute_line_id INT4",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template_attribute_value ptav
        SET attribute_line_id = ptal.id
        FROM product_template_attribute_line ptal
        JOIN product_attribute_value pav ON ptal.attribute_id = pav.attribute_id
        WHERE ptav.product_tmpl_id = ptal.product_tmpl_id
            AND ptav.product_attribute_value_id = pav.id
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
    sql.create_index(
        env.cr, 'product_template_attribute_value_ou_migration_idx',
        "product_template_attribute_value",
        ['product_attribute_value_id', 'product_tmpl_id'])
    insert_missing_product_template_attribute_line(env)
    fill_product_template_attribute_value_attribute_line_id(env)
    insert_missing_product_template_attribute_value(env)
    calculate_product_product_combination_indices(env)
    add_product_template_attribute_value__attribute_id_column(env)
