# Copyright 2023 Viindoo - Nguyễn Đại Dương
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _remove_table_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env, "sale", "res_company", "res_company_check_quotation_validity_days"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "sale", "sale_order", "sale_order_date_order_conditional_required"
    )


def _sale_sale_order(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order
            ADD COLUMN IF NOT EXISTS locked BOOLEAN
            ADD COLUMN IF NOT EXISTS temp_state VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order so
        SET temp_state = so.state
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order so
        SET so.state = 'sale'
        WHERE so.state = 'done'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _remove_table_constraints(env)
    _sale_sale_order(env)
