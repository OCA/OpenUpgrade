# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "auth_totp_mail", "16.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "auth_totp_mail", ["mail_template_totp_invite"], ["name", "email_from"]
    )
