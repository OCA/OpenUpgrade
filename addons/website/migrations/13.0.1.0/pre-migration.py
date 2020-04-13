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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
