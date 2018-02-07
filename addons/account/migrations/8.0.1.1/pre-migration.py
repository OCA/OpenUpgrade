# -*- coding: utf-8 -*-
# © 2014 Alexis de Lattre <alexis.delattre@akretion.com>
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


column_renames = {
    'account_bank_statement_line': [
        ('analytic_account_id', None),
        ('type', None),
        ('account_id', None),
    ]
}

tables_renames = [
    (
        'account_bank_statement_line_move_rel',
        'bak_account_bank_statement_line_move_rel'
    ),
]


def pre_compute_reconcile_ref_field(cr):
    """Create and compute values for new functional field reconcile_ref.

    Bypass the ORM auto creation and computation because it can take
    a long time and consume a lot of memory for large account_move_line.
    """
    cr.execute("""
        alter table account_move_line
        add column reconcile_ref character varying;
        """)
    cr.execute("""
        update account_move_line ml
            set reconcile_ref = r.name
        from account_move_reconcile r
        where ml.reconcile_partial_id = r.id;
        """)
    cr.execute("""
        update account_move_line ml
            set reconcile_ref = r.name
        from account_move_reconcile r
        where ml.reconcile_id = r.id;
        """)


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """SELECT id FROM account_analytic_journal WHERE type='purchase' """)
    res = cr.fetchone()
    if res:
        openupgrade.add_xmlid(
            cr, 'account', 'exp', 'account.analytic.journal', res[0], True)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, tables_renames)
    pre_compute_reconcile_ref_field(cr)
    # drop views that inhibit changing field types. They will be recreated
    # anyways
    for view in [
            'analytic_entries_report', 'account_entries_report',
            'report_invoice_created', 'report_aged_receivable']:
        cr.execute('drop view if exists %s cascade' % view)
    # Avoid inconsistencies between partner_id in account_invoice_line and
    # account invoice
    openupgrade.logged_query(
        cr, """
        UPDATE account_invoice_line ail
        SET partner_id=ai.partner_id
        FROM account_invoice ai
        WHERE
            ail.invoice_id = ai.id AND
            ail.partner_id != ai.partner_id;
        """)
    # delete a view from obsolete module account_report_company that causes
    # migration of the account module not to happen cleanly
    cr.execute(
        "delete from ir_ui_view v "
        "using ir_model_data d where "
        "v.id=d.res_id and d.model='ir.ui.view' and "
        "d.name='account_report_company_invoice_report_tree_view'")
