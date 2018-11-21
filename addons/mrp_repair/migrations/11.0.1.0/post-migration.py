# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_stock_move_repair_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET repair_id = mr.id
        FROM mrp_repair mr
        WHERE mr.move_id = sm.id
        """
    )


def reset_mrp_repair_price_unit(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_repair_line
        SET price_unit = 0
        WHERE NOT %s
        """, (AsIs(openupgrade.get_legacy_name('to_invoice')), ),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_repair_fee
        SET price_unit = 0
        WHERE NOT %s
        """, (AsIs(openupgrade.get_legacy_name('to_invoice')), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_move_repair_id(env)
    openupgrade.load_data(
        env.cr, 'mrp_repair', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
