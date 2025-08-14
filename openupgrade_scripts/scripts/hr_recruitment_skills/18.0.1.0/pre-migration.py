# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.remove_tables_fks(
        env.cr, ["hr_applicant_skill", "hr_applicant_hr_skill_rel"]
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_recruitment_skills", "hr_applicant_skill", "unique_skill"
    )
