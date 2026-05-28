from openupgradelib import openupgrade

# overtime_id removed in 19.0; drop the column whose FK the overtime rename invalidated.
_dropped_columns = [
    ("hr_leave", "overtime_id"),
    ("hr_leave_allocation", "overtime_id"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.drop_columns(env.cr, _dropped_columns)
