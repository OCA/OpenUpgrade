# Copyright 2026 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo import Command


@openupgrade.migrate()
def migrate(env, version):
    group_system = env.ref("base.group_system", False)
    group_dashboard_manager = env.ref(
        "spreadsheet_dashboard.group_dashboard_manager", False
    )
    if group_system and group_dashboard_manager:
        group_system.users.write(
            {"groups_id": [Command.link(group_dashboard_manager.id)]}
        )
