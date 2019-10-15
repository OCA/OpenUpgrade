# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

from base64 import b64encode
from itertools import chain, product
from os import listdir
from pathlib import Path

from psycopg2.extensions import AsIs

from openupgradelib import openupgrade
from openupgradelib.openupgrade_120 import convert_string_bootstrap_3to4

_field_renames = [
    ('website.page', 'website_page', 'website_published', 'is_published'),
]
_xml_ids_renames = [
    ('website.menu_homepage', 'website.menu_home'),
]


def _apply_v11_dummy_image_replacement(replacements, original_html):
    """Perform image URL replacements."""
    new_html = original_html
    for xmlid, dbid in replacements.items():
        old_url = "/web/image/%s" % xmlid
        new_url = "/web/image/%d" % dbid
        new_html = new_html.replace(old_url, new_url)
    return new_html


def _preserve_v11_dummy_images(env):
    """Preserve dummy images, which could still be used in some websites."""
    replacements = {}
    images_dir = Path(__file__).parent / "changed_dummy_images"
    for image_path in map(images_dir.joinpath, listdir(str(images_dir))):
        xmlid = image_path.stem
        try:
            old = env.ref(xmlid)
        except ValueError:
            continue  # Attachment was deleted; nothing to do
        with image_path.open("rb") as image_stream:
            new = old.copy({
                "url": False,
                "datas": b64encode(image_stream.read()),
            })
            replacements[xmlid] = new.id
    return replacements


def bootstrap_4_migration(env):
    """Convert customized website views to Bootstrap 4 and multiwebsite.

    This process is a bit complex, so here's the big picture:

    In v11, there's no upstream support for multi-websites, but databases
    can actually have several websites and some records (pages, menus, views)
    get multi-website features behind the scenes, so we have to treat them
    like semi-supported. Usually it follows this logic:

    - Website-specific records only appear in their website.
    - Website-agnostic records appear in all websites.
    - View changes affect all websites.

    In v12, there's full multi-website support, usually following this logic:

    - Website-specific records override website-agnostic ones.
    - View changes create a website-specific copy (Copy-On-Write, COW) always.

    This migration tries to make v11 changes look like they were done in v12:

    - Unmodified views (noupdate=0) are not touched.
    - Website-agnostic modified (noupdate=1) views are copied and
      marked as noupdate=0. Those copied views are made website-specific
      and migrated to Bootstrap 4.

    This must be done in the "pre" stage, because the "mid" stage could
    update or even delete missing views now that they are marked as
    noupdate=0, but that's exactly what you want because when you create a
    new website with the UI in v12, that website will be "virgin",
    including only the raw views that come directly from the modules,
    without any modifications made for other websites.
    """
    # Preserve old dummy images that have changed
    image_replacements = _preserve_v11_dummy_images(env)
    # Create a column to remember where do new views come from
    oldview_id_col = openupgrade.get_legacy_name("bs4_migrated_from")
    table_name = env["ir.ui.view"]._table
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE %s ADD COLUMN %s INTEGER",
        (AsIs(table_name), AsIs(oldview_id_col)),
    )
    # Create another column to store migration metadata
    old_metadata_col = openupgrade.get_legacy_name("bs4_migration_metadata")
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE %s ADD COLUMN %s TEXT",
        (AsIs(table_name), AsIs(old_metadata_col)),
    )
    # Find report views, which should never be converted here
    report_names = env["ir.actions.report"].search([
        ("report_name", "!=", False),
        ("report_type", "=like", "qweb-%"),
    ]).mapped("report_name")
    # Find updatable views, to be excluded; standard addon update is enough
    udpatable_ids = env["ir.model.data"].search([
        ("model", "=", "ir.ui.view"),
        ("noupdate", "=", False),
    ]).mapped("res_id")
    # In Odoo v11, a page can be related to multiple websites, and the related
    # view doesn't need to be related to a website (although it could be);
    # in v12, a page is related to a view, which is related (or not) to a sigle
    # website. Usually it would be impossible to link a page to multiple
    # websites using UI in v11, so it's not supported
    env.cr.execute(
        """SELECT r.website_id, p.view_id
           FROM website_website_page_rel AS r
           INNER JOIN website_page AS p ON r.website_page_id = p.id
           INNER JOIN ir_ui_view AS v ON p.view_id = v.id
           WHERE v.website_id IS NULL
           ORDER BY r.website_id DESC""",
    )
    for page_website_id, view_id in env.cr.fetchall():
        # If a page happens to be in different websites, only the first one
        # will be stored in the view; the others will be lost, which isn't a
        # problem since v11 didn't support multi-websites
        openupgrade.logged_query(
            env.cr,
            "UPDATE ir_ui_view SET website_id = %s WHERE id = %s",
            (page_website_id, view_id),
        )
    # Find views to convert
    all_views = env['ir.ui.view'].with_context(active_test=False).search([
        ("id", "not in", udpatable_ids),
        ("key", "not in", report_names),
        ("type", "=", "qweb"),
    ])
    # Find available websites
    env.cr.execute("SELECT id FROM website")
    website_ids = list(chain.from_iterable(env.cr.fetchall()))
    # Convert in place views that already have a website
    env.cr.execute(
        "SELECT id FROM %s WHERE id IN %s AND website_id IS NOT NULL",
        (AsIs(table_name), tuple(all_views.ids)),
    )
    views_with_website = env["ir.ui.view"].browse(
        list(chain.from_iterable(env.cr.fetchall())),
        prefetch=all_views._prefetch,
    )
    for view in views_with_website:
        new_arch = convert_string_bootstrap_3to4(view.arch_db)
        new_arch = _apply_v11_dummy_image_replacement(
            image_replacements,
            new_arch,
        )
        view.arch_db = new_arch
    # Convert a website-specific copy of the view for the rest
    views_without_website = all_views - views_with_website
    for website_id, oldview in product(website_ids, views_without_website):
        # Skip if the view is a page and already has a website-specific copy
        env.cr.execute(
            """SELECT v.id
               FROM ir_ui_view AS v
               INNER JOIN website_page AS p
               ON p.view_id = v.id
               WHERE v.website_id = %s AND p.url IN (
                    SELECT url
                    FROM website_page
                    WHERE view_id = %s
               )""",
            (website_id, oldview.id),
        )
        if env.cr.fetchall():
            continue
        # Skip if a website-specific copy already exists
        env.cr.execute(
            "SELECT id FROM %s WHERE key = %s AND website_id = %s",
            (AsIs(table_name), oldview.key, website_id),
        )
        if env.cr.fetchall():
            continue
        # Create the copy and convert it, otherwise
        new_arch = convert_string_bootstrap_3to4(oldview.arch_db)
        new_arch = _apply_v11_dummy_image_replacement(
            image_replacements,
            new_arch,
        )
        newview = oldview.copy({
            "arch_db": new_arch,
            "key": oldview.key,  # Avoid automatic deduplication
        })
        # Website-specific copy of the related website.page record
        openupgrade.logged_query(
            env.cr,
            """INSERT INTO website_page (
                    create_date, create_uid, write_date, write_uid,
                    date_publish, is_published, url, website_indexed, view_id)
               SELECT
                    create_date, create_uid, write_date, write_uid,
                    date_publish, is_published, url, website_indexed, %(new)s
               FROM website_page
               WHERE view_id = %(old)s""",
            {"new": newview.id, "old": oldview.id},
        )
        # Obtain related website.menu details
        env.cr.execute(
            """SELECT
                    wm.create_date, wm.create_uid, wm.write_date, wm.write_uid,
                    wm.name, wm.url, wm.new_window, wm.sequence, wm.parent_id
               FROM website_menu AS wm
               INNER JOIN website_page AS wp ON wm.page_id = wp.id
               INNER JOIN ir_ui_view AS v ON wp.view_id = v.id
               WHERE view_id = %s AND wm.website_id IS NULL""",
            (oldview.id,)
        )
        menus = []
        # Use only JSON-serializable types
        for menu in env.cr.dictfetchall():
            for key in menu:
                if not isinstance(menu[key], (str, int, float,
                                              bool, type(None))):
                    menu[key] = str(menu[key])
            menus.append(menu)
        # Store needed info in the migration columns
        openupgrade.logged_query(
            env.cr,
            "UPDATE %s SET %s = %s, %s = %s, website_id = %s WHERE id = %s",
            (
                AsIs(table_name),
                AsIs(oldview_id_col),
                oldview.id,
                AsIs(old_metadata_col),
                json.dumps({
                    "menus": menus,
                }),
                website_id,
                newview.id,
            )
        )
    # Inherit translated SEO metadata from original views
    openupgrade.copy_fields_multilang(
        env.cr, "ir.ui.view", env["ir.ui.view"]._table,
        ["website_meta_title",
         "website_meta_description",
         "website_meta_keywords"],
        oldview_id_col,
    )
    # Inherit arch translations from parent views
    openupgrade.copy_fields_multilang(
        env.cr, "ir.ui.view", env["ir.ui.view"]._table,
        ["arch_db"],
        oldview_id_col,
        translations_only=True,
    )
    # Set website-agnostic views as updatable
    model_data = env["ir.model.data"].search([
        ("model", "=", "ir.ui.view"),
        ("res_id", "in", views_without_website.ids),
    ])
    model_data.write({"noupdate": False})


def disable_less_customizations(env):
    """Less customizations will fail in 99% of the times. Disable them.

    Odoo v12 uses now Scss and Bootstrap 4. You need to transform your
    sources to the new lang and framework to make them work. This cannot be
    automated.
    """
    # Find views applying Less customizations
    pattern = "/%/static/%.custom.%assets%.less"
    custom_less_views = env["ir.ui.view"].search([
        ("name", "=like", pattern),
        ("arch_db", "like", '<attribute name="href">%s</attribute>' % pattern),
        ("active", "=", True),
    ])
    # Disable them
    custom_less_views.write({"active": False})


def fill_website_company_id(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website w
        SET company_id = c.id
        FROM (SELECT id FROM res_company ORDER BY id ASC LIMIT 1) AS c
        WHERE w.company_id IS NULL
        """
    )


def fill_website_name(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website w
        SET name = 'Home #' || w.id
        WHERE w.name IS NULL
        """
    )


def fill_website_redirect_type(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website_redirect wr
        SET type = '301'
        WHERE wr.type IS NULL
        """
    )


def fill_website_redirect_urls(cr):
    # done in pre-migration to avoid warning messages
    openupgrade.logged_query(
        cr, """
        UPDATE website_redirect wr
        SET active = FALSE
        WHERE wr.url_from IS NULL OR wr.url_to IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(cr, _xml_ids_renames)
    fill_website_company_id(cr)
    fill_website_name(cr)
    fill_website_redirect_type(cr)
    fill_website_redirect_urls(cr)
    disable_less_customizations(env)
    bootstrap_4_migration(env)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'website', ['aboutus', 'contactus', 'homepage'], False)
