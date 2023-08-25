# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re

from openupgradelib import openupgrade
from openupgradelib.openupgrade_140 import convert_html_string_13to14


def extract_footer_copyright_company_name(env):
    """Replace Copyright content in the footer so as not to lose
    content from previous versions if the copyright has been customised."""
    for website in env["website"].search([]):
        # Search for old copyright and if it does not exist set the default company name
        web_frontend_layout_view = env["ir.ui.view"].search(
            [("key", "=", "web.frontend_layout"), ("website_id", "=", website.id)]
        )
        if web_frontend_layout_view:
            frontend_layout_pattern = r"<span(?:.*?)>(.*?)</span>"
            frontend_layout_matches = re.findall(
                frontend_layout_pattern,
                web_frontend_layout_view.arch_db,
                re.DOTALL,
            )
            copyright_content = " ".join(
                match.strip() for match in frontend_layout_matches
            )
        else:
            copyright_content = f"Copyright © {website.company_id.name}"
        # Set new copyright
        website_layout_view = env.ref("website.layout")
        website_layout_pattern = (
            r'<span class="o_footer_copyright_name mr-2">(.*?)<\/span>'
        )
        website_layout_matches, *_ = re.findall(
            website_layout_pattern, website_layout_view.arch_db, re.DOTALL
        )
        new_arch = website_layout_view.arch_db.replace(
            website_layout_matches, copyright_content
        )
        website_layout_view.with_context(website_id=website.id).arch_db = new_arch


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


def convert_html_string(env):
    website_views = env["ir.ui.view"].search(
        [("type", "=", "qweb"), ("website_id", "!=", False)]
    )
    for view in website_views:
        new_arch_db = convert_html_string_13to14(view.arch_db)
        if new_arch_db != view.arch_db:
            view.arch_db = new_arch_db


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["website.aboutus_page"])
    website_cookie_notice_post_migration(env)
    convert_html_string(env)
    # This call is commented out as this script causes conflicts with inheritance
    # in migrations to later versions. In v14 a duplicate of website.layout with
    # associated website is made when the company name is modified in the footer,
    # this script replicates that behaviour in the migration but in later versions
    # it can be a problem of inheritance. However, it can be uncommented and used if
    # deemed appropriate.
    # extract_footer_copyright_company_name(env)
