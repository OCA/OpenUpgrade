# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('website_crm.salesteam_website_sales',
     'sales_team.salesteam_website_sales'),
]


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.is_module_installed(env.cr, 'website_crm'):
        openupgrade.rename_xmlids(env.cr, _xmlid_renames)
