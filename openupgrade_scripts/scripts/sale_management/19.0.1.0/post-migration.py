# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def sale_order_line_options(env):
    """
    Model sale.order.option has been replaced by optional lines on sale orders
    """
    SaleOrderLine = env["sale.order.line"]
    link_column = openupgrade.get_legacy_name("option_id")
    env.cr.execute(
        f"ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS {link_column} int "
    )
    env.cr.execute(
        """
        SELECT
        id, order_id, name, product_id, quantity, price_unit, sequence, uom_id, discount
        FROM
        sale_order_option
        """
    )
    for (
        option_id,
        order_id,
        name,
        product_id,
        quantity,
        price_unit,
        sequence,
        uom_id,
        discount,
    ) in env.cr.fetchall():
        line = SaleOrderLine.create(
            {
                "is_optional": True,
                "order_id": order_id,
                "name": name,
                "product_id": product_id,
                "product_uom_qty": quantity,
                "price_unit": price_unit,
                "sequence": sequence,
                "product_uom_id": uom_id,
                "discount": discount,
            }
        )
        env.cr.execute(
            f"""
            UPDATE sale_order_line
            SET {link_column}={option_id}
            WHERE id={line.id}
            """
        )


def sale_order_template_options(env):
    """
    Model sale.order.template.option has been replaced by optional lines
    """
    SaleOrderTemplateLine = env["sale.order.template.line"]
    link_column = openupgrade.get_legacy_name("option_id")
    env.cr.execute(
        "ALTER TABLE sale_order_template_line "
        f"ADD COLUMN IF NOT EXISTS {link_column} int "
    )
    env.cr.execute(
        """
        SELECT
        id, sale_order_template_id, name, product_id, quantity, uom_id
        FROM
        sale_order_template_option
        """
    )
    for (
        option_id,
        template_id,
        name,
        product_id,
        quantity,
        uom_id,
    ) in env.cr.fetchall():
        line = SaleOrderTemplateLine.create(
            {
                "is_optional": True,
                "sale_order_template_id": template_id,
                "name": name,
                "product_id": product_id,
                "product_uom_qty": quantity,
                "product_uom_id": uom_id,
            }
        )
        env.cr.execute(
            f"""
            UPDATE sale_order_template_line
            SET {link_column}={option_id}
            WHERE id={line.id}
            """
        )


@openupgrade.migrate()
def migrate(env, version):
    sale_order_line_options(env)
    sale_order_template_options(env)
