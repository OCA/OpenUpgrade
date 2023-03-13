# Copyright 2023 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "calendar_sms", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "calendar_sms",
        [
            "sms_template_data_calendar_reminder",
        ],
    )
