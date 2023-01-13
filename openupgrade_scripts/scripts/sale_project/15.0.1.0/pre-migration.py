# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Disappeared constraint
    openupgrade.delete_sql_constraint_safely(
        env, "sale_project", "project_project", "sale_order_required_if_sale_line"
    )
