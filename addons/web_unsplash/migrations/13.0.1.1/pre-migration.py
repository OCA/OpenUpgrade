# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

xmlid_renames = [
    ('web_unsplash.assets_common', 'web_unsplash.assets_frontend'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
