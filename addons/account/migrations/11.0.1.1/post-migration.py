# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # map old / non existing value 'proforma' and 'proforma2' to value 'draft'
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('proforma', 'draft'), ('proforma2', 'draft')],
        table='account_invoice', write='sql')

    # copy statement_line_id values from account.move to account.move.line
    env.cr.execute("""
        UPDATE account_move_line aml
        SET statement_line_id = am.statement_line_id
        FROM account_move am
        WHERE aml.move_id = am.id AND am.statement_line_id IS NOT NULL;
    """)

    openupgrade.load_data(
        env.cr, 'account', 'migrations/11.0.1.1/noupdate_changes.xml',
    )
