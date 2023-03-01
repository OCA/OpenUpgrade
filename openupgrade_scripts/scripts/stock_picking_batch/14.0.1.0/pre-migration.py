# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _prefill_scheduled_date(env):
    """Add manually the field and do the same as the compute, but through SQL."""
    openupgrade.add_fields(
        env,
        [
            (
                "scheduled_date",
                "stock.picking.batch",
                "stock_picking_batch",
                "datetime",
                False,
                "stock_picking_batch",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking_batch spb
        SET scheduled_date = sub.scheduled_date
        FROM (
            SELECT batch_id, MIN(scheduled_date) AS scheduled_date
            FROM stock_picking
            WHERE batch_id IS NOT NULL
            GROUP BY batch_id
        ) sub
        WHERE spb.id = sub.batch_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _prefill_scheduled_date(env)
