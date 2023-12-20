# Copyright 2023 GRAP - Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _fast_fill_sale_order_amount_unpaid(env):
    _logger.info("Fast computation of sale_order.amount_unpaid ...")
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS amount_unpaid numeric",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        set amount_unpaid = tmp.amount_unpaid
        FROM (SELECT
            so.id,
            so.amount_total - sum(COALESCE(aml.price_total, 0)) as amount_unpaid
            FROM sale_order so
            INNER JOIN sale_order_line sol
                ON sol.order_id = so.id
            LEFT JOIN sale_order_line_invoice_rel rel
                ON rel.order_line_id = sol.id
            LEFT JOIN account_move_line aml
                ON aml.id = rel.invoice_line_id
                AND aml.parent_state != 'cancel'
            GROUP BY so.id
        ) tmp
        WHERE sale_order.id = tmp.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fast_fill_sale_order_amount_unpaid(env)
