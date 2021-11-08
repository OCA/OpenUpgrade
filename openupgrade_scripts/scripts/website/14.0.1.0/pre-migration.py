# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def assure_website_visitor_partner_is_set(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website_visitor wv
        SET partner_id = rel.partner_id
        FROM website_visitor_partner_rel rel
        WHERE wv.partner_id IS NULL AND wv.id = rel.visitor_id""",
    )


def website_cookie_notice_pre_migration(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH keys AS (
            SELECT key
            FROM ir_ui_view iuv
            JOIN ir_model_data imd ON (
                imd.model = 'ir.ui.view' AND imd.res_id = iuv.id AND module = 'website')
            WHERE imd.name IN ('legal_cookie_policy', 'cookie_banner')
        )
        DELETE FROM ir_ui_view iuv
        USING keys
        WHERE iuv.key = keys.key AND iuv.website_id IS NOT NULL""",
    )
    # rename xmlids
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("website.legal_cookie_policy", "website.cookie_policy"),
            ("website.cookie_banner", "website.cookies_bar"),
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    assure_website_visitor_partner_is_set(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website",
        [
            "website_designer_edit_qweb",
            "website_designer_view",
            "website_group_system_edit_all_views",
            "website_menu",
            "website_page_rule_public",
        ],
        True,
    )
    website_cookie_notice_pre_migration(env)
