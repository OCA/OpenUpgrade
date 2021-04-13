# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.addons.mrp import _create_warehouse_data


def fill_mrp_workcenter_resource_calendar_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_workcenter mw
        SET resource_calendar_id = rr.calendar_id
        FROM resource_resource rr
        WHERE mw.resource_id = rr.id AND mw.resource_calendar_id IS NULL
        """
    )


def fill_mrp_workcenter_productivity_loss_loss_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_workcenter_productivity_loss wpl
        SET loss_id = wplt.id
        FROM mrp_workcenter_productivity_loss_type wplt
        WHERE wpl.loss_id IS NULL AND wpl.loss_type = wplt.loss_type
        """,
    )


def fill_stock_warehouse_picking_types(env):
    # It breaks in purchase_stock if we do this in an end-migration instead.
    # We need to fill the new pbm_type_id field to assure calling in
    # _create_or_update_global_routes_rules() in other modules doesn't break.
    warehouses = env['stock.warehouse'].with_context(active_test=False).search([])
    for warehouse in warehouses:
        warehouse.write(
            warehouse._create_or_update_sequences_and_picking_types())


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_mrp_workcenter_resource_calendar_id(cr)
    openupgrade.load_data(
        cr, 'mrp', 'migrations/12.0.2.0/noupdate_changes.xml')
    fill_mrp_workcenter_productivity_loss_loss_id(cr)
    fill_stock_warehouse_picking_types(env)
    _create_warehouse_data(cr, env.registry)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'mrp.sequence_mrp_prod',
        ],
    )
