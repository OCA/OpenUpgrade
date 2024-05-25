# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Create fake table for not triggering the compute method
    env.cr.execute(
        """CREATE TABLE hr_employee_hr_skill_rel
        (hr_employee_id integer, hr_skill_id integer)"""
    )
