# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fill_mrp_workorder_costs_hour(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_workorder mwo
        SET costs_hour = mwc.costs_hour
        FROM mrp_workcenter mwc
        WHERE mwo.workcenter_id = mwc.id AND mwo.state = 'done'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_mrp_workorder_costs_hour(env)
    openupgrade.load_data(env.cr, "mrp", "15.0.2.0/noupdate_changes.xml")
