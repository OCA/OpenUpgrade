# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'account_voucher': [
        ('type', None, None),
    ],
}


def delete_payment_views(cr):
    """Delete account.voucher payment views that hinder upgrade."""
    cr.execute(
        """\
        DELETE FROM ir_ui_view
        WHERE inherit_id in (
        SELECT id FROM ir_ui_view WHERE name like '%account.voucher.payment%')
        """
    )
    cr.execute(
        """\
        DELETE FROM ir_ui_view
        WHERE name like '%account.voucher.payment%'
        """
    )


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute('update account_voucher_line set amount=0 where amount is null')
    cr.execute("update account_voucher_line set name='/' where name is null")
    openupgrade.copy_columns(cr, column_copies)
    delete_payment_views(cr)
