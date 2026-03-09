env = locals().get("env")

# create template with options
template = env["sale.order.template"].create(
    {
        "name": "Sale order template",
        "sale_order_template_line_ids": [],
        "sale_order_template_option_ids": [
            (
                0,
                0,
                {
                    "name": "some option",
                    "product_id": env.ref("product.product_product_1").id,
                    "uom_id": env.ref("uom.product_uom_unit").id,
                    "quantity": 42,
                },
            ),
            (
                0,
                0,
                {
                    "name": "another option",
                    "product_id": env.ref("product.product_product_2").id,
                    "uom_id": env.ref("uom.product_uom_unit").id,
                    "quantity": 4242,
                },
            ),
        ],
    }
)
order = env["sale.order"].create(
    {
        "partner_id": env.user.partner_id.id,
        "sale_order_template_id": template.id,
    }
)
order._onchange_sale_order_template_id()

env.cr.commit()
