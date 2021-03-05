# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_stock_picking_batch_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE stock_picking_batch spb
        SET company_id = sp.company_id
        FROM stock_picking sp
        WHERE sp.batch_id = spb.id AND spb.company_id IS NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_picking_batch_company_id(env.cr)
