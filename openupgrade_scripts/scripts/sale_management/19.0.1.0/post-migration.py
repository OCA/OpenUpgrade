# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from openupgradelib import openupgrade


def sale_order_line_options(env):
    """
    Model sale.order.option has been replaced by optional lines on sale orders
    """
    SaleOrderLine = env["sale.order.line"]
    env.cr.execute(
        """
        SELECT
        soo.order_id, name, product_id, quantity, price_unit, sequence, uom_id,
        discount, line_id, max_sequence
        FROM
        sale_order_option soo
        LEFT JOIN
        (
            SELECT order_id, MAX(sequence) max_sequence
            FROM sale_order_line
            GROUP BY order_id
        ) order2max_sequence
        ON order2max_sequence.order_id=soo.order_id
        ORDER BY
        order_id
        """
    )
    last_order_id = 0
    for (
        order_id,
        name,
        product_id,
        quantity,
        price_unit,
        sequence,
        uom_id,
        discount,
        line_id,
        max_sequence,
    ) in env.cr.fetchall():
        if order_id != last_order_id:
            SaleOrderLine.create(
                {
                    "is_optional": True,
                    "order_id": order_id,
                    "name": "/",
                    "display_type": "line_section",
                    "sequence": (max_sequence or 0) + 1,
                }
            )
        sequence = (max_sequence or 0) + 2 + (sequence or 0)
        if line_id:
            SaleOrderLine.browse(line_id).sequence = sequence
        else:
            SaleOrderLine.create(
                {
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
        last_order_id = order_id


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
        id, soto.sale_order_template_id, name, product_id, quantity, uom_id,
        max_sequence
        FROM
        sale_order_template_option soto
        LEFT JOIN
        (
            SELECT sale_order_template_id, max(sequence) max_sequence
            FROM sale_order_template_line
            GROUP BY sale_order_template_id
        ) template2max_sequence
        ON
        template2max_sequence.sale_order_template_id=soto.sale_order_template_id
        ORDER BY
        sale_order_template_id
        """
    )
    last_template_id = 0
    for (
        option_id,
        template_id,
        name,
        product_id,
        quantity,
        uom_id,
        max_sequence,
    ) in env.cr.fetchall():
        if template_id != last_template_id:
            SaleOrderTemplateLine.create(
                {
                    "is_optional": True,
                    "sale_order_template_id": template_id,
                    "name": "/",
                    "display_type": "line_section",
                    "sequence": (max_sequence or 0) + 1,
                }
            )
        line = SaleOrderTemplateLine.create(
            {
                "sale_order_template_id": template_id,
                "name": "/",
                "product_id": product_id,
                "product_uom_qty": quantity,
                "product_uom_id": uom_id,
                "sequence": (max_sequence or 0) + 2,
            }
        )
        env.cr.execute(
            f"""
            UPDATE sale_order_template_line
            SET {link_column}={option_id}, name=%s
            WHERE id={line.id}
            """,
            (json.dumps(name),),
        )
        last_template_id = template_id


@openupgrade.migrate()
def migrate(env, version):
    sale_order_line_options(env)
    sale_order_template_options(env)
