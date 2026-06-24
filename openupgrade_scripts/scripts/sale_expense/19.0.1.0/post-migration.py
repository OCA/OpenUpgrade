# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fill_hr_expense_sale_order_line_id(env):
    """
    This function finds the corresponding sale order line for each hr.expense record
    based on the product, quantity, and expense name
    A sale order can have multiple lines with the same product and quantity,
    so we use DISTINCT ON to select the first matching sale order line
    """
    env.cr.execute(
        """
        WITH expense_sale_line_match AS (
            SELECT DISTINCT ON (he.id)
                he.id AS expense_id,
                sol.id AS sale_line_id
            FROM hr_expense he
            JOIN account_move_line aml ON aml.expense_id = he.id
            JOIN sale_order_line sol ON sol.name = aml.name
            JOIN sale_order so ON so.id = sol.order_id AND so.id = he.sale_order_id
            WHERE sol.product_id = he.product_id
                AND sol.product_uom_qty = he.quantity
                AND sol.is_expense = True
            ORDER BY he.id, sol.id
        )
        UPDATE hr_expense he
        SET sale_order_line_id = esm.sale_line_id
        FROM expense_sale_line_match esm
        WHERE esm.expense_id = he.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_hr_expense_sale_order_line_id(env)
