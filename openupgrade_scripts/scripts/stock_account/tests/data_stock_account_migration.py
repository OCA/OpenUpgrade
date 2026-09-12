env = locals().get("env")

category_fifo = env["product.category"].create(
    {
        "name": "FIFO category",
        "property_valuation": "real_time",
        "property_cost_method": "fifo",
    }
)
category_avg = env["product.category"].create(
    {
        "name": "AVG category",
        "property_valuation": "real_time",
        "property_cost_method": "average",
    }
)

product_fifo = env["product.product"].create(
    {
        "name": "FIFO product",
        "categ_id": category_fifo.id,
        "standard_price": 10,
        "is_storable": True,
    }
)

product_avg = env["product.product"].create(
    {
        "name": "AVG product",
        "categ_id": category_avg.id,
        "standard_price": 10,
        "is_storable": True,
    }
)

location_customer = env.ref("stock.stock_location_customers")
location_supplier = env.ref("stock.stock_location_suppliers")
location_stock = env.ref("stock.stock_location_stock")


def buy(product, **kwargs):
    in_move = env["stock.move"].create(
        dict(
            {
                "name": "/",
                "product_id": product.id,
                "location_id": location_supplier.id,
                "location_dest_id": location_stock.id,
            },
            **kwargs,
        )
    )
    in_move._action_confirm()
    in_move.picked = True
    in_move._action_done()
    return in_move


# fifo product
buy(product_fifo, price_unit=20, product_uom_qty=2)
buy(product_fifo, price_unit=22, product_uom_qty=2)
product_fifo_out_move = env["stock.move"].create(
    {
        "name": "OUT FIFO",
        "product_id": product_fifo.id,
        "location_id": location_stock.id,
        "location_dest_id": location_customer.id,
        "product_uom_qty": 2,
    }
)
product_fifo_out_move._action_confirm()
product_fifo_out_move.picked = True
product_fifo_out_move._action_assign(force_qty=2)
product_fifo_out_move._action_done()
assert product_fifo.standard_price == 22
# avg product
buy(product_avg, price_unit=20, product_uom_qty=2)
buy(product_avg, price_unit=22, product_uom_qty=2)
assert product_avg.standard_price == 21
# setting the price must happen in its own transaction, otherwise the create date
# of the resulting stock valuation layer is equal to the previous or following ones
env.cr.commit()
product_avg.standard_price = 22
env.cr.commit()
