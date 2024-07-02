# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, "fetchmail_server", "use_microsoft_outlook_service"
    ):
        openupgrade.logged_query(
            env.cr,
            """UPDATE fetchmail_server
            SET server_type = 'outlook'
            WHERE use_microsoft_outlook_service
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """UPDATE ir_mail_server
        SET smtp_authentication = 'outlook'
        WHERE use_microsoft_outlook_service
        """,
    )
