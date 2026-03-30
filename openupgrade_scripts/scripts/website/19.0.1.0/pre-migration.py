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


@openupgrade.migrate()
def migrate(env, version):
    website_menu_url(env)
