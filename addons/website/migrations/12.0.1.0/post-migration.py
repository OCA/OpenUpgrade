# Copyright 2018-19 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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


def apply_bootstrap_4(view):
    text = view.arch_db
    # TO BE FILLED
    view.arch_db = text


def bootstrap_4_migration(env):
    pages = env['website.page'].search([])
    views = pages.mapped('view_id').filtered(
        lambda v: v.type == 'qweb' and not v.xml_id)
    for view in views:
        apply_bootstrap_4(view)


def apply_copy_views(env):
    env.cr.execute(
        """
        SELECT website_page_id, website_id
        FROM website_website_page_rel
        """
    )
    pages = {}
    for page_id, website_id in env.cr.fetchall():
        if page_id not in pages:
            pages[page_id] = []
        pages[page_id].append(website_id)
    for page in env['website.page'].browse(list(pages)):
        for website in env['website'].browse(list(pages[page.id])):
            page.copy({'website_id': website.id})


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    assign_theme(env)
    fill_website_socials(cr)
    env['website.menu']._parent_store_compute()
    bootstrap_4_migration(env)
    apply_copy_views(env)
    openupgrade.load_data(
        cr, 'website', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'website.action_website_homepage',
            'website.action_module_theme',
            'website.action_module_website',
        ],
    )
