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


def hr_expense_sheet_compatibility(env):
    """
    We update the statuses of the hr.expense.sheet records to match those of
    hr_expense_sheet (to ensure consistency with the statuses of hr.expense)
    """
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [
            ("submit", "submitted"),
            ("approve", "approved"),
            ("cancel", "refused"),
        ],
        table="hr_expense_sheet",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET state = 'posted'
        WHERE state = 'post' AND payment_state = 'not_paid'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET state = 'in_payment'
        WHERE state = 'post' AND payment_state = 'partial'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET state = 'paid'
        WHERE state = 'post' AND payment_state IN ('paid', 'reversed')
        """,
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("approval_state"),
        "approval_state",
        [
            ("submit", "submitted"),
            ("approve", "approved"),
            ("post", "posted"),
            ("cancel", "refused"),
        ],
        table="hr_expense_sheet",
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
    hr_expense_sheet_compatibility(env)
    update_product_uoms(env)
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
