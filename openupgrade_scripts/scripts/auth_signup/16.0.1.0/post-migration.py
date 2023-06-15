# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_translations_to_delete = [
    "mail_template_data_unregistered_users",
    "mail_template_user_signup_account_created",
    "reset_password_email",
    "set_password_email",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "auth_signup", "16.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "auth_signup", _translations_to_delete
    )
