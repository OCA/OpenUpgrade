# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    "mrp_production": [
        ("priority", None, None),
        ("state", None, None),
    ],
}


def switch_flexible_consumption_to_warning(env):
    """For benefiting from this new feature."""
    openupgrade.logged_query(
        env.cr,
        "UPDATE mrp_bom SET consumption = 'warning' WHERE consumption='flexible'",
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE mrp_workorder SET consumption = 'warning' WHERE consumption='flexible'",
    )


def fill_mrp_production__consumption(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE mrp_production ADD consumption VARCHAR"
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE mrp_production mp
        SET consumption = mb.consumption
        FROM mrp_bom mb
        WHERE mb.id = mp.bom_id
        """,
    )


def fill_mrp_routing_workcenter_bom_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mrp_routing_workcenter
        ADD COLUMN bom_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mrp_routing_workcenter
        ADD COLUMN old_routing_workcenter_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mrp_routing_workcenter
        ALTER COLUMN routing_id DROP NOT NULL""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mrp_routing_workcenter
        ALTER COLUMN batch DROP NOT NULL""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mrp_routing_workcenter (name, workcenter_id, sequence,
            company_id, worksheet_type, note, worksheet_google_slide, time_mode,
            time_mode_batch, time_cycle_manual, create_uid, write_uid,
            create_date, write_date, bom_id, routing_id,
            old_routing_workcenter_id)
        SELECT mrw.name, mrw.workcenter_id, mrw.sequence, mrw.company_id,
            mrw.worksheet_type, mrw.note, mrw.worksheet_google_slide,
            mrw.time_mode, mrw.time_mode_batch, mrw.time_cycle_manual,
            mrw.create_uid, mb.write_uid, mb.create_date, mb.create_date,
            mb.id, mrw.routing_id, mrw.id
        FROM mrp_routing_workcenter mrw
        JOIN mrp_bom mb ON mb.routing_id = mrw.routing_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_bom_line mbl
        SET operation_id = mrw.id
        FROM mrp_bom mb
        JOIN mrp_routing_workcenter mrw ON mrw.bom_id = mb.id
        JOIN mrp_routing_workcenter mrw2 ON mrw.old_routing_workcenter_id = mrw2.id
        WHERE mbl.bom_id = mb.id AND mbl.operation_id = mrw2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_bom_byproduct mbp
        SET operation_id = mrw.id
        FROM mrp_bom mb
        JOIN mrp_routing_workcenter mrw ON mrw.bom_id = mb.id
        JOIN mrp_routing_workcenter mrw2 ON mrw.old_routing_workcenter_id = mrw2.id
        WHERE mbp.bom_id = mb.id AND mbp.operation_id = mrw2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_workorder mw
        SET operation_id = mrw.id
        FROM mrp_production mp
        JOIN mrp_bom mb ON mp.bom_id = mb.id
        JOIN mrp_routing_workcenter mrw ON mrw.bom_id = mb.id
        JOIN mrp_routing_workcenter mrw2 ON mrw.old_routing_workcenter_id = mrw2.id
        WHERE mw.production_id = mp.id AND mw.operation_id = mrw2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET operation_id = mrw.id
        FROM mrp_production mp
        JOIN mrp_bom mb ON mp.bom_id = mb.id
        JOIN mrp_routing_workcenter mrw ON mrw.bom_id = mb.id
        JOIN mrp_routing_workcenter mrw2 ON mrw.old_routing_workcenter_id = mrw2.id
        WHERE sm.raw_material_production_id = mp.id AND sm.operation_id = mrw2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mrp_routing_workcenter
        WHERE old_routing_workcenter_id IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    switch_flexible_consumption_to_warning(env)
    fill_mrp_production__consumption(env)
    fill_mrp_routing_workcenter_bom_id(env)
