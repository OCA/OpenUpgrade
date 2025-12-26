env = locals().get("env")
# packaging that should be assigned existing UOM
product = env.ref("product.product_delivery_01")
packaging = env["product.packaging"].create(
    {
        "name": "Sixpack",
        "barcode": "42 42",
        "product_id": product.id,
        "qty": 6,
    }
)
# packaging that should have a new UOM created
product = env.ref("product.product_delivery_01")
packaging = env["product.packaging"].create(
    {
        "name": "Thirteenpack",
        "barcode": "42 43",
        "product_id": product.id,
        "qty": 13,
    }
)
# packaging that should reuse UOM created for the one above
product = env.ref("product.product_delivery_02")
packaging = env["product.packaging"].create(
    {
        "name": "Thirteenpack",
        "barcode": "42 44",
        "product_id": product.id,
        "qty": 13,
    }
)
env.cr.commit()
