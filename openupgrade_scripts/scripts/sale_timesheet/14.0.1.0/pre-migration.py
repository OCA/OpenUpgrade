# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_column_copies = {
    "project_project": [("billable_type", None, None)],
}
_field_renames = [
    ("project.project", "project_project", "billable_type", "pricing_type"),
]


def map_pricing_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project
        SET pricing_type = 'fixed_rate'
        WHERE pricing_type = 'task_rate'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project
        SET pricing_type = NULL
        WHERE pricing_type = 'no'""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_fields(env, _field_renames)
    map_pricing_type(env)
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_project ADD timesheet_product_id int4"
    )
