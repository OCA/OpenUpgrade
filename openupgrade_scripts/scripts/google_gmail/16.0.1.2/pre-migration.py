from openupgradelib import openupgrade


def fetchmail_server_set_gmail_server_type(env):
    if openupgrade.column_exists(
        env.cr, "fetchmail_server", "use_google_gmail_service"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE fetchmail_server
            SET server_type='gmail'
            WHERE use_google_gmail_service = true;
            """,
        )


def ir_mail_server_set_gmail_smtp_authentication(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_mail_server
        SET smtp_authentication='gmail'
        WHERE use_google_gmail_service = true;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fetchmail_server_set_gmail_server_type(env)
    ir_mail_server_set_gmail_smtp_authentication(env)
