# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo import tools

_column_copies = {
    'mrp_production': [
        ('state', None, None),
    ],
}

_column_copies2 = {
    'mrp_workorder': [
        ('state', None, None),
    ],
}

_column_renames = {
    'mrp_bom': [
        ('date_stop', None),
    ],
    'stock_move': [
        ('consumed_for', None),
    ],
    'mrp_workorder': [
        ('sequence', None),
        ('cycle', None),
        ('hour', None),
    ],
    'mrp_routing_workcenter': [
        ('hour_nbr', None),
        ('cycle_nbr', None),
    ],
}

_column_renames2 = {
    'mrp_workorder': [
        ('delay', None),
    ],
}

_field_renames = [
    ('mrp.bom', 'mrp_bom', 'product_uom', 'product_uom_id'),
    ('mrp.bom.line', 'mrp_bom_line', 'product_uom', 'product_uom_id'),
    ('mrp.production', 'mrp_production', 'date_planned',
     'date_planned_start'),
    ('mrp.production', 'mrp_production', 'move_lines', 'move_raw_ids'),
    ('mrp.production', 'mrp_production', 'move_created_ids2',
     'move_finished_ids'),
    ('mrp.production', 'mrp_production', 'product_uom', 'product_uom_id'),
    ('mrp.production', 'mrp_production', 'workcenter_lines', 'workorder_ids'),
    ('mrp.routing', 'mrp_routing', 'workcenter_lines', 'operation_ids'),
    ('mrp.workcenter', 'mrp_workcenter', 'capacity_per_cycle', 'capacity'),
]

_field_renames2 = [
    ('mrp.workorder', 'mrp_workorder', 'date_planned', 'date_planned_start'),
    ('mrp.workorder', 'mrp_workorder', 'date_planned_end',
     'date_planned_finished'),
    ('mrp.workorder', 'mrp_workorder', 'product', 'product_id'),
    ('mrp.workorder', 'mrp_workorder', 'qty', 'qty_production'),
    ('mrp.workorder', 'mrp_workorder', 'uom', 'product_uom_id'),
]

_xmlid_renames = [
    ('base.menu_mrp_config', 'mrp.menu_mrp_config'),
    ('base.menu_mrp_root', 'mrp.menu_mrp_root'),
]


def delete_old_workorder_model(cr):
    """Delete old mrp.workorder model that was a report."""
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model WHERE model = %s",
        ('mrp.workorder',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_fields WHERE relation = %s",
        ('mrp.workorder',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_data WHERE model = %s",
        ('mrp.workorder',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_data WHERE name = %s AND model = 'ir.model'",
        ('model_mrp_workorder',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_data WHERE name LIKE %s AND"
        " model = 'ir.model.fields'",
        ('field_mrp_workorder_%',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_attachment WHERE res_model = %s",
        ('mrp.workorder',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_fields WHERE model = %s",
        ('mrp.workorder',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_translation WHERE name LIKE %s",
        ('mrp.workorder,%',)
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_property WHERE value_reference LIKE %s",
        ('mrp.workorder,%',)
    )


def rename_mrp_workorder(cr):
    """Special case where in v9, you have a model called mrp.workorder that is
    an SQL view report, but on v10 it's a model, which corresponds to a
    renamed model.
    """
    tools.drop_view_if_exists(cr, 'mrp_workorder')
    delete_old_workorder_model(cr)
    openupgrade.rename_tables(
        cr, [('mrp_production_workcenter_line', 'mrp_workorder')],
    )
    openupgrade.rename_models(
        cr, [('mrp.production.workcenter.line', 'mrp.workorder')],
    )
    # Fix the external ID:
    cr.execute("""
        SELECT id FROM ir_model
        WHERE model = 'mrp.workorder'
    """)
    model_id = cr.fetchone()
    openupgrade.logged_query(
        cr,
        "UPDATE ir_model_data SET res_id = %s "
        "WHERE name = 'model_mrp_workorder'",
        model_id
    )


def prepopulate_fields(cr):
    if openupgrade.column_exists(cr, 'mrp_production', 'picking_type_id'):
        return False
    cr.execute(
        """
        ALTER TABLE mrp_production
        ADD COLUMN picking_type_id INTEGER
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    rename_mrp_workorder(cr)
    openupgrade.copy_columns(cr, _column_copies)
    if openupgrade.column_exists(cr, 'mrp_workorder', 'state'):
        # if mrp_operations was installed
        openupgrade.copy_columns(cr, _column_copies2)
        openupgrade.rename_columns(cr, _column_renames2)
        openupgrade.rename_fields(env, _field_renames2)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    prepopulate_fields(cr)
    openupgrade.rename_xmlids(cr, _xmlid_renames)
