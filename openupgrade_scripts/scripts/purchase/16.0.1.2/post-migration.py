# Copyright 2024 Le Filament
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "purchase", "16.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "purchase",
        [
            "email_template_edi_purchase",
            "email_template_edi_purchase_done",
            "email_template_edi_purchase_reminder",
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["purchase.mail_notification_confirm"],
    )
