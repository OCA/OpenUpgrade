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
    'account_invoice': [
        ('reference_type', None),
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
            min(ail.sequence) - 1 as sequence, max(slc.name), 0, 0,
            'line_section', min(ail.create_uid), min(ail.create_date),
            min(ail.write_uid), min(ail.write_date)
        FROM account_invoice_line ail
        INNER JOIN sale_layout_category slc ON slc.id = ail.layout_category_id
        GROUP BY invoice_id, layout_category_id
        ORDER BY invoice_id, layout_category_id, sequence
        """
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
