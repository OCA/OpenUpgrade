# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _link_work_orders(env):
    """Link work order sequentiation according old field next_work_order_id."""
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mrp_workorder_dependencies_rel
        (workorder_id, blocked_by_id)
        SELECT next_work_order_id, id
        FROM mrp_workorder
        WHERE next_work_order_id IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _link_work_orders(env)
