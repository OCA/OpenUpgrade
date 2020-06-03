# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def fill_pos_order_line_prices(env):
    """Avoid null values in required fields."""
    env.cr.execute(
        """
        SELECT count(*)
        FROM ir_module_module
        WHERE name = 'pos_pricelist'
        AND state = 'to upgrade';
        """
    )
    if env.cr.fetchone()[0] == 1:
        _logger.info(
            "Skipped the recompute of price_subtotal and price_subtotal_incl"
            " for all pos.order.line, because pos_pricelist was installed")
        return

    for lines in openupgrade.chunked(
        env["pos.order.line"].search([]),
        single=False
    ):
        lines._onchange_amount_line_all()


def fill_pos_order_amounts(env):
    """Avoid null values in required fields."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order po
            SET amount_paid = tmp.amount_paid,
            amount_return = tmp.amount_return
        FROM (
            SELECT
                po.id,
                sum(absl.amount) AS amount_paid,
                sum(LEAST(absl.amount, 0)) AS amount_return
            FROM pos_order po
            INNER JOIN account_bank_statement_line absl
                ON absl.pos_statement_id = po.id
            GROUP BY po.id
        ) AS tmp
        WHERE po.id = tmp.id;
        """
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order po
            SET amount_total = tmp.amount_total,
            amount_tax = tmp.amount_total - tmp.amount_untaxed
        FROM (
            SELECT
                po.id,
                sum(pol.price_subtotal_incl) AS amount_total,
                sum(pol.price_subtotal) AS amount_untaxed
            FROM pos_order po
            INNER JOIN pos_order_line pol
                ON pol.order_id = po.id
            GROUP BY po.id
        ) AS tmp
        WHERE po.id = tmp.id;
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_pos_order_line_prices(env)
    fill_pos_order_amounts(env)
    openupgrade.load_data(
        cr, 'point_of_sale', 'migrations/12.0.1.0.1/noupdate_changes.xml')
