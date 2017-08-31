# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # map old / non existing value 'cost' to default value 'order'
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('invoice_policy'), 'invoice_policy',
        [('cost', 'order')],
        table='product_template', write='sql')
    openupgrade.load_data(
        cr, 'sale', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
