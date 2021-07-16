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
