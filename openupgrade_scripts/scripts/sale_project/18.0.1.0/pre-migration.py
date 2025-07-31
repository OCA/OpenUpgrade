# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _fill_project_reinvoiced_sale_order_id(env):
    openupgrade.logged_query(
        env.cr,
        """
         ALTER TABLE project_project ADD COLUMN
         IF NOT EXISTS reinvoiced_sale_order_id INTEGER
         """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project p
        SET reinvoiced_sale_order_id = sol.order_id
        FROM sale_order_line sol
        WHERE p.reinvoiced_sale_order_id IS NULL
        AND p.sale_line_id = sol.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "product_template", "project_id"):
        openupgrade.rename_columns(
            env.cr,
            {"product_template": [("project_id", None)]},
        )
    if openupgrade.column_exists(env.cr, "product_template", "project_template_id"):
        openupgrade.rename_columns(
            env.cr,
            {"product_template": [("project_template_id", None)]},
        )
    _fill_project_reinvoiced_sale_order_id(env)
