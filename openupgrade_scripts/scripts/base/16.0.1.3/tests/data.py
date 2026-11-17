env = locals().get("env")
# set company_registry in v15 to be sure we migrate it correctly to v16
env.ref("base.main_company").company_registry = "424242"
# create the same bank account for the same partner in two companies: the new
# unique(sanitized_acc_number, partner_id) constraint does not allow it, so the
# pre-migration must keep only one record
company = env["res.company"].create({"name": "OpenUpgrade Test Company"})
partner = env["res.partner"].create(
    {"name": "OpenUpgrade Test Partner", "is_company": True}
)
bank = env["res.bank"].create({"name": "OpenUpgrade Test Bank"})
env["res.partner.bank"].create(
    [
        {
            "acc_number": "OPENUPGRADE TEST ACCOUNT",
            "partner_id": partner.id,
            "bank_id": bank.id,
            "company_id": env.ref("base.main_company").id,
        },
        {
            "acc_number": "OPENUPGRADE TEST ACCOUNT",
            "partner_id": partner.id,
            "bank_id": bank.id,
            "company_id": company.id,
        },
    ]
)
env.cr.commit()
