# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 Andrii Skrypka <andrijskrypa@ukr.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('mrp.subproduct', 'mrp.bom.byproduct'),
]

_table_renames = [
    ('mrp_bom_line_product_attribute_value_rel', 'mrp_bom_line_product_template_attribute_value_rel'),
]

_mrp_subproduct_table_renames = [
    ('mrp_subproduct', 'mrp_bom_byproduct'),
]

_field_renames = [
    ('mrp.workorder', 'mrp_workorder', 'final_lot_id', 'finished_lot_id'),
    ('mrp.bom', 'mrp_bom', 'sub_products', 'byproduct_ids'),
    ('mrp.bom.line', 'mrp_bom_line', 'attribute_value_ids', 'bom_product_template_attribute_value_ids'),
    ('mrp.production', 'mrp_production', 'propagate', 'propagate_cancel'),
    ('stock.move', 'stock_move', 'subproduct_id', 'byproduct_id'),
]

_column_renames = {
    'stock_move_line': [
        ('lot_produced_id', None),
    ],
}

_column_copies = {
    'mrp_production': [
        ('availability', 'reservation_state', None),
    ],
    'mrp_bom_line_product_template_attribute_value_rel': [
        ('product_attribute_value_id', 'product_template_attribute_value_id', None),
    ],
}

_mrp_subproduct_xmlid_renames = [
    # ir.model.access
    ('mrp.access_mrp_subproduct_manager', 'mrp.access_mrp_bom_byproduct_manager'),
    ('mrp.access_mrp_subproduct_user', 'mrp.access_mrp_bom_byproduct_user'),
]


def fast_precreation_and_fill_mrp_bom_byproduct(env):
    """Faster way"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE mrp_bom_byproduct
        ADD COLUMN company_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE mrp_bom_byproduct
        ADD COLUMN routing_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_bom_byproduct mbb
        SET company_id = mb.company_id, routing_id = mb.routing_id
        FROM mrp_bom mb
        WHERE mb.id = mbb.bom_id""",
    )


def fast_precreation_and_fill_mrp_bom_line(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE mrp_bom_line
        ADD COLUMN company_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_bom_line mbl
        SET company_id = mb.company_id
        FROM mrp_bom mb
        WHERE mb.id = mbl.bom_id""",
    )


def fill_bom_product_template_attribute_value(env):
    """ Convert product.attribute.value ids to product.template.attribute.value ids"""
    openupgrade.logged_query(env.cr, """
    UPDATE mrp_bom_line_product_template_attribute_value_rel mbl_ptav_rel
    SET product_template_attribute_value_id = (
        SELECT id
        FROM product_template_attribute_value ptav
        WHERE mb.product_tmpl_id = ptav.product_tmpl_id
            AND mbl_ptav_rel.product_attribute_value_id = ptav.product_attribute_value_id
        LIMIT 1
    )
    FROM mrp_bom_line mbl
    JOIN mrp_bom mb ON mbl.bom_id = mb.id
    WHERE mbl.id = mbl_ptav_rel.mrp_bom_line_id
    """)
    openupgrade.drop_columns(env.cr, [
        ("mrp_bom_line_product_template_attribute_value_rel", "product_attribute_value_id")])


def mapped_reservation_state(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_production
        SET reservation_state = CASE
          WHEN reservation_state = 'partially_available' THEN 'assigned'
          WHEN reservation_state = 'none' THEN NULL
          END
        WHERE reservation_state in ('partially_available', 'none')"""
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.remove_tables_fks(env.cr, 'mrp_bom_line_product_attribute_value_rel')
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    if openupgrade.table_exists(env.cr, 'mrp_subproduct'):
        openupgrade.rename_tables(env.cr, _mrp_subproduct_table_renames)
        fast_precreation_and_fill_mrp_bom_byproduct(env)
        openupgrade.rename_xmlids(env.cr, _mrp_subproduct_xmlid_renames)
    fast_precreation_and_fill_mrp_bom_line(env)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_columns(env.cr, _column_renames)
    fill_bom_product_template_attribute_value(env)
    mapped_reservation_state(env)
