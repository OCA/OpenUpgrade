# Copyright 2018-19 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs

from openupgradelib import openupgrade


def assign_theme(env):
    theme_category = env.ref('base.module_category_theme')
    theme_module = env['ir.module.module'].search(
        [('state', '=', 'installed'),
         ('category_id', '=', theme_category.id)],
        limit=1,
    )
    websites = env['website'].search([])
    if theme_module:
        websites.write({'theme_id': theme_module.id})


def enable_multiwebsites(env):
    websites = env["website"].search([])
    if len(websites) > 1:
        wizard = env["res.config.settings"].create({
            "group_multi_website": True,
        })
        wizard.execute()


def fill_website_socials(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE website w
        SET social_facebook = c.social_facebook,
            social_github = c.social_github,
            social_googleplus = c.social_googleplus,
            social_linkedin = c.social_linkedin,
            social_twitter = c.social_twitter,
            social_youtube = c.social_youtube
        FROM res_company c
        WHERE w.company_id = c.id
        """
    )


def sync_menu_views_pages_websites(env):
    # Main menu and children must be website-agnostic
    main_menu = env.ref('website.main_menu')
    child_menus = env["website.menu"].search([
        ("id", "child_of", main_menu.id),
        ("website_id", "!=", False),
    ])
    child_menus.write({"website_id": False})
    # Duplicate the main menu for main website
    website = env["website"].get_current_website()
    website.copy_menu_hierarchy(main_menu)
    # Find views that were website-specified in pre stage
    col_name = openupgrade.get_legacy_name("bs4_migrated_from")
    env.cr.execute(
        "SELECT %s, id FROM %s WHERE %s IS NOT NULL",
        (
            AsIs(col_name),
            AsIs(env["ir.ui.view"]._table),
            AsIs(col_name),
        )
    )
    for agnostic_view_id, specific_view_id in env.cr.fetchall():
        # Create website-specific page for the copied view
        agnostic_view = env["ir.ui.view"].browse(agnostic_view_id)
        specific_view = env["ir.ui.view"].browse(specific_view_id)
        agnostic_page = agnostic_view.first_page_id
        if not agnostic_page:
            continue
        specific_page = env["website.page"].search([
            ("url", "=", agnostic_page.url),
            ("website_id", "=", specific_view.website_id.id),
        ])
        if not specific_page:
            specific_page = agnostic_page.copy({
                "is_published": agnostic_page.is_published,
                "url": agnostic_page.url,
                "view_id": specific_view_id,
                "website_id": specific_view.website_id.id,
            })
        elif specific_page.view_id == agnostic_view:
            specific_page.view_id = specific_view_id
        # Create website-specific menu for the copied page
        specific_menu = env["website.menu"].search([
            ("website_id", "=", specific_page.website_id.id),
            ("url", "=", specific_page.url),
        ], limit=1)
        if specific_menu:
            if specific_menu.page_id:
                specific_menu.page_id = specific_page
        else:
            agnostic_menu = env["website.menu"].search([
                ("website_id", "=", False),
                ("url", "=", specific_page.url),
            ], limit=1)
            if agnostic_menu:
                agnostic_menu.copy({
                    "website_id": specific_page.website_id.id,
                    "page_id": agnostic_menu.page_id.id and specific_page.id,
                })


def website_views_add_children(env):
    """Add all expected children to website-specific views.

    The COW system would duplicate children views when duplicating the parent
    one, but that system wasn't loaded in the pre-migration stage, where many
    views were COW-ed manually to perform BS4 migration on them.

    Now that the COW system is loaded, it's time to ensure all views have
    all their children in place.
    """
    for website in env["website"].search([]):
        done_views = View = env["ir.ui.view"].with_context(
            # We need to duplicate inactive views to allow users enable them
            # from the "Customize" menu
            active_test=False,
            # This key enables the COW system in views
            website_id=website.id,
        )
        while True:
            # Find all views specific for this website
            todo_views = View.search([
                ("id", "not in", done_views.ids),
                ("key", "!=", False),
                ("website_id", "=", website.id),
            ])
            if not todo_views:
                break
            for parent_view in todo_views:
                # A child view could delete a parent view in the COW process,
                # so we need to ensure it exists before anything else
                if not parent_view.exists():
                    continue
                # Search website-agnostic child views by key instead of by ID
                child_views = View.search([
                    ("website_id", "=", False),
                    ("inherit_id.key", "=", parent_view.key),
                ])
                # Trigger the COW system in write(), which will make sure that
                # website-specific children views inherit from their
                # website-specific parent, creating the missing children
                # views if needed
                child_views.write({"inherit_id": parent_view.id})
            # Skip these views next loop
            done_views |= todo_views


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    assign_theme(env)
    fill_website_socials(cr)
    env['website.menu']._parent_store_compute()
    openupgrade.load_data(
        cr, 'website', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'website.action_website_homepage',
            'website.action_module_theme',
            'website.action_module_website',
        ],
    )
    enable_multiwebsites(env)
    sync_menu_views_pages_websites(env)
    website_views_add_children(env)
