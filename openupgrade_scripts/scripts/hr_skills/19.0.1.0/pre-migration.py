# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    ("valid_from", "hr.employee.skill", "hr_employee_skill", "date", None, "hr_skills"),
]
_renamed_xmlids = [
    ("hr_skills_slides.resume_type_training", "hr_skills.resume_type_training"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
