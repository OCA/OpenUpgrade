# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

added_fields = [
    ("manager_id", "hr.expense", "hr_expense", "many2one", None, "hr_expense"),
    ("department_id", "hr.expense", "hr_expense", "many2one", None, "hr_expense"),
]

renamed_fields = [
    ("hr.expense", "hr_expense", "sheet_id", "former_sheet_id"),
]

copied_columns = {
    "hr_expense": [("state", None, None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.copy_columns(env.cr, copied_columns)
    openupgrade.add_fields(env, added_fields)
