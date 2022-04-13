# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def website_cookie_notice_post_migration(env):
    cookie_message = env.ref("website.cookie_message", raise_if_not_found=False)
    if cookie_message:
        websites = env["website"].search([])
        for website in websites:
            website.write({"cookies_bar": True})
        env.cr.execute(
            """WITH keys AS (
                SELECT key
                FROM ir_ui_view iuv
                JOIN ir_model_data imd ON (imd.model = 'ir.ui.view'
                    AND imd.res_id = iuv.id AND module = 'website')
                WHERE imd.name IN ('cookie_message', 'cookie_message_container')
            )
            SELECT iuv.id
            FROM ir_ui_view iuv
            JOIN keys ON iuv.key = keys.key""",
        )
        view_ids = [x[0] for x in env.cr.fetchall()]
        if view_ids:
            env["ir.ui.view"].browse(view_ids).unlink()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["website.aboutus_page"])
    website_cookie_notice_post_migration(env)
