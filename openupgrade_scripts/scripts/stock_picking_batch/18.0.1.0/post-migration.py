# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _adjust_stock_picking_batch_sequence(env):
    """As the order in the tree view and report is now by batch_sequence,
    we need to set the batch_sequence field
    to maintain the same order as in the previous version,
    because this new field does not have a default value.
    The order is taken from the picking model.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking sp
        SET batch_sequence = sub.row_number
        FROM (
            SELECT id, row_number()
            OVER (
                PARTITION BY batch_id
                ORDER BY priority desc, scheduled_date asc, id desc
            )
            FROM stock_picking
        ) as sub
        WHERE sub.id = sp.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _adjust_stock_picking_batch_sequence(env)
