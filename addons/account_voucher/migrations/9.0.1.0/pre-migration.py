# -*- coding: utf-8 -*-
# Copyright 2016 Therp BV <http://therp.nl>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp.addons.account_voucher.account_voucher import \
    account_voucher_line

account_voucher_line._openupgrade_recompute_fields_blacklist = []


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
    cr.execute('SELECT count(*) FROM account_voucher WHERE tax_id IS NOT NULL')
    taxed_vouchers = cr.fetchone()[0]
    if not taxed_vouchers:
        # If you have a DB where all account vouchers have no tax applied (we
        # do), the new field price_subtotal can be computed from price_unit
        # (amount) and quantity (1).
        #
        # See the post migration script to have the full idea.
        account_voucher_line._openupgrade_recompute_fields_blacklist.append(
            'price_subtotal'
        )
