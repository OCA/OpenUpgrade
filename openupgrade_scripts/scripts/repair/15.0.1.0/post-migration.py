# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "repair", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "repair",
        ["mail_template_repair_quotation"],
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("invoice_except", "2binvoiced")],
        table="repair_order",
    )
