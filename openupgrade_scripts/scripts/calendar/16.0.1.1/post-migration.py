# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_translations_to_delete = [
    "calendar_template_meeting_changedate",
    "calendar_template_meeting_invitation",
    "calendar_template_meeting_reminder",
    "calendar_template_meeting_update",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "calendar", "16.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "calendar", _translations_to_delete)
