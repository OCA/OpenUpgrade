from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mail_activity_type WHERE id IN (
            SELECT imd.res_id FROM ir_model_data imd
            WHERE imd.model = 'mail.activity.type'
              AND imd.module = 'website_slides'
              AND imd.name = 'mail_activity_data_access_request'
        )
        """,
    )
