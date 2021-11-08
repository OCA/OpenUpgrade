# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def website_cookie_notice_post_migration(env):
    cookie_message = env.ref("website.cookie_message", raise_if_not_found=False)
    if cookie_message:
        websites = env["website"].search([])
        websites.write({"cookies_bar": True})
        openupgrade.logged_query(
            env.cr,
            """
            WITH keys AS (
                SELECT key
                FROM ir_ui_view iuv
                JOIN ir_model_data imd ON (imd.model = 'ir.ui.view'
                    AND imd.res_id = iuv.id AND module = 'website')
                WHERE imd.name IN ('cookie_message', 'cookie_message_container')
            )
            DELETE FROM ir_ui_view iuv
            USING keys
            WHERE iuv.key = keys.key""",
        )
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM ir_model_data imd
            WHERE imd.model = 'ir.ui.view' AND module = 'website'
                AND imd.name IN ('cookie_message', 'cookie_message_container')""",
        )


@openupgrade.migrate()
def migrate(env, version):
    website_cookie_notice_post_migration(env)
