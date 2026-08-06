# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(
        env, [("sale.order.line", "event_slot_id", "many2one", None, "sale_order_line")]
    )
