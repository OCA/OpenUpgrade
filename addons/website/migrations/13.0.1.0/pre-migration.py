# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('website.redirect', 'website.rewrite'),
]

_table_renames = [
    ('website_redirect', 'website_rewrite'),
]

_field_renames = [
    ('website.rewrite', 'website_rewrite', 'type', 'redirect_type'),
]

_xmlid_renames = [
    ('website.access_website_redirect', 'website.access_website_rewrite'),
    ('website.access_website_redirect_designer', 'website.access_website_rewrite_designer'),
]


def fill_website_rewrite_name(cr):
    openupgrade.logged_query(
        cr, """
        ALTER TABLE website_rewrite
        ADD COLUMN name varchar""",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE website_rewrite
        SET name = CASE WHEN url_from IS NOT NULL OR url_to IS NOT NULL THEN
            url_from || ' -> ' || url_to
            ELSE 'default_name' END""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fill_website_rewrite_name(env.cr)
