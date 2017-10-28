# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
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


def delete_payment_views(cr):
    """Delete account.voucher payment views that hinder upgrade."""
    cr.execute(
        """\
        DELETE FROM ir_ui_view
        WHERE name like '%account.voucher.payment%'
        """
    )

def amount_account_voucher(cr):
    '''
    Metodo para respaldar campo amount de la tabla account_voucher
    '''
    column_copies_av = {
                    'account_voucher': [
                        ('amount', None, None),
                    ],
                    }
    openupgrade.copy_columns(cr, column_copies_av)

def amount_account_voucher_line(cr):
    '''
    Metodo para respaldar campo amount de la tabla account_voucher_line,
    debido a quee en version 9 el campo se transforma en funcion
    '''
    column_copies_avl = {
                    'account_voucher_line': [
                        ('amount', None, None),
                    ],
                    }
    openupgrade.copy_columns(cr, column_copies_avl)
     
@openupgrade.migrate()
def migrate(cr, version):
    cr.execute('update account_voucher_line set amount=0 where amount is null')
    cr.execute("update account_voucher_line set name='/' where name is null")
    openupgrade.copy_columns(cr, column_copies)
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
    
    #Metodos para respaldar campos
    amount_account_voucher(cr)
    amount_account_voucher_line(cr)
    