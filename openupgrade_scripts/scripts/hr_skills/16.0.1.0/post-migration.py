# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import deque

from openupgradelib import openupgrade


def _fill_hr_employee_hr_skills(env):
    """Drop the previous fake table and create correctly all the relations through ORM,
    and then populate the expected data equivalent to the compute method.
    """
    openupgrade.logged_query(env.cr, "DROP TABLE hr_employee_hr_skill_rel")
    env.registry._post_init_queue = deque()
    HrEmployee = env["hr.employee"]
    HrEmployee._fields["skill_ids"].update_db(HrEmployee, False)
    openupgrade.logged_query(
        env.cr,
        """INSERT INTO hr_employee_hr_skill_rel
        (hr_employee_id, hr_skill_id)
        SELECT employee_id, skill_id
        FROM hr_employee_skill
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_hr_employee_hr_skills(env)
    openupgrade.load_data(env.cr, "hr_skills", "16.0.1.0/noupdate_changes.xml")
