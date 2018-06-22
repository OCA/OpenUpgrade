# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_sale_line_id(env):
    openupgrade.logged_query(
        env.cr, """
          UPDATE purchase_order_line pol
          SET sale_line_id = po.sale_line_id
          FROM procurement_order po
          WHERE po.purchase_line_id = pol.id
            AND po.sale_line_id IS NOT NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'stock_dropshipping', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    update_sale_line_id(env)
