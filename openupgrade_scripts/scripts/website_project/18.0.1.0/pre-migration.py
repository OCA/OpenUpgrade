# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

column_creates = [
    ("project.task", "partner_name", "char"),
    ("project.task", "partner_phone", "char"),
    ("project.task", "partner_company_name", "char"),
]


def fill_project_task_columns(env):
    """
    Set partner_name, partner_phone, and partner_company_name for project tasks.
    """
    env.cr.execute(
        """
        UPDATE project_task pt
        SET
            partner_name = rp.name,
            partner_phone = COALESCE(rp.mobile, rp.phone),
            partner_company_name = rp.company_name
        FROM res_partner rp
        WHERE pt.partner_id = rp.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, column_creates)
    fill_project_task_columns(env)
