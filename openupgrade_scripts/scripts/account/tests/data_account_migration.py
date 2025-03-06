env = locals().get("env")
# create payment term that triggers installation of account_payment_term
env["account.payment.term"].create(
    {
        "name": "Openupgrade test term",
        "line_ids": [
            (
                0,
                0,
                {
                    "value": "balance",
                    "days": 10,
                    "end_month": True,
                    "days_after": 5,
                },
            ),
        ],
    }
)
env.cr.commit()
