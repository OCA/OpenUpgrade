# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo import tools

_column_copies = {
    'mrp_production': [
        ('state', None, None)
    ],
    'mrp_workorder': [
        ('state', None, None)
    ],
}

_column_renames = {
    'stock_move': [
        ('consumed_for', None),
    ],
}

_field_renames = [
    ('mrp.bom', 'mrp_bom', 'product_uom', 'product_uom_id'),
    ('mrp.bom.line', 'mrp_bom_line', 'product_uom', 'product_uom_id'),
    ('mrp.production', 'mrp_production', 'date_planned', 'date_planned_start'),
    ('mrp.production', 'mrp_production', 'move_lines', 'move_raw_ids'),
    ('mrp.production', 'mrp_production', 'product_uom', 'product_uom_id'),
    ('mrp.production', 'mrp_production', 'workcenter_lines', 'workorder_ids'),
    ('mrp.routing', 'mrp_routing', 'workcenter_lines', 'operation_ids'),
    ('mrp.workcenter', 'mrp_workcenter', 'capacity_per_cycle', 'capacity'),
    ('mrp.workorder', 'mrp_workorder', 'date_planned', 'date_planned_start'),
]

_table_renames = [
    ('mrp_production_workcenter_line', 'mrp_workorder'),
]

_xmlid_renames = [
    ('base.menu_mrp_config', 'mrp.menu_mrp_config'),
    ('base.menu_mrp_root', 'mrp.menu_mrp_root'),
]


def prepopulate_fields(cr):
    cr.execute(
        """
        ALTER TABLE mrp_production
        ADD COLUMN picking_type_id INTEGER
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    tools.drop_view_if_exists(cr, 'mrp_workorder')
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    prepopulate_fields(cr)
    openupgrade.rename_xmlids(cr, _xmlid_renames)
