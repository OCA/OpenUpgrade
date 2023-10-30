from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "payment_transfer", "15.0.2.0/noupdate_changes.xml")
    # Delete the old form record and manually link the custom acquirers made by
    # the users.
    openupgrade.delete_records_safely_by_xml_id(env, ["payment_transfer.transfer_form"])
    custom_transfer = env["payment.acquirer"].search([("provider", "=", "transfer")])
    custom_transfer.redirect_form_view_id = env.ref("payment_transfer.redirect_form")
