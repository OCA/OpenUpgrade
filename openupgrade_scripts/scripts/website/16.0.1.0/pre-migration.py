from itertools import chain

from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5

_xmlids_renames = [
    (
        "website.group_website_publisher",
        "website.group_website_restricted_editor",
    ),
    (
        "website_sale.menu_reporting",
        "website.menu_reporting",
    ),
]

# delete xml xpath for odoo add it again
_xmlids_delete = [
    "website.website_configurator",
    "website.website_menu",
]


def delete_constraint_website_visitor_partner_uniq(env):
    openupgrade.delete_sql_constraint_safely(
        env,
        "website",
        "website_visitor",
        "partner_uniq",
    )


def _fill_partner_id_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website_visitor v
           SET partner_id = p.id
          FROM res_partner p
         WHERE v.partner_id IS NULL
           AND length(v.access_token) != 32
           AND p.id = CAST(v.access_token AS integer);
        """,
    )


def _fill_language_ids_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO website_lang_rel (website_id, lang_id)
        SELECT w.id, w.default_lang_id
          FROM website w
         WHERE NOT EXISTS (
            SELECT 1
              FROM website_lang_rel wlr
             WHERE wlr.website_id = w.id
         );
         """,
    )


def _fill_homepage_url(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE website
            ADD COLUMN IF NOT EXISTS homepage_url CHARACTER VARYING
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website
           SET homepage_url = website_page.url
        FROM website_page
        WHERE website_page.id = website.homepage_id
        """,
    )


def boostrap_5_migration(env):
    """Convert customized website views to Bootstrap 5."""
    # Find views to convert
    env.cr.execute(
        """
        SELECT iuv.id FROM ir_ui_view iuv JOIN website w on w.id = iuv.website_id
        WHERE iuv.type = 'qweb' AND iuv.website_id IS NOT NULL
    """
    )
    view_ids = list(chain.from_iterable(env.cr.fetchall()))
    all_view_need_bs5_migration = env["ir.ui.view"].browse(view_ids)
    for view in all_view_need_bs5_migration:
        new_arch = convert_string_bootstrap_4to5(view.arch_db)
        view.arch_db = new_arch


@openupgrade.migrate()
def migrate(env, version):
    _fill_partner_id_if_null(env)
    _fill_language_ids_if_null(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_delete)
    delete_constraint_website_visitor_partner_uniq(env)
    boostrap_5_migration(env)
    _fill_homepage_url(env)
