# Copyright 2026 OpenUpgrade Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_new_columns = [
    ("hr.employee", "manually_set_presence", "boolean", False),
]

_column_copies = {
    "hr_employee": [("hr_presence_state_display", None, None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, _new_columns)
    openupgrade.copy_columns(env.cr, _column_copies)
