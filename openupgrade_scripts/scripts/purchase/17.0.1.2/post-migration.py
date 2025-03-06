# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "purchase", "17.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "purchase",
        [
            "email_template_edi_purchase_done",
            "email_template_edi_purchase_reminder",
        ],
    )
