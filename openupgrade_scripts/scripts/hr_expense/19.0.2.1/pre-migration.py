# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

added_fields = [
    ("manager_id", "hr.expense", "hr_expense", "many2one", None, "hr_expense"),
    ("department_id", "hr.expense", "hr_expense", "many2one", None, "hr_expense"),
]

renamed_fields = []

copied_columns = {
    "hr_expense": [
        ("state", None, None),
        # It is important NOT to rename the sheet_id field because the hr_expense_sheet
        # module will continue to use that field
        ("sheet_id", "former_sheet_id", None),
    ],
    "hr_expense_sheet": [
        ("state", None, None),
        ("approval_state", None, None),
        ("user_id", "manager_id", None),
        ("total_tax_amount", "tax_amount", None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.copy_columns(env.cr, copied_columns)
    openupgrade.add_fields(env, added_fields)
