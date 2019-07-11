# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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


def noupdate_changes(env):
    """Set some specific noupdate=1 records to noupdate=0"""
    noupdates = env["ir.model.data"].search([
        ("module", "=", "website"),
        ("name", "in", ["aboutus", "contactus", "homepage"]),
        ("noupdate", "=", True),
    ])
    noupdates.write({"noupdate": False})


def bootstrap_4_migration(env):
    """Convert customized website views to Bootstrap 4."""
    # Preserve old dummy images that have changed
    image_replacements = _preserve_v11_dummy_images(env)
    # Create a column to remember where do new views come from
    col_name = openupgrade.get_legacy_name("bs4_migrated_from")
    table_name = env["ir.ui.view"]._table
    if not openupgrade.column_exists(env.cr, table_name, col_name):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE %s ADD COLUMN %s INTEGER",
            (AsIs(table_name), AsIs(col_name)),
        )
    # Find report views, which should never be converted here
    report_names = env["ir.actions.report"].search([
        ("report_name", "!=", False),
        ("report_type", "=like", "qweb-%"),
    ]).mapped("report_name")
    # Find updatable views, to be excluded; standard addon update is enough
    updatable_ids = env["ir.model.data"].search([
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
        ("id", "not in", updatable_ids),
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
        openupgrade.logged_query(
            env.cr,
            "UPDATE %s SET %s = %s, website_id = %s WHERE id = %s",
            (
                AsIs(table_name),
                AsIs(col_name),
                oldview.id,
                website_id,
                newview.id,
            )
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
    noupdate_changes(env)
