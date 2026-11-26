# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.exceptions import ValidationError


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
    openupgrade.logged_query(
        env.cr,
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
        """,
    )


def hr_expense_sheet_chatter(env):
    """
    Move the messages, attachments, followers and activities of each
    hr.expense.sheet to its first expense, and drop the activities of sheets
    without expenses, as the model no longer exists
    """
    sheet_expense = """
        sheet_expense AS (
            SELECT DISTINCT ON (former_sheet_id)
                former_sheet_id AS sheet_id, id AS expense_id, name
            FROM hr_expense
            WHERE former_sheet_id IS NOT NULL
            ORDER BY former_sheet_id, id
        )
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH {sheet_expense}
        UPDATE mail_message mm
        SET model = 'hr.expense', res_id = se.expense_id
        FROM sheet_expense se
        WHERE mm.model = 'hr.expense.sheet' AND mm.res_id = se.sheet_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH {sheet_expense}
        UPDATE ir_attachment ia
        SET res_model = 'hr.expense', res_id = se.expense_id
        FROM sheet_expense se
        WHERE ia.res_model = 'hr.expense.sheet' AND ia.res_id = se.sheet_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH {sheet_expense}
        UPDATE mail_followers mf
        SET res_model = 'hr.expense', res_id = se.expense_id
        FROM sheet_expense se
        WHERE mf.res_model = 'hr.expense.sheet' AND mf.res_id = se.sheet_id
            AND NOT EXISTS (
                SELECT 1 FROM mail_followers mf2
                WHERE mf2.res_model = 'hr.expense'
                    AND mf2.res_id = se.expense_id
                    AND mf2.partner_id = mf.partner_id
            )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        "DELETE FROM mail_followers WHERE res_model = 'hr.expense.sheet'",
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH {sheet_expense}
        UPDATE mail_activity ma
        SET res_model = 'hr.expense',
            res_model_id = im.id,
            res_id = se.expense_id,
            res_name = se.name
        FROM sheet_expense se, ir_model im
        WHERE ma.res_model = 'hr.expense.sheet' AND ma.res_id = se.sheet_id
            AND im.model = 'hr.expense'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        "DELETE FROM mail_activity WHERE res_model = 'hr.expense.sheet'",
    )


def update_product_uoms(env):
    """
    Set updated product uoms if possible
    """
    uom = env.ref("uom.product_uom_unit")
    for xmlid in ("expense_product_communication", "expense_product_gift"):
        product = env.ref(f"hr_expense.{xmlid}")
        org_uom = product.uom_id
        try:
            product.uom_id = uom
        except ValidationError:
            product.uom_id = org_uom


deleted_xmlids = [
    "hr_expense.hr_expense_report_comp_rule",
    "hr_expense.ir_rule_hr_expense_sheet_approver",
    "hr_expense.ir_rule_hr_expense_sheet_employee",
    "hr_expense.ir_rule_hr_expense_sheet_employee_not_draft",
    "hr_expense.ir_rule_hr_expense_sheet_manager",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "hr_expense",
        "19.0.2.1/noupdate_changes.xml",
        xml_transformation_filename="19.0.2.1/noupdate_changes-transformation.xml",
    )
    hr_expense_account_move_id(env)
    hr_expense_approval_fields(env)
    hr_expense_sheet_chatter(env)
    update_product_uoms(env)
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
