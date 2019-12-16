# -*- coding: utf-8 -*-
# Copyright 2016 Therp BV <http://therp.nl>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


column_copies = {
    'account_voucher': [
        ('type', None, None),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('account.voucher', 'account_voucher', 'type', 'voucher_type'),
    ('account.voucher.line', 'account_voucher_line', 'amount', 'price_unit'),
]


def delete_payment_views(cr):
    """Delete account.voucher payment views that hinder upgrade."""
    cr.execute(
        """\
        DELETE FROM ir_ui_view
        WHERE name like '%account.voucher.payment%'
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    cr.execute('update account_voucher_line set amount=0 where amount is null')
    cr.execute("update account_voucher_line set name='/' where name is null")
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_fields(env, field_renames)
    delete_payment_views(cr)
    openupgrade.add_fields(
        env, [
            ('price_subtotal', 'account.voucher.line', 'account_voucher_line',
             'monetary', False, 'account_voucher'),
        ],
    )
