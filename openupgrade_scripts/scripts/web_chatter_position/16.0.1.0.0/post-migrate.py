from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Field 'chatter_position' was defined in module 'web_responsive' before it was
    # moved to 'web_chatter_position'. In 'web_responsive' the allowed values have
    # been ['normal', 'sided'].
    # In case users installed 'web_chatter_position' along with 'web_responsive' field
    # 'chatter_position' potentially was already in the db with old values, which are
    # not supported.
    # This migration covers this scenario by correcting unsupported values.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_users
        SET chatter_position = 'auto'
        WHERE chatter_position not in ('auto', 'bottom', 'sided')
        """,
    )
