# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def website_menu_url(env):
    """
    Ensure website.menu#url is set
    """
    env.cr.execute(
        """
        UPDATE website_menu
        SET url=COALESCE(website_page.url, '#')
        FROM
        website_menu website_menu2
        LEFT JOIN website_page
        ON website_menu2.page_id=website_page.id
        WHERE website_menu.id=website_menu2.id
        """
    )


def qweb_templates_remove_inherit_id(env):
    """
    Central snippet related qweb templates were provided by web_editor v18, and website
    inherited from them. Now with web_editor being merged into html_editor, we need
    to disentangle those templates from their parents, as in v19, website is where
    snippets are introduced, and they would be deleted if inheritance wasn't removed
    during cleanup of xmlids
    """
    xmlids = [
        "website.snippets",
        "website.snippet_options",
    ]
    sum(map(env.ref, xmlids), env["ir.ui.view"]).write({"inherit_id": False})


@openupgrade.migrate()
def migrate(env, version):
    website_menu_url(env)
    qweb_templates_remove_inherit_id(env)
    openupgrade.cow_templates_mark_if_equal_to_upstream(env.cr)
