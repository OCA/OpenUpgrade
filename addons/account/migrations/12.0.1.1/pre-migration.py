# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'account_journal': [
        ('bank_statements_source', None, None),
    ],
    'account_payment_term_line': [
        ('option', None, None),
    ],
    'account_invoice': [
        ('reference_type', None, None),
    ],
}

_column_renames = {
    'account_tax': [
        ('tax_adjustment', None),
    ],
    'account_tax_template': [
        ('tax_adjustment', None),
    ],
    'account_chart_template': [
        ('company_id', None),
        ('transfer_account_id', None)
    ],
}

_field_renames = [
    ('account.tax', 'account_tax', 'cash_basis_account',
     'cash_basis_account_id'),
    ('account.tax.template', 'account_tax_template', 'cash_basis_account',
     'cash_basis_account_id'),
]

_field_renames_sale = [
    ('res.config.settings', 'res_config_settings', 'group_show_price_subtotal',
     'group_show_line_subtotals_tax_excluded'),
    ('res.config.settings', 'res_config_settings', 'group_show_price_total',
     'group_show_line_subtotals_tax_included'),
    ('res.config.settings', 'res_config_settings', 'sale_show_tax',
     'show_line_subtotals_tax_selection'),
]

_field_renames_account_reversal = [
    ('account.move', 'account_move', 'to_be_reversed', 'auto_reverse'),
    ('account.move', 'account_move', 'reversal_id', 'reverse_entry_id'),
]

xmlid_renames = [
    ('sale.group_show_price_subtotal',
     'account.group_show_line_subtotals_tax_excluded'),
    ('sale.group_show_price_total',
     'account.group_show_line_subtotals_tax_included'),
    ('sale_timesheet.account_analytic_line_rule_billing_user',
     'account.account_analytic_line_rule_billing_user'),
]


def fill_account_invoice_line_sections(cr):
    """It's done here instead of post-migration to avoid
    possible new rows added in the migration (just in case)"""
    if not openupgrade.column_exists(
        cr, 'account_invoice_line', 'layout_category_id'
    ):
        # Module 'sale' not installed in previous version
        return
    cr.execute(
        "ALTER TABLE account_invoice_line ADD COLUMN display_type varchar",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE account_invoice_line ail
        SET sequence = sub.rank * 5
        FROM (
            SELECT id, rank()
            OVER (
                PARTITION BY invoice_id ORDER BY sequence, id
            ) FROM account_invoice_line
        ) sub
        WHERE ail.id = sub.id
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE account_invoice_line ALTER COLUMN account_id DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        INSERT INTO account_invoice_line (invoice_id, layout_category_id,
            sequence, name, price_unit, quantity, display_type,
            create_uid, create_date, write_uid, write_date)
        SELECT ail.invoice_id, ail.layout_category_id,
            min(ail.sequence) - 1 as sequence, max(COALESCE(slc.name, ' ')),
            0, 0, 'line_section', min(ail.create_uid), min(ail.create_date),
            min(ail.write_uid), min(ail.write_date)
        FROM account_invoice_line ail
        LEFT JOIN sale_layout_category slc ON slc.id = ail.layout_category_id
        WHERE ail.invoice_id in (
            SELECT invoice_id
            FROM account_invoice_line
            WHERE layout_category_id IS NOT NULL)
        GROUP BY invoice_id, layout_category_id
        ORDER BY invoice_id, layout_category_id, sequence
        """
    )


def prefill_account_chart_template_transfer_account_prefix(env):
    """We do this for avoiding a temporary warning on null values."""
    openupgrade.add_fields(
        env, [('transfer_account_code_prefix', 'account.chart.template',
               'account_chart_template', 'char', False, 'account')],
    )
    openupgrade.logged_query(
        env.cr, "UPDATE account_chart_template "
                "SET transfer_account_code_prefix = 'OUB'")


def drop_obsolete_fk_constraints(env):
    """We remove the constraints on wizard_multi_charts_accounts
    to avoid not null error if account chart changed and account template has
    been removed.
    For exemple l10n_fr.pcg_58 has been removed between 11.0 and 12.0
    and is used as default transfer_account_id.
    Note : wizard_multi_charts_accounts is an obsolete table. Model
    has been removed in V12.0
    """
    openupgrade.remove_tables_fks(env.cr, [
        'wizard_multi_charts_accounts',
        'account_aged_trial_balance',
        'account_aged_trial_balance_account_journal_rel',
        'account_balance_report',
        'account_balance_report_journal_rel',
        'account_bank_accounts_wizard',
        'account_common_account_report',
        'account_common_partner_report',
        'account_financial_report',
        'accounting_report',
        'account_move_line_reconcile',
        'account_move_line_reconcile_writeoff',
        'account_opening',
        'account_report_general_ledger',
        'account_report_general_ledger_journal_rel',
        'account_report_partner_ledger',
        'account_tax_report',
    ])
    # also, we lift some obsolete fk constraints from mny2ones
    openupgrade.lift_constraints(env.cr, "account_chart_template", "transfer_account_id")
    openupgrade.lift_constraints(env.cr, "account_chart_template", "company_id")
    openupgrade.lift_constraints(env.cr, "account_tax_template", "company_id")


def fix_double_membership(cr):
    # avoid error raised by new function '_check_one_user_type'

    # we arbitrarily keep the tax included
    group_to_remove = "group_show_line_subtotals_tax_excluded"
    group_to_keep = "group_show_line_subtotals_tax_included"
    openupgrade.logged_query(
        cr, """
            DELETE FROM res_groups_users_rel
            WHERE
            gid = (
                SELECT res_id
                FROM ir_model_data
                WHERE module = 'account' AND name = %s
            )
            AND uid IN (
                SELECT uid FROM res_groups_users_rel WHERE gid IN (
                    SELECT res_id
                    FROM ir_model_data
                    WHERE module = 'account'
                    AND name IN (%s, %s)
                )
                GROUP BY uid
                HAVING count(*) > 1
            );
        """, (group_to_remove, group_to_remove, group_to_keep)
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.delete_records_safely_by_xml_id(
        env, ['account.action_view_account_move_line_reconcile'],
    )
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    if openupgrade.table_exists(cr, 'sale_order'):
        openupgrade.rename_fields(env, _field_renames_sale)
    if openupgrade.table_exists(cr, 'sale_layout_category'):
        fill_account_invoice_line_sections(cr)
    if openupgrade.table_exists(cr, 'account_move_reverse'):
        # module account_reversal
        openupgrade.rename_fields(env, _field_renames_account_reversal)
    if not openupgrade.column_exists(env.cr, 'res_company', 'incoterm_id'):
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE res_company ADD COLUMN incoterm_id INTEGER""",
        )
    prefill_account_chart_template_transfer_account_prefix(env)
    drop_obsolete_fk_constraints(env)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'account', ['account_analytic_line_rule_billing_user'], False)

    # Fix potentiel duplicates in res_groups_users_rel
    fix_double_membership(env.cr)
