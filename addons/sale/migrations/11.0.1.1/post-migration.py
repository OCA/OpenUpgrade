# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('sale.group_display_incoterm', 'sale_stock.group_display_incoterm'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.load_data(
        env.cr, 'sale', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
