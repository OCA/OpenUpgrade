# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {
            "project_project": [
                ("rating_status", None, None),
            ],
        },
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "project.project",
                "project_project",
                "portal_show_rating",
                "rating_active",
            ),
        ],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("project.access_partner_task user", "project.access_partner_task_user"),
        ],
    )
