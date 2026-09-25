env = locals().get("env")
# call sending wizard on some moves asynchronously
action = (
    env["account.move"]
    .search(
        [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("company_id", "=", env.ref("base.main_company").id),
        ]
    )
    .action_send_and_print()
)
env[action["res_model"]].with_context(**action["context"]).create(
    {
        "checkbox_download": False,
    }
).action_send_and_print()
env.cr.commit()

# Payments for the state fix in post-migration, in the four reconciliation
# shapes: once on a journal paying from a plain bank account, once on a journal
# paying from a reconcilable outstanding account.
company = env.ref("base.main_company")

recv = env["account.account"].search(
    [("account_type", "=", "asset_receivable"), ("company_id", "=", company.id)],
    limit=1,
)
income = env["account.account"].search(
    [("account_type", "=", "income"), ("company_id", "=", company.id)], limit=1
)

bank_acc = env["account.account"].create(
    {
        "name": "OU test direct bank",
        "code": "OUDIR",
        "account_type": "asset_cash",
        "reconcile": False,
        "company_id": company.id,
    }
)
outstanding_acc = env["account.account"].create(
    {
        "name": "OU test outstanding",
        "code": "OUOUT",
        "account_type": "asset_current",
        "reconcile": True,
        "company_id": company.id,
    }
)
outstanding_bank_acc = env["account.account"].create(
    {
        "name": "OU test outstanding bank",
        "code": "OUOBK",
        "account_type": "asset_cash",
        "reconcile": False,
        "company_id": company.id,
    }
)

direct_journal = env["account.journal"].create(
    {
        "name": "OU test direct bank",
        "code": "OUDBK",
        "type": "bank",
        "company_id": company.id,
        "default_account_id": bank_acc.id,
    }
)
# liquidity posts straight to the (non-reconcilable) bank account
direct_journal.inbound_payment_method_line_ids.payment_account_id = bank_acc.id
direct_journal.outbound_payment_method_line_ids.payment_account_id = bank_acc.id

outstanding_journal = env["account.journal"].create(
    {
        "name": "OU test outstanding bank",
        "code": "OUOBK",
        "type": "bank",
        "company_id": company.id,
        "default_account_id": outstanding_bank_acc.id,
    }
)
# liquidity posts to the reconcilable outstanding account
outstanding_journal.inbound_payment_method_line_ids.payment_account_id = (
    outstanding_acc.id
)
outstanding_journal.outbound_payment_method_line_ids.payment_account_id = (
    outstanding_acc.id
)

sale_journal = env["account.journal"].search(
    [("type", "=", "sale"), ("company_id", "=", company.id)], limit=1
)
ou_partner = env["res.partner"].create(
    {
        "name": "OU test payment partner",
        "property_account_receivable_id": recv.id,
    }
)


def _ou_invoice(amount):
    inv = env["account.move"].create(
        {
            "move_type": "out_invoice",
            "partner_id": ou_partner.id,
            "journal_id": sale_journal.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "ou test",
                        "quantity": 1,
                        "price_unit": amount,
                        "account_id": income.id,
                        "tax_ids": [(6, 0, [])],
                    },
                )
            ],
        }
    )
    inv.action_post()
    return inv


def _ou_pay(invoices, journal, amount):
    wizard = (
        env["account.payment.register"]
        .with_context(
            active_model="account.move",
            active_ids=invoices.ids,
        )
        .create({"journal_id": journal.id})
    )
    if len(invoices) > 1:
        wizard.group_payment = True
    wizard.amount = amount
    return wizard._create_payments()


def _ou_build(prefix, journal):
    # 1) partial payment of one invoice
    p1 = _ou_pay(_ou_invoice(1000), journal, 400)
    # 2) one payment paying multiple invoices partially
    p2 = _ou_pay(_ou_invoice(1000) | _ou_invoice(1000), journal, 800)
    # 3) a payment paying an invoice fully
    p3 = _ou_pay(_ou_invoice(1000), journal, 1000)
    # 4) two payments paying one invoice fully
    inv = _ou_invoice(1000)
    p4a = _ou_pay(inv, journal, 600)
    p4b = _ou_pay(inv, journal, 400)
    env["ir.model.data"]._update_xmlids(
        [
            {"xml_id": "openupgrade_test_account.%s_s1" % prefix, "record": p1},
            {"xml_id": "openupgrade_test_account.%s_s2" % prefix, "record": p2},
            {"xml_id": "openupgrade_test_account.%s_s3" % prefix, "record": p3},
            {"xml_id": "openupgrade_test_account.%s_s4a" % prefix, "record": p4a},
            {"xml_id": "openupgrade_test_account.%s_s4b" % prefix, "record": p4b},
        ]
    )


_ou_build("ou_direct", direct_journal)
_ou_build("ou_outstanding", outstanding_journal)
env.cr.commit()
