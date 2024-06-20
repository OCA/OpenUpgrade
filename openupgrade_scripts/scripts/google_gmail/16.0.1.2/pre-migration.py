# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(cr, "fetchmail_server", "use_google_gmail_service"):
        openupgrade.logged_query(
            env.cr,
            """UPDATE fetchmail_server
            SET server_type = 'gmail'
            WHERE use_google_gmail_service
            """,
        )
    openupgrade.logged_query(
        cr,
        """UPDATE ir_mail_server
        SET smtp_authentication = 'gmail'
        WHERE use_google_gmail_service
        """,
    )
