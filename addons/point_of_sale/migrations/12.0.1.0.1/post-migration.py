# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_pos_order_amounts(env):
    """Avoid null values in required fields."""
    env["pos.order"].search([])._compute_batch_amount_all()


def fill_pos_order_line_prices(env):
    """Avoid null values in required fields."""
    env["pos.order.line"].search([])._onchange_amount_line_all()


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_pos_order_amounts(env)
    fill_pos_order_line_prices(env)
    openupgrade.load_data(
        cr, 'point_of_sale', 'migrations/12.0.1.0.1/noupdate_changes.xml')
