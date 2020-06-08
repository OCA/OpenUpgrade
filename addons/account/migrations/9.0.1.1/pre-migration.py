# -*- coding: utf-8 -*-
# © 2016 Sylvain LE GAL <https://twitter.com/legalsylvain>
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from psycopg2.extensions import AsIs

from openupgradelib import openupgrade

logger = logging.getLogger('OpenUpgrade')

column_renames = {
    'account_account_type': [
        ('close_method', None),
    ],
    'account_bank_statement_line': [
        ('journal_entry_id', None),
    ],
    'account_account': [
        ('type', None),
    ],
    'account_cashbox_line': [
        ('pieces', 'coin_value'),
        ('number_opening', None),
        ('number_closing', None),
        ('bank_statement_id', None),
    ]
}

field_renames = [
    ('account.bank.statement', 'account_bank_statement', 'closing_date',
     'date_done'),
    # renamings with oldname attribute - They also need the rest of operations
    ('account.account', 'account_account', 'user_type', 'user_type_id'),
    ('account.account.template', 'account_account_template', 'user_type',
     'user_type_id'),
    ('account.chart.template', 'account_chart_template',
     'property_account_expense', 'property_account_expense_id'),
    ('account.chart.template', 'account_chart_template',
     'property_account_expense_categ', 'property_account_expense_categ_id'),
    ('account.chart.template', 'account_chart_template',
     'property_account_income', 'property_account_income_id'),
    ('account.chart.template', 'account_chart_template',
     'property_account_income_categ', 'property_account_income_categ_id'),
    ('account.chart.template', 'account_chart_template',
     'property_account_payable', 'property_account_payable_id'),
    ('account.chart.template', 'account_chart_template',
     'property_account_receivable', 'property_account_receivable_id'),
    ('account.invoice', 'account_invoice', 'fiscal_position',
     'fiscal_position_id'),
    ('account.invoice', 'account_invoice', 'invoice_line', 'invoice_line_ids'),
    ('account.invoice', 'account_invoice', 'payment_term', 'payment_term_id'),
    ('account.invoice', 'account_invoice', 'tax_line', 'tax_line_ids'),
    ('account.invoice.line', 'account_invoice_line', 'invoice_line_tax_id',
     'invoice_line_tax_ids'),
    ('account.invoice.line', 'account_invoice_line', 'uos_id', 'uom_id'),
    ('account.journal', 'account_journal', 'currency', 'currency_id'),
    ('account.move.line', 'account_move_line', 'analytic_lines',
     'analytic_line_ids'),
    ('account.move.line', 'account_move_line', 'invoice', 'invoice_id'),
    ('account.tax', 'account_tax', 'account_collected_id', 'account_id'),
    ('account.tax', 'account_tax', 'account_paid_id', 'refund_account_id'),
    ('account.tax', 'account_tax', 'type', 'amount_type'),
    ('account.tax.template', 'account_tax_template', 'account_collected_id',
     'account_id'),
    ('account.tax.template', 'account_tax_template', 'account_paid_id',
     'refund_account_id'),
    ('product.category', 'product_category', 'property_account_expense_categ',
     'property_account_expense_categ_id'),
    ('product.category', 'product_category', 'property_account_income_categ',
     'property_account_income_categ_id'),
    ('product.template', 'product_template', 'property_account_expense',
     'property_account_expense_id'),
    ('product.template', 'product_template', 'property_account_income',
     'property_account_income_id'),
    ('res.partner', 'res_partner', 'last_reconciliation_date',
     'last_time_entries_checked'),
    ('res.partner', 'res_partner', 'property_account_payable',
     'property_account_payable_id'),
    ('res.partner', 'res_partner', 'property_account_position',
     'property_account_position_id'),
    ('res.partner', 'res_partner', 'property_account_receivable',
     'property_account_receivable_id'),
    ('res.partner', 'res_partner', 'property_payment_term',
     'property_payment_term_id'),
    ('res.partner', 'res_partner', 'property_supplier_payment_term',
     'property_supplier_payment_term_id'),
    ('res.partner', 'res_partner', 'ref_companies', 'ref_company_ids'),
]

column_copies = {
    'account_bank_statement': [
        ('state', None, None),
    ],
    'account_journal': [
        ('type', None, None),
    ],
    'account_tax': [
        ('type_tax_use', None, None),
        ('type', None, None),
        ('tax_code_id', 'tax_group_id', None),
    ],
    'account_tax_template': [
        ('type_tax_use', None, None),
        ('type', None, None),
    ],
    'account_invoice': [
        ('reference', None, None),
    ]
}

table_renames = [
    ('account_statement_operation_template', 'account_operation_template'),
    ('account_tax_code', 'account_tax_group')]

xmlid_renames = [
    ('account.conf_account_type_equity', 'account.data_account_type_equity'),
    ('account.data_account_type_income', 'account.data_account_type_revenue'),
    ('account.data_account_type_bank', 'account.data_account_type_liquidity'),
    ('account.data_account_type_asset',
     'account.data_account_type_current_assets'),
    ('account.data_account_type_liability',
     'account.data_account_type_current_liabilities'),
    ('account.data_account_type_expense',
     'account.data_account_type_expenses'),
]

PROPERTY_FIELDS = {
    ('product.category', 'property_account_expense_categ',
     'property_account_expense_categ_id'),
    ('product.category', 'property_account_income_categ',
     'property_account_income_categ_id'),
    ('product.template', 'property_account_income',
     'property_account_income_id'),
    ('product.template', 'property_account_expense',
     'property_account_expense_id'),
    ('res.partner', 'property_account_payable', 'property_account_payable_id'),
    ('res.partner', 'property_account_receivable',
     'property_account_receivable_id'),
    ('res.partner', 'property_account_position',
     'property_account_position_id'),
    ('res.partner', 'property_payment_term', 'property_payment_term_id'),
    ('res.partner', 'property_supplier_payment_term',
     'property_supplier_payment_term_id'),
}


FAST_CREATIONS = [
    ('account_invoice_tax', 'currency_id', 'integer', """
    UPDATE account_invoice_tax ait SET currency_id = ai.currency_id
    FROM account_invoice ai where ai.id = ait.invoice_id;
    """),
    ('account_bank_statement', 'difference', 'numeric', """
    UPDATE account_bank_statement abs
    SET difference = balance_end_real - balance_end;
    """),
    ('account_invoice', 'amount_total_signed', 'numeric', """
    UPDATE account_invoice
    SET amount_total_signed = amount_total
    WHERE type IN ('in_invoice', 'out_invoice');
    UPDATE account_invoice
    SET amount_total_signed = - amount_total
    WHERE type IN ('in_refund', 'out_refund');
    """),
    # For multicurrency invoices, these values will be overwritten
    # in the post script
    ('account_invoice', 'amount_total_company_signed', 'numeric', """
    UPDATE account_invoice
    SET amount_total_company_signed = amount_total_signed;
    """),
    ('account_invoice', 'amount_untaxed_signed', 'numeric', """
    UPDATE account_invoice
    SET amount_untaxed_signed = amount_untaxed
    WHERE type IN ('in_invoice', 'out_invoice');
    UPDATE account_invoice
    SET amount_untaxed_signed = - amount_untaxed
    WHERE type IN ('in_refund', 'out_refund');
    """)
]


def migrate_properties(cr):
    for model, name_v8, name_v9 in PROPERTY_FIELDS:
        openupgrade.logged_query(cr, """
            update ir_model_fields
            set name = '{name_v9}'
            where name = '{name_v8}'
            and model = '{model}'
            """.format(model=model, name_v8=name_v8, name_v9=name_v9))
        openupgrade.logged_query(cr, """
            update ir_property
            set name = '{name_v9}'
            where name = '{name_v8}'
            """.format(name_v8=name_v8, name_v9=name_v9))


def remove_account_moves_from_special_periods(cr):
    """We first search for journal entries in a special period, in the
    first reported fiscal year of the company, and we take them out of the
    special period, into a normal period, because we assume that this is
    the starting balance of the company, and should be maintained.
    Then we delete all the moves associated to special periods."""
    cr.execute("""
        SELECT id FROM account_move
        WHERE period_id in (SELECT id FROM account_period WHERE special = True
        AND fiscalyear_id = (SELECT id FROM account_fiscalyear
        ORDER BY date_start ASC LIMIT 1) ORDER BY date_start ASC LIMIT 1)
    """)
    move_ids = [i for i, in cr.fetchall()]

    cr.execute("""
        SELECT id FROM account_period WHERE special = False
        AND fiscalyear_id = (SELECT id FROM account_fiscalyear
        ORDER BY date_start ASC LIMIT 1) ORDER BY date_start ASC LIMIT 1
    """)
    first_nsp_id = cr.fetchone()
    first_nsp_id = first_nsp_id and first_nsp_id[0]

    if first_nsp_id and move_ids:
        openupgrade.logged_query(cr, """
            UPDATE account_move
            SET period_id = %s
            where id in %s
            """, (first_nsp_id, tuple(move_ids)))

    openupgrade.logged_query(cr, """
        DELETE FROM account_move_line l
        USING account_period p, account_journal j
        WHERE l.period_id=p.id AND l.journal_id=j.id
        AND p.special AND j.centralisation
    """)

    openupgrade.logged_query(cr, """
        DELETE FROM account_move m
        USING account_period p, account_journal j
        WHERE m.period_id=p.id AND m.journal_id=j.id
        AND p.special AND j.centralisation
    """)


def install_account_tax_python(cr):
    """ Type tax type 'code' is in v9 introduced by module
    'account_tax_python. So, if we find an existing tax using this type,
    we know that we have to install the module."""
    openupgrade.logged_query(
        cr, "update ir_module_module set state='to install' "
        "where name='account_tax_python' "
        "and state in ('uninstalled', 'to remove') "
        "and exists (select id FROM account_tax where type = 'code')")


def map_account_tax_type(cr):
    """ The tax type 'code' is not an option in the account module for v9.
    We need to assign a temporary 'dummy' value until module
    account_tax_python is installed. In post-migration we will
    restore the original value.

    Also, the value `none` is not accepted anymore. We switch to `percent` +
    value = 0.
    """
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('code', 'group')],
        table='account_tax', write='sql')
    openupgrade.logged_query(
        cr, """
        UPDATE account_tax
        SET type='percent',
            amount=0.0
        WHERE type='none'""",
    )


def map_account_tax_template_type(cr):
    """Same comments as in map_account_tax_type"""
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('code', 'group')],
        table='account_tax_template', write='sql')


def map_payment_term_line_value(cr):
    """ Someone fixed a Flemishism and payment terms percentages are now
    over 100, not over 1.
    """
    openupgrade.logged_query(
        cr,
        """UPDATE account_payment_term_line
        SET value = 'percent' WHERE value = 'procent';""")
    openupgrade.logged_query(
        cr, """
        UPDATE account_payment_term_line
        SET value_amount = value_amount * 100 WHERE value = 'percent'""",
    )


def blacklist_field_recomputation(env):
    """Create computed fields that take long time to compute, but will be
    filled with valid values by migration."""
    from openerp.addons.account.models.account_move import \
        AccountMove, AccountMoveLine
    AccountMove._openupgrade_recompute_fields_blacklist = [
        'currency_id',
        'amount',
        'matched_percentage',
    ]
    AccountMoveLine._openupgrade_recompute_fields_blacklist = [
        'amount_residual',
        'amount_residual_currency',
        'reconciled',
        'company_currency_id',
        'balance',
        'debit_cash_basis',
        'credit_cash_basis',
        'balance_cash_basis',
        'user_type_id',
    ]
    from openerp.addons.account.models.account_invoice import \
        AccountInvoice, AccountInvoiceLine
    AccountInvoice._openupgrade_recompute_fields_blacklist = [
        'payment_move_line_ids',
        'residual',
        'residual_signed',
        'residual_company_signed',
        'reconciled',
    ]
    AccountInvoiceLine._openupgrade_recompute_fields_blacklist = [
        'price_subtotal_signed',
        'currency_id',
    ]


def merge_supplier_invoice_refs(env):
    """In v8, there are 2 fields for writing references:
    supplier_invoice_number and reference. Now in v9 there's only the last one.
    We merge the first field content in the second one for avoiding data loss.
    Note that previously the `reference` field has been copied for preserving
    the original field contents.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice
        SET reference = supplier_invoice_number || ' - ' || reference
        WHERE type IN ('in_invoice', 'in_refund')
            AND reference IS NOT NULL
            AND supplier_invoice_number IS NOT NULL
            AND reference != supplier_invoice_number""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice
        SET reference = supplier_invoice_number
        WHERE type IN ('in_invoice', 'in_refund')
            AND reference IS NULL
            AND supplier_invoice_number IS NOT NULL"""
    )


def set_date_maturity(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line
        SET date_maturity = date
        WHERE date_maturity IS NULL"""
    )


def fast_create(env, settings):
    for setting in settings:
        (table_name, field_name, sql_type, sql_request) = setting
        logger.info(
            "Fast creation of the field '%s' (table '%s')" % (
                field_name, table_name))
        env.cr.execute(
            "ALTER TABLE %s ADD COLUMN %s %s;",
            (AsIs(table_name), AsIs(field_name), AsIs(sql_type)),)
        env.cr.execute(sql_request)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # 9.0 introduces a constraint enforcing this
    cr.execute(
        "update account_account set reconcile=True "
        "where type in ('receivable', 'payable')"
    )

    # Move obsolete table from connector_ecommerce out of the way to
    # prevent name conflict with new Odoo table
    if openupgrade.table_exists(cr, 'account_tax_group'):
        cr.execute(
            """ SELECT count(*) FROM ir_model_data
            WHERE name = 'model_account_tax_group'
            AND module = 'connector_ecommerce' """)
        if cr.fetchone()[0]:
            logger.info(
                "Moving connector_ecommerce's account_tax_group "
                "table out of the way.")
            openupgrade.rename_columns(
                cr, {'account_tax': [('group_id', None)]})
            openupgrade.rename_tables(
                cr, [('account_tax_group', None)])

    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.copy_columns(cr, column_copies)
    migrate_properties(cr)
    install_account_tax_python(cr)
    map_account_tax_type(cr)
    map_account_tax_template_type(cr)
    map_payment_term_line_value(cr)
    remove_account_moves_from_special_periods(cr)
    blacklist_field_recomputation(env)
    merge_supplier_invoice_refs(env)
    openupgrade.rename_fields(env, field_renames)
    set_date_maturity(env)

    # Fast Create new fields
    fast_create(env, FAST_CREATIONS)
    openupgrade.add_fields(
        env, [
            ('matched_percentage', 'account.move', 'account_move',
             'float', False, 'account'),
            ('debit_cash_basis', 'account.move.line', 'account_move_line',
             'monetary', False, 'account'),
            ('credit_cash_basis', 'account.move.line', 'account_move_line',
             'monetary', False, 'account'),
            ('balance_cash_basis', 'account.move.line', 'account_move_line',
             'monetary', False, 'account'),
        ]
    )
