# Copyright 2021 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('website_livechat.user_navbar_inherit_website_livecaht',
     'website_livechat.user_navbar_inherit_website_livechat'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
