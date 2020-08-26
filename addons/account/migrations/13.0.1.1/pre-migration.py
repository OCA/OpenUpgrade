# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo import fields
from odoo.tools import sql

_column_copies = {
    'res_company': [
        ('fiscalyear_last_month', None, None),
    ],
    'account_payment_term_line': [
        ('option', None, None),
    ],
}

_column_renames = {
    'account_move_line': [
        ('user_type_id', None),
    ],
    'account_journal': [
        ('post_at_bank_rec', None),
        ('update_posted', None),
    ],
    'account_reconcile_model': [
        ('second_tax_id', None),
        ('tax_id', None),
    ],
    'account_reconcile_model_template': [
        ('second_tax_id', None),
        ('tax_id', None),
    ],
    'res_company': [
        ('invoice_reference_type', None),
    ],
}

_field_renames = [
    ('account.move', 'account_move', 'amount', 'amount_total'),
    ('account.move', 'account_move', 'reverse_entry_id', 'reversed_entry_id'),
]

_field_sale_renames = [
    ('res.company', 'res_company', 'sale_note', 'invoice_terms'),
]

_model_renames = [
    ('account.register.payments', 'account.payment.register'),
]

_table_renames = [
    ('account_register_payments', 'account_payment_register'),
    ('account_analytic_tag_account_reconcile_model_rel',
     'account_reconcile_model_analytic_tag_rel'),
]


def type_change_account_fiscal_position_zips(env):
    tables = ['account_fiscal_position', 'account_fiscal_position_template']
    fields = ['zip_from', 'zip_to']
    for table in tables:
        for field in fields:
            openupgrade.logged_query(
                env.cr,
                "ALTER TABLE %(table)s "
                "ALTER COLUMN %(field)s "
                "TYPE varchar" % {
                    'table': table,
                    'field': field,
                })


def create_account_invoice_amount_tax_company_signed(env):
    if not openupgrade.column_exists(
            env.cr, "account_invoice", "amount_tax_company_signed"):
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE account_invoice
            ADD COLUMN amount_tax_company_signed numeric"""
        )
        openupgrade.logged_query(
            env.cr, """
            SELECT ai.id, ai.amount_tax, ai.type, ai.currency_id,
                ai.company_id, rc.currency_id, ai.date_invoice
            FROM account_invoice ai
            JOIN res_company rc ON ai.company_id = rc.id"""
        )
        for _id, tax, inv_type, curr, company, company_curr, date in \
                env.cr.fetchall():
            company_tax = tax
            if curr != company_curr:
                curr_ = env["res.currency"].browse(curr)
                company_curr_ = env["res.currency"].browse(company_curr)
                company_ = env["res.company"].browse(company)
                company_tax = curr_._convert(
                    company_tax, company_curr_, company_,
                    date or fields.Date.today())
            sign = inv_type in ['in_refund', 'out_refund'] and -1 or 1
            company_tax = company_tax * sign
            openupgrade.logged_query(
                env.cr, """
                UPDATE account_invoice
                SET amount_tax_company_signed = %s WHERE id = %s""",
                (company_tax, _id),
            )


def create_account_move_new_columns(env):
    """Faster way, avoid compute"""
    data = {
        'account_move': [
            ('amount_total_signed', 'numeric'),
            ('amount_untaxed', 'numeric'),
            ('amount_untaxed_signed', 'numeric'),
            ('amount_tax', 'numeric'),
            ('amount_tax_signed', 'numeric'),
            ('amount_residual_signed', 'numeric'),
        ],
    }
    for table, column_spec_list in data.items():
        for column, column_type in column_spec_list:
            openupgrade.logged_query(
                env.cr, """
                ALTER TABLE {table}
                ADD COLUMN {column} {column_type}""".format(
                    table=table, column=column, column_type=column_type
                ),
            )


def fill_account_move_line_parent_state(env):
    """Faster way"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN parent_state varchar""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET parent_state = am.state
        FROM account_move am
        WHERE am.id = aml.move_id""",
    )


def fill_account_move_line_account_internal_type(env):
    """Faster way"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN account_internal_type varchar""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET account_internal_type = aat.type
        FROM account_account aa
        JOIN account_account_type aat ON aa.user_type_id = aat.id
        WHERE aml.account_id = aa.id""",
    )


def create_res_partner_ranks(env):
    """Faster way"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner
        ADD COLUMN customer_rank integer
        DEFAULT 0""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner ALTER COLUMN customer_rank DROP DEFAULT""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner
        ADD COLUMN supplier_rank integer
        DEFAULT 0""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner ALTER COLUMN supplier_rank DROP DEFAULT""",
    )


def add_helper_invoice_move_rel(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move
        ADD COLUMN old_invoice_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET old_invoice_id = ai.id
        FROM account_invoice ai
        WHERE ai.move_id = am.id
        """,
    )
    index_name = '%s_%s_index' % ("account_move", "old_invoice_id")
    sql.create_index(
        env.cr, index_name, "account_move", ['"%s"' % "old_invoice_id"])
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET old_invoice_id = aml.invoice_id
        FROM account_move_line aml
        WHERE aml.move_id = am.id AND am.old_invoice_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice ai
        SET move_id = am.old_invoice_id
        FROM account_move am
        WHERE am.old_invoice_id = ai.id AND ai.move_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN old_invoice_line_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN old_invoice_tax_id integer""",
    )


def add_helper_voucher_move_rel(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move
        ADD COLUMN old_voucher_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET old_voucher_id = av.id
        FROM account_voucher av
        WHERE av.move_id = am.id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN old_voucher_line_id integer""",
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    if openupgrade.table_exists(cr, 'sale_order'):
        openupgrade.rename_fields(env, _field_sale_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    type_change_account_fiscal_position_zips(env)
    create_account_invoice_amount_tax_company_signed(env)
    create_account_move_new_columns(env)
    fill_account_move_line_parent_state(env)
    fill_account_move_line_account_internal_type(env)
    create_res_partner_ranks(env)
    add_helper_invoice_move_rel(env)
    if openupgrade.table_exists(cr, 'account_voucher'):
        add_helper_voucher_move_rel(env)
