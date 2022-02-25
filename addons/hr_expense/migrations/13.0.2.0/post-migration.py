# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def assign_account_tags_to_move_lines_from_expenses(env):
    """ Migrate all account.account.tag's of move lines that are a result of
        expenses.
    """
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aatatrlr.account_account_tag_id
        FROM account_move_line aml
        JOIN expense_tax et ON et.expense_id = aml.expense_id
        JOIN account_tax_repartition_line atrl ON
            atrl.invoice_tax_id = et.tax_id OR atrl.refund_tax_id = et.tax_id
        JOIN account_account_tag_account_tax_repartition_line_rel aatatrlr ON
            aatatrlr.account_tax_repartition_line_id = atrl.id
        ON CONFLICT DO NOTHING"""
    )


def fill_hr_expense_company_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense he
        SET company_id = emp.company_id
        FROM hr_employee emp
        WHERE emp.id = he.employee_id AND
        he.company_id is NULL""",
    )


def fill_hr_expense_sheet_company_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense_sheet hes
        SET company_id = emp.company_id
        FROM hr_employee emp
        WHERE emp.id = hes.employee_id AND
        hes.company_id is NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    assign_account_tags_to_move_lines_from_expenses(env)
    fill_hr_expense_company_id(env)
    fill_hr_expense_sheet_company_id(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "hr_expense.ir_rule_hr_expense_user",
            "hr_expense.ir_rule_hr_expense_sheet_user",
            "hr_expense.product_product_fixed_cost",
        ],
    )
    openupgrade.load_data(
        env.cr, 'hr_expense', 'migrations/13.0.2.0/noupdate_changes.xml')
