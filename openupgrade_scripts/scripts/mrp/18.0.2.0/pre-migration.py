# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

add_columns = [
    ("product.document", "attached_on_mrp", "char", "hidden"),
]

copy_columns = {
    "mrp_production": [
        ("location_dest_id", "location_final_id", "integer"),
    ],
}


def mrp_workorder_sequence(env):
    """
    Precreate sequence field and fill with operation_id.sequence or 100
    """
    openupgrade.add_columns(env, [("mrp.workorder", "sequence", "integer", 100)])
    env.cr.execute(
        """
        UPDATE mrp_workorder
        SET sequence=COALESCE(mrp_routing_workcenter.sequence, mrp_workorder.sequence)
        FROM mrp_routing_workcenter
        WHERE mrp_workorder.operation_id=mrp_routing_workcenter.id
        """
    )


def fill_mrp_stock_move_location_dest_id(env):
    """
    MRP stock moves:
    In v17, location_dest_id contained the destination of the move.
    During the migration it is preserved as location_final_id.
    For MRP moves, the new location_dest_id must preserve this value
    instead of using the generic stock logic.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move
        SET location_dest_id = location_final_id
        WHERE (
            raw_material_production_id IS NOT NULL
            OR production_id IS NOT NULL
        )
        AND location_final_id IS NOT NULL;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, add_columns)
    openupgrade.copy_columns(env.cr, copy_columns)
    mrp_workorder_sequence(env)
    fill_mrp_stock_move_location_dest_id(env)
