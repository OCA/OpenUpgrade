from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Rename the removed ``_get_mail_partner`` helper to ``_get_mail_author``
    in the stored ``lang`` of these templates, as the 19.0 data-load render
    aborts before the existing post-migration could clear the field.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_template
           SET lang = REPLACE(lang, '_get_mail_partner', '_get_mail_author')
         WHERE model = 'loyalty.card'
           AND lang LIKE '%%_get_mail_partner%%'
        """,
    )
