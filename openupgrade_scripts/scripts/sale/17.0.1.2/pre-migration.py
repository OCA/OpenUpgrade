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


@openupgrade.migrate()
def migrate(env, version):
    _remove_table_constraints(env)
