# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_160


def _hr_expense_table_new_columns(env):
    """Custom process to create new columns:
    - amount_tax: (total_amount - untaxed_amount). It will be similar enough.
    - amount_tax_company: the same value as amount_tax if same currency, and let
      for post-migration for different currency.
    """
    if not openupgrade.column_exists(env.cr, "hr_expense", "amount_tax"):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE hr_expense ADD COLUMN amount_tax numeric",
        )
        openupgrade.logged_query(
            env.cr, "UPDATE hr_expense SET amount_tax = (total_amount - untaxed_amount)"
        )
    if not openupgrade.column_exists(env.cr, "hr_expense", "amount_tax_company"):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE hr_expense ADD COLUMN amount_tax_company numeric",
        )
        openupgrade.logged_query(
            env.cr,
            """UPDATE hr_expense he
            SET amount_tax_company = amount_tax
            FROM res_company rc
            WHERE rc.id = he.company_id AND rc.currency_id = he.currency_id
            """,
        )


def _hr_expense_sheet_table_new_columns(env):
    """Pre-create columns to be processed on post-migration."""
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE hr_expense_sheet
        ADD COLUMN IF NOT EXISTS total_amount_taxes numeric""",
    )
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE hr_expense_sheet
        ADD COLUMN IF NOT EXISTS untaxed_amount numeric""",
    )


def _fast_fill_analytic_distribution_on_hr_expense(env):
    if not openupgrade.column_exists(env.cr, "hr_expense", "analytic_distribution"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_expense
            ADD COLUMN IF NOT EXISTS analytic_distribution jsonb;
            """,
        )
    openupgrade_160.fill_analytic_distribution(
        env,
        table="hr_expense",
        m2m_rel="account_analytic_tag_hr_expense_rel",
        m2m_column1="hr_expense_id",
    )


def _convert_expense_sheet_entries_to_invoices(env):
    """From v16 onwards, account_move related to hr_expense_sheet are created with
    move_type = "in_invoice" as per
    https://github.com/odoo/odoo/blob/87f4667d81f7d8a40dcf225f3daf1a9e2795680d/
    addons/hr_expense/models/hr_expense.py#L1297
    on contrary than on v15, which was "entry".

    Then, in _compute_payment_state from account.move it will check if the move_type is
    "entry", putting payment_state = "not_paid" for that cases, no matter the
    reconcilation:
    https://github.com/odoo/odoo/blob/87f4667d81f7d8a40dcf225f3daf1a9e2795680d/
    addons/account/models/account_move.py#L926

    As the sheet payment state is taken from the move's payment_state, we need to
    switch all the existing expenses entries to "in_invoice".
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET move_type = 'in_invoice'
        FROM hr_expense_sheet hes
        WHERE hes.account_move_id = am.id AND am.move_type <> 'in_invoice'
        """,
    )


_xmlid_renames = [
    (
        "hr_expense.product_product_zero_cost",
        "hr_expense.product_product_no_cost",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    _hr_expense_table_new_columns(env)
    _hr_expense_sheet_table_new_columns(env)
    _fast_fill_analytic_distribution_on_hr_expense(env)
    _convert_expense_sheet_entries_to_invoices(env)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
