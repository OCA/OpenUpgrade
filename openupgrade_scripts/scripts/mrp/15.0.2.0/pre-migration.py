# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fill_mrp_routing_workcenter_active(env):
    if openupgrade.column_exists(env.cr, "mrp_routing_workcenter", "active"):
        return
    openupgrade.add_fields(
        env,
        [
            (
                "active",
                "mrp.routing.workcenter",
                "mrp_routing_workcenter",
                "boolean",
                "bool",
                "mrp",
                True,
            )
        ],
    )


def fill_mrp_routing_workcenter_bom_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_routing_workcenter mrw
        SET bom_id = mbl.bom_id
        FROM mrp_bom_line mbl
        WHERE mrw.bom_id IS NULL AND mbl.operation_id = mrw.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_routing_workcenter mrw
        SET bom_id = mbb.bom_id
        FROM mrp_bom_byproduct mbb
        WHERE mrw.bom_id IS NULL AND mbb.operation_id = mrw.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_routing_workcenter mrw
        SET bom_id = mp.bom_id
        FROM stock_move sm
        JOIN mrp_production mp ON sm.raw_material_production_id = mp.id
        WHERE mrw.bom_id IS NULL AND sm.operation_id = mrw.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_mrp_routing_workcenter_active(env)
    fill_mrp_routing_workcenter_bom_id(env)
    openupgrade.convert_field_to_html(
        env.cr, "mrp_routing_workcenter", "note", "note", verbose=False
    )
    openupgrade.convert_field_to_html(
        env.cr, "mrp_workcenter", "note", "note", verbose=False
    )
