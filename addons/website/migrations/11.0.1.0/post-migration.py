# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark <http://bloopark.de>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_website_pages(env):
    """Fill remaining website.page records (not populated by data) with data
    from view records with the old page flag set.
    """
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO website_page
            (url, view_id, website_indexed, website_published, create_uid,
             create_date, write_uid, write_date)
        SELECT COALESCE(wm.url, '/page/' || iuv.name), iuv.id, TRUE, TRUE,
            iuv.create_uid,
            iuv.create_date, iuv.write_uid, iuv.write_date
        FROM
            website_page wp
        RIGHT JOIN
            ir_ui_view iuv ON wp.view_id = iuv.id
        LEFT JOIN
            website_menu wm ON wm.url = '/page/' || iuv.name
            AND (wm.website_id = iuv.website_id
            OR wm.website_id IS NULL
            OR iuv.website_id IS NULL)
        WHERE
            wp.id IS NULL
            AND iuv.page = TRUE""",
    )


def link_websites_with_pages(env):
    """Fill many2many relation for field website_ids of website.page."""
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO website_website_page_rel
            (website_page_id, website_id)
        SELECT
            wp.id, iuv.website_id
        FROM
            ir_ui_view iuv,
            website_page wp
        WHERE
            wp.view_id = iuv.id AND
            iuv.website_id IS NOT NULL""",
    )


def add_website_homepages(env):
    # Add homepage for websites
    openupgrade.logged_query(
        env.cr, """
        UPDATE
            website AS w
        SET
            homepage_id = wp.id
        FROM ir_ui_view iuv,
             website_page wp
        WHERE
            iuv.website_id = w.id AND
            iuv.key = 'website.homepage' AND
            iuv.id = wp.view_id""",
    )


def delete_noupdate_records(env):
    """Clean data for website.menu_website deleted from noupdate data."""
    env.ref('website.menu_website').unlink()


def import_website_seo_redirection_data(env):
    """Check if module was installed looking to the expected table, and then
    import data in the new website feature table.
    """
    if not openupgrade.table_exists(env.cr, 'website_seo_redirection'):
        return
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO website_redirect
        (type, url_from, url_to, active, sequence)
        SELECT '301', wsr.origin, wsr.destination, True, 10
        FROM website_seo_redirection wsr""",
    )


def update_social_media(env):
    """Data are now located at company level."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE res_company rc
        SET social_twitter = w.%s,
            social_facebook = w.%s,
            social_github = w.%s,
            social_linkedin = w.%s,
            social_youtube = w.%s,
            social_googleplus = w.%s
        FROM website w
        WHERE w.company_id = rc.id""", (
            AsIs(openupgrade.get_legacy_name('social_twitter')),
            AsIs(openupgrade.get_legacy_name('social_facebook')),
            AsIs(openupgrade.get_legacy_name('social_github')),
            AsIs(openupgrade.get_legacy_name('social_linkedin')),
            AsIs(openupgrade.get_legacy_name('social_youtube')),
            AsIs(openupgrade.get_legacy_name('social_googleplus')),
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_website_pages(env)
    link_websites_with_pages(env)
    add_website_homepages(env)
    delete_noupdate_records(env)
    update_social_media(env)
    import_website_seo_redirection_data(env)
    openupgrade.load_data(
        env.cr, 'website', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
