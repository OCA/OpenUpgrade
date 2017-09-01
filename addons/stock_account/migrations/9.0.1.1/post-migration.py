# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        'update stock_inventory i set accounting_date=p.date_start '
        'from account_period p where p.id=i.period_id')
    openupgrade.load_data(
        cr, 'stock_account', 'migrations/9.0.1.1/noupdate_changes.xml',
    )
