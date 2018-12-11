# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr, env['payment.transaction'], 'payment_transaction',
        'invoice_ids', 'account_invoice_id',
    )
