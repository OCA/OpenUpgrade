env = locals().get("env")
for model in ("product.template", "product.product"):
    env["ir.default"].set(model, "type", "product")
env.cr.commit()
