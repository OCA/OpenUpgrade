# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'purchase', 'migrations/10.0.1.2/noupdate_changes.xml',
    )
    # v10 added correcly handling the invoice state of products invoiced
    # by delivered quantity
    records = env['purchase.order'].search([
        ('order_line.product_id.invoice_policy', '=', 'delivery'),
        ('invoice_status', '=', 'to invoice'),
    ])
    records._recompute_todo(env['purchase.order']._fields['invoice_status'])
    records.recompute()
