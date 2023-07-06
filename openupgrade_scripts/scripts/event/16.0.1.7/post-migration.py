# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_translations_to_delete = [
    "event_registration_mail_template_badge",
    "event_reminder",
    "event_subscription",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "event", "16.0.1.7/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "event", _translations_to_delete)
