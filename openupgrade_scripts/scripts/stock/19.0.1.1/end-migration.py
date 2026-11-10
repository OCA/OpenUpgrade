# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["stock.picking"].search(
        [
            ("state", "not in", ("done", "cancel")),
        ]
    )._check_entire_pack()
