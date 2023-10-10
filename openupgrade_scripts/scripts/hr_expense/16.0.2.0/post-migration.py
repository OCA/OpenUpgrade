# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _hr_expense_process(env):
    """Set amount_tax_company value only when it is necessary with ORM."""
    env.cr.execute(
        """
        SELECT id
        FROM hr_expense
        WHERE total_amount_company != total_amount AND amount_tax > 0
        AND amount_tax_company != 0
        """
    )
    expense_model = env["hr.expense"]
    for expense_id in env.cr.fetchall():
        expense = expense_model.browse(expense_id)
        expense._compute_amount_tax()


def _hr_expense_sheet_process(env):
    """With the hr.expense values already defined, we can now set the missing data."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet SET total_amount_taxes = (
            SELECT SUM(amount_tax_company)
            FROM hr_expense
            WHERE sheet_id = hr_expense_sheet.id
        ) WHERE total_amount_taxes = 0
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET untaxed_amount = (total_amount - total_amount_taxes)
        WHERE untaxed_amount = 0
        """,
    )


def _hr_expense_analytic_tag(env):
    """If table exists and there are any records, we set the module
    hr_expense_analytic_tag to be installed."""
    if openupgrade.table_exists(env.cr, "account_analytic_tag_hr_expense_rel"):
        env.cr.execute(
            """SELECT COUNT(*)
            FROM account_analytic_tag_hr_expense_rel""",
        )
        if env.cr.fetchone()[0]:
            openupgrade.logged_query(
                env.cr,
                """UPDATE ir_module_module
                SET state = 'to install'
                WHERE name = 'hr_expense_analytic_tag'""",
            )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr_expense", "16.0.2.0/noupdate_changes.xml")
    _hr_expense_process(env)
    _hr_expense_sheet_process(env)
    _hr_expense_analytic_tag(env)
