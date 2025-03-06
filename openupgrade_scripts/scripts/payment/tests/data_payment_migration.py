env = locals().get("env")
# create a payment token and a transaction to
# see if our migration migrates them correctly
demo_provider = env.ref("payment.payment_provider_demo")
demo_provider.state = "test"
token = env["payment.token"].create(
    {
        "provider_id": demo_provider.id,
        "partner_id": env.user.partner_id.id,
        "provider_ref": "hello world",
    }
)
env["payment.transaction"].create(
    {
        "provider_id": demo_provider.id,
        "token_id": token.id,
        "reference": "hello world",
        "amount": 42,
        "currency_id": demo_provider.main_currency_id.id,
        "state": "pending",
        "partner_id": env.user.partner_id.id,
    }
)
env.cr.commit()
