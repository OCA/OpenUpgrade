# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_translations_to_delete = [
    "mail_template_data_portal_welcome",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "portal", "16.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "portal", _translations_to_delete)
