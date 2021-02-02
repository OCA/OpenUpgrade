# Copyright 2020 ForgeFLow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_merge_records
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
    openupgrade.add_fields(env, [(
        "active", "product.pricelist.item",
        "product_pricelist_item", "boolean", False, "product", True,
    )])


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
    if openupgrade.table_exists(env.cr, "mrp_bom_line"):
        # make use of mrp_bom_line_product_attribute_value_rel
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO product_template_attribute_line
                (active, product_tmpl_id, attribute_id)
            SELECT False, mb.product_tmpl_id, pav.attribute_id
            FROM mrp_bom_line_product_attribute_value_rel mblpavr
            JOIN mrp_bom_line mbl ON mbl.id = mblpavr.mrp_bom_line_id
            JOIN mrp_bom mb ON mbl.bom_id = mb.id
            JOIN product_attribute_value pav ON pav.id = mblpavr.product_attribute_value_id
            LEFT JOIN product_template_attribute_line ptal
                ON ptal.product_tmpl_id = mb.product_tmpl_id
                    AND ptal.attribute_id = pav.attribute_id
            WHERE ptal.id IS NULL
            GROUP BY pav.attribute_id, mb.product_tmpl_id"""
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
            (ptav_active, product_attribute_value_id, product_tmpl_id, attribute_line_id)
        SELECT
            False, pavppr.product_attribute_value_id, pp.product_tmpl_id, ptal.id
        FROM product_attribute_value_product_product_rel pavppr
        JOIN product_product pp ON pp.id = pavppr.product_product_id
        JOIN product_attribute_value pav ON pav.id = pavppr.product_attribute_value_id
        JOIN product_template_attribute_line ptal
            ON ptal.product_tmpl_id = pp.product_tmpl_id
            AND pav.attribute_id = ptal.attribute_id
        LEFT JOIN product_template_attribute_value ptav
            ON ptav.product_attribute_value_id = pavppr.product_attribute_value_id
            AND ptav.product_tmpl_id = pp.product_tmpl_id
            AND ptav.attribute_line_id = ptal.id
        WHERE ptav.id IS NULL
        GROUP BY pavppr.product_attribute_value_id, pp.product_tmpl_id, ptal.id""",
    )
    if openupgrade.table_exists(env.cr, "mrp_bom_line"):
        # make use of mrp_bom_line_product_attribute_value_rel
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO product_template_attribute_value
                (ptav_active, product_attribute_value_id, product_tmpl_id, attribute_line_id)
            SELECT False, mblpavr.product_attribute_value_id, mb.product_tmpl_id, ptal.id
            FROM mrp_bom_line_product_attribute_value_rel mblpavr
            JOIN mrp_bom_line mbl ON mbl.id = mblpavr.mrp_bom_line_id
            JOIN mrp_bom mb ON mbl.bom_id = mb.id
            JOIN product_attribute_value pav ON pav.id = mblpavr.product_attribute_value_id
            JOIN product_template_attribute_line ptal ON (
                ptal.product_tmpl_id = mb.product_tmpl_id
                AND pav.attribute_id = ptal.attribute_id)
            LEFT JOIN product_template_attribute_value ptav
                ON (ptav.product_attribute_value_id = pav.id
                AND ptav.product_tmpl_id = mb.product_tmpl_id
                AND ptav.attribute_line_id = ptal.id)
            WHERE ptav.id IS NULL
            GROUP BY mblpavr.product_attribute_value_id, mb.product_tmpl_id, ptal.id""",
        )


def merge_variants_with_same_attributes(env):
    openupgrade.logged_query(
        env.cr, """
        WITH templates AS (
            SELECT pt.id, pp.combination_indices, COUNT(*)
            FROM product_product pp
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE pp.combination_indices IS NOT NULL
            GROUP BY pt.id, pp.combination_indices
            HAVING COUNT(*) > 1
        )
        SELECT pp.id, pp.product_tmpl_id
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        JOIN templates ON (templates.id = pt.id
            AND templates.combination_indices = pp.combination_indices)"""
    )
    templates = {}
    for product_id, template_id in env.cr.fetchall():
        templates.setdefault(template_id, []).append(product_id)
    for template_id in templates:
        openupgrade_merge_records.merge_records(
            env, 'product.product', templates[template_id][1:],
            templates[template_id][0], field_spec=None, method='sql',
            delete=True, exclude_columns=None, model_table='product_product')


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
    merge_variants_with_same_attributes(env)


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


def fill_product_template_attribute_value__attribute_id_related(env):
    """We fill the attribute_id of ptavs in pre-migration for a reason:
     When the module is loading, the new product_attribute_product_template_rel
     table will be automatically created and filled (it's an stored computed m2m),
     thus the attribute_id of ptavs is needed in the compute."""
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE product_template_attribute_value "
        "ADD COLUMN attribute_id INT4",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template_attribute_value ptav
        SET attribute_id = ptal.attribute_id
        FROM product_template_attribute_line ptal
        WHERE ptav.attribute_line_id = ptal.id""",
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
    fill_product_template_attribute_value__attribute_id_related(env)
