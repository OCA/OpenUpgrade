# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.load_data(cr, 'hr_contract',
                          'migrations/9.0.1.0/noupdate_changes.xml')
    cr.execute("update hr_contract set state='open' where state='draft'")
