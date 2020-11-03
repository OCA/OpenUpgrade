# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("hr_expense.ir_rule_hr_expense_user",
             "hr_expense.ir_rule_hr_expense_approver"),
            ("hr_expense.ir_rule_hr_expense_sheet_user",
             "hr_expense.ir_rule_hr_expense_sheet_approver"),
        ],
    )
