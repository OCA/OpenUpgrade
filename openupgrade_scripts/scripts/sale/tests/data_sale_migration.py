env = locals().get("env")

# set a default downpayment account for company 1
env["ir.default"].set(
    "product.category",
    "property_account_downpayment_categ_id",
    env.ref("account.1_payable").id,
    company_id=env.company.id,
)

env.cr.commit()
