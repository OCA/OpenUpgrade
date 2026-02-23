env = locals().get("env")

# create fiscal positions with tax mappings to test their migration

env["account.fiscal.position"].create(
    {
        "name": "Domestic fiscal position",
        "country_id": env.company.country_id.id,
    }
)

domestic_tax = env.ref("account.1_purchase_tax_template")
foreign_tax1 = domestic_tax.copy(
    {
        "name": "Foreign tax1",
    }
)

foreign_tax2 = domestic_tax.copy(
    {
        "name": "Foreign tax2",
    }
)


env["account.fiscal.position"].create(
    {
        "name": "Foreign fiscal position",
        "tax_ids": [
            (
                0,
                0,
                {
                    "tax_src_id": domestic_tax.id,
                    "tax_dest_id": foreign_tax1.id,
                },
            ),
            (
                0,
                0,
                {
                    "tax_src_id": domestic_tax.id,
                    "tax_dest_id": foreign_tax2.id,
                },
            ),
        ],
    }
)

# create a reconciliation with exchange move to check if exchange_move_id is moved
# from full reconcile record to new partial reconciliation

payable_account = env.ref("account.1_payable")
expense_account = env.ref("account.1_expense_rent")
eur = env.ref("base.EUR")

original_move = env["account.move"].create(
    {
        "ref": "Exchange move test move",
        "line_ids": [
            (
                0,
                0,
                {
                    "account_id": payable_account.id,
                    "credit": 42,
                    "currency_id": eur.id,
                    "amount_currency": 0,
                },
            ),
            (
                0,
                0,
                {
                    "account_id": expense_account.id,
                    "debit": 42,
                },
            ),
        ],
    }
)
original_move.action_post()

payment_move = env["account.move"].create(
    {
        "line_ids": [
            (
                0,
                0,
                {
                    "account_id": payable_account.id,
                    "debit": 40,
                    "currency_id": eur.id,
                    "amount_currency": 0,
                },
            ),
            (
                0,
                0,
                {
                    "account_id": expense_account.id,
                    "credit": 40,
                },
            ),
        ]
    }
)

payment_move.action_post()

(
    original_move.line_ids.filtered("account_id.reconcile")
    + payment_move.line_ids.filtered("account_id.reconcile")
).reconcile()

original_move.line_ids.full_reconcile_id.exchange_move_id.ref = (
    "Exchange move of test move's full reconciliation"
)

# create reconciliation models with partner mappings to test if they are migrated
# correctly
env["account.reconcile.model"].create(
    {
        "name": "Model with partner mapping, contains label matching",
        "match_label": "contains",
        "match_label_param": "hello world",
        "partner_mapping_line_ids": [
            (
                0,
                0,
                {
                    "partner_id": env.user.partner_id.id,
                    "payment_ref_regex": "hello",
                    "narration_regex": "world",
                },
            ),
        ],
    }
)
env["account.reconcile.model"].create(
    {
        "name": "Model with partner mapping, not_contains label matching",
        "match_label": "not_contains",
        "match_label_param": "hello world",
        "partner_mapping_line_ids": [
            (
                0,
                0,
                {
                    "partner_id": env.user.partner_id.id,
                    "payment_ref_regex": "hello",
                    "narration_regex": "world",
                },
            ),
        ],
    }
)
env["account.reconcile.model"].create(
    {
        "name": "Model with partner mapping, regex label matching",
        "match_label": "match_regex",
        "match_label_param": "hello world",
        "partner_mapping_line_ids": [
            (
                0,
                0,
                {
                    "partner_id": env.user.partner_id.id,
                    "payment_ref_regex": "hello",
                    "narration_regex": "world",
                },
            ),
        ],
    }
)


env.cr.commit()
