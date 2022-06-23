from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "auth_signup", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "auth_signup",
        [
            "mail_template_data_unregistered_users",
            "mail_template_user_signup_account_created",
            "reset_password_email",
            "set_password_email",
        ],
    )
