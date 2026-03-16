# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_renamed_tables = [
    ("account_move_mrp_production_rel", "wip_move_production_rel"),
]

_renamed_columns = {
    "wip_move_production_rel": [
        ("account_move_id", "move_id"),
        ("mrp_production_id", "production_id"),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.rename_columns(env.cr, _renamed_columns)
