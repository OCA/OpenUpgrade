from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # This method will copy records has scope = '2fa_trusted_device'
    # from res_users_apikeys to auth_totp_device
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO auth_totp_device (name, user_id, scope, index, key, create_date)
        SELECT name, user_id, 'browser', index, key, create_date
        FROM res_users_apikeys
        WHERE scope = '2fa_trusted_device'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM res_users_apikeys
        WHERE scope = '2fa_trusted_device'""",
    )
