# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade

column_renames = {
    # Using magic None value to trigger call to get_legacy_name()
    'account_invoice':
    [
        ('address_contact_id', None),
        ('address_invoice_id', None),
    ],
    'account_invoice_line':
    [
        ('note', None),
    ],
    'account_cashbox_line':
    [
        ('ending_id', None),
        ('starting_id', None),
        ('number', None),
    ]
}

xmlid_renames = [
    ('account.account_payment_term_15days', 'account.account_payment_term'),
    ]


def fix_move_line_currency(cr):
    """
    In OpenERP 7.0, there is a new constraint on move lines
    having their currency set to the company currency.
    These would be happily created in OpenERP 6.1, specifically
    from bank statements.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_move_line l
        SET currency_id = NULL
        FROM res_company c
        WHERE l.company_id = c.id
              AND l.currency_id = c.currency_id;
        """)


def sanitize_account_invoice_lines(cr):
    """This method prevents that partner_id information on account invoice
    lines is desynchronized with account invoice, and avoid possible foreign
    key errors. This can be due to https://github.com/odoo/odoo/issues/6942 -
    Stored related fields without recompute triggers are never recomputed.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice_line ail
        SET partner_id=ai.partner_id
        FROM account_invoice ai
        WHERE ail.invoice_id=ai.id
        AND ail.partner_id != ai.partner_id;
        """)


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    fix_move_line_currency(cr)
    sanitize_account_invoice_lines(cr)
