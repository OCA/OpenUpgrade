# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_column_renames = {
    "project_project": [
        ("billable_type", "pricing_type"),
    ],
}


def fill_pricing_type(env):
    openupgrade.logged_query(
        env.cr,
        """ UPDATE
                        project_project
                    SET
                        pricing_type = 'fixed_rate'
                    WHERE
                        pricing_type = 'task_rate'
""",
    )
    openupgrade.logged_query(
        env.cr,
        """ UPDATE
                        project_project
                    SET
                        pricing_type = ''
                    WHERE
                        pricing_type = 'no'
""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)

    fill_pricing_type(env)
