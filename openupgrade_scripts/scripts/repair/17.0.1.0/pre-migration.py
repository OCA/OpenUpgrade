# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo.tools import sql


def add_helper_repair_move_rel(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move
        ADD COLUMN old_repair_line_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET old_repair_line_id = rl.id
        FROM repair_line rl
        WHERE sm.id = rl.move_id
        """,
    )
    # Create index for these columns, as they are going to be accessed frequently
    index_name = "stock_move_old_repair_line_id_index"
    sql.create_index(env.cr, index_name, "stock_move", ['"old_repair_line_id"'])


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.remove_tables_fks(env.cr, ["repair_line", "repair_fee"])
    add_helper_repair_move_rel(env)
