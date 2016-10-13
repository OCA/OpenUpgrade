# -*- coding: utf-8 -*-
# © 2016 Sylvain LE GAL <https://twitter.com/legalsylvain>
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_renames = {
    'account_bank_statement': [
        ('closing_date', 'date_done'),
    ],
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
    ],
    'account_tax_template': [
        ('type_tax_use', None, None),
        ('type', None, None),
    ],
}

table_renames = [
    ('account_statement_operation_template', 'account_operation_template'),
    ('account_tax_code', 'account_tax_group')]

PROPERTY_FIELDS = {
    ('product.category', 'property_account_expense_categ',
     'property_account_expense_categ_id'),
    ('product.category', 'property_account_income_categ',
     'property_account_income_categ_id'),
    ('res.partner', 'property_account_payable', 'property_account_payable_id'),
    ('res.partner', 'property_account_receivable',
     'property_account_receivable_id'),
}


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


def no_remove_moves_exception_modules():
    """ In some countries the odoo standard closing procedure is not used,
    and the special periods should not be deleted."""
    return ['l10n_es_fiscal_year_closing']


def remove_account_moves_from_special_periods(cr):
    """We first search for journal entries in a special period, in the
    first reported fiscal year of the company, and we take them out of the
    special period, into a normal period, because we assume that this is
    the starting balance of the company, and should be maintained.
    Then we delete all the moves associated to special periods."""

    module_names = no_remove_moves_exception_modules()
    cr.execute("""
        SELECT * FROM ir_module_module
        WHERE name in %s
        AND state='installed'
    """, (tuple(module_names),))
    if cr.fetchall():
        return True

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
    first_nsp_id = cr.fetchone()[0] or False

    if first_nsp_id and move_ids:
        openupgrade.logged_query(cr, """
            UPDATE account_move
            SET period_id = %s
            where id in %s
            """, (first_nsp_id, tuple(move_ids)))

    openupgrade.logged_query(cr, """
        DELETE FROM account_move_line
        WHERE move_id IN (SELECT id FROM account_move WHERE period_id IN (
        SELECT id FROM account_period WHERE special = True))
    """)

    openupgrade.logged_query(cr, """
        DELETE FROM account_move
        WHERE period_id IN (SELECT id FROM account_period WHERE special = True)
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
    restore the original value."""
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('code', 'group')],
        table='account_tax', write='sql')


def map_account_tax_template_type(cr):
    """Same comments as in map_account_tax_type"""
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('code', 'group')],
        table='account_tax_template', write='sql')


@openupgrade.migrate()
def migrate(cr, version):
    # 9.0 introduces a constraint enforcing this
    cr.execute(
        "update account_account set reconcile=True "
        "where type in ('receivable', 'payable')"
    )
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
    migrate_properties(cr)
    install_account_tax_python(cr)
    map_account_tax_type(cr)
    map_account_tax_template_type(cr)
    remove_account_moves_from_special_periods(cr)
