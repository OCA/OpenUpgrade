# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "purchase_requisition", "migrations/13.0.0.1/noupdate_changes.xml")
    openupgrade.rename_xmlids(
        env.cr, [
            (
                "purchase_requisition.access_purchase_requisition_stock_manager",
                "purchase_requisition_stock.access_purchase_requisition_stock_manager",
            ),
            (
                "purchase_requisition.access_purchase_requisition_line_stock_manager",
                "purchase_requisition_stock.access_purchase_requisition_line_stock_manager",
            ),
        ]
    )
