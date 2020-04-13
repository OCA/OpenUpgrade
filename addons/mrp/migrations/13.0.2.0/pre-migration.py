# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('mrp.subproduct', 'mrp.bom.byproduct'),
]

_table_renames = [
    ('mrp_subproduct', 'mrp_bom_byproduct'),
    ('mrp_bom_line_product_attribute_value_rel', 'mrp_bom_line_product_template_attribute_value_rel'),
]

_field_renames = [
    ('mrp.workorder', 'mrp_workorder', 'final_lot_id', 'finished_lot_id'),
    ('mrp.bom.line', 'mrp_bom_line', 'attribute_value_ids', 'bom_product_template_attribute_value_ids'),
    ('mrp.production', 'mrp_production', 'availability', 'reservation_state'),
    ('mrp.production', 'mrp_production', 'propagate', 'propagate_cancel'),
]

_column_renames = {
    'stock_move_line': [
        ('lot_produced_id', None),
    ],
    'mrp_bom_line_product_template_attribute_value_rel': [
        ('product_attribute_value_id', 'product_template_attribute_value_id'),
    ],
}

_xmlid_renames = [
    # ir.model.access
    ('mrp_byproduct.access_mrp_subproduct_manager', 'mrp.access_mrp_bom_byproduct_manager'),
    ('mrp_byproduct.access_mrp_subproduct_user', 'mrp.access_mrp_bom_byproduct_user'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
