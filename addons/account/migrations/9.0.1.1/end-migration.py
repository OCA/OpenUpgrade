# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_journal_payment_methods(env):
    """Update default payment methods in journals when type is 'bank' or
    'cash'.
    """
    payment_methods = env['account.payment.method'].search([])
    journals = env['account.journal'].search([
        '|', ('type', '=', 'bank'), ('type', '=', 'cash'),
    ])
    in_methods = payment_methods.filtered(
        lambda x: x.payment_type == 'inbound')
    out_methods = payment_methods - in_methods
    journals.write({
        'inbound_payment_method_ids': [(6, 0, in_methods.ids)],
        'outbound_payment_method_ids': [(6, 0, out_methods.ids)],
    })


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_journal_payment_methods(env)
