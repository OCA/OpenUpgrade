env = locals().get("env")
# decimeter
env["uom.uom"].create(
    {
        "name": "dm",
        "category_id": env.ref("uom.uom_categ_length").id,
        "factor": 10,
        "uom_type": "smaller",
    }
)
# megameter
env["uom.uom"].create(
    {
        "name": "Mm",
        "category_id": env.ref("uom.uom_categ_length").id,
        "factor": 1000000,
        "uom_type": "bigger",
    }
)
# entirely custom uom category
uom_category = env["uom.category"].create(
    {
        "name": "Electric current",
    }
)
env["uom.uom"].create(
    {
        "name": "A",
        "category_id": uom_category.id,
        "factor": 1,
        "uom_type": "reference",
    }
)
env["uom.uom"].create(
    {
        "name": "mA",
        "category_id": uom_category.id,
        "factor": 1000,
        "uom_type": "smaller",
    }
)
env["uom.uom"].create(
    {
        "name": "MA",
        "category_id": uom_category.id,
        "factor": 1000000,
        "uom_type": "bigger",
    }
)

env.cr.commit()
