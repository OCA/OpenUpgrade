# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def hr_expense_account_move_id(env):
    """
    Fill account.move#expense_ids from expense_sheet_id
    """
    env.cr.execute(
        """
        UPDATE hr_expense
        SET account_move_id=account_move.id
        FROM
        account_move
        WHERE
        account_move.expense_sheet_id=hr_expense.former_sheet_id
        """
    )


def hr_expense_approval_fields(env):
    """
    Fill hr.expense#approval_{date,state} and manager_id from hr.expense.sheet
    """
    env.cr.execute(
        """
        UPDATE hr_expense
        SET
        approval_date=hr_expense_sheet.approval_date,
        approval_state=CASE
            WHEN hr_expense_sheet.approval_state = 'approve' THEN 'approved'
            WHEN hr_expense_sheet.approval_state = 'cancel' THEN 'refused'
            WHEN hr_expense_sheet.approval_state = 'submit' THEN 'submitted'
        END,
        manager_id=hr_expense_sheet.user_id,
        department_id=hr_expense_sheet.department_id
        FROM
        hr_expense_sheet
        WHERE
        hr_expense.former_sheet_id=hr_expense_sheet.id
        """
    )


def hr_expense_state(env):
    """
    Recompute hr.expense#state for records in states 'approved', 'done', 'reported'
    """
    env.cr.execute(
        "SELECT id FROM hr_expense WHERE state IN ('approved', 'done', 'reported')"
    )
    records = env["hr.expense"].browse(_id for (_id,) in env.cr.fetchall())
    records._compute_state()


deleted_xmlids = [
    "hr_expense.hr_expense_report_comp_rule",
    "hr_expense.ir_rule_hr_expense_sheet_approver",
    "hr_expense.ir_rule_hr_expense_sheet_employee",
    "hr_expense.ir_rule_hr_expense_sheet_employee_not_draft",
    "hr_expense.ir_rule_hr_expense_sheet_manager",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_expense", "19.0.2.1/noupdate_changes.xml")
    hr_expense_account_move_id(env)
    hr_expense_approval_fields(env)
    hr_expense_state(env)
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
