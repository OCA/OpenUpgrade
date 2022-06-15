from openupgradelib import openupgrade


def _fill_account_analytic_line_category(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line aal
        SET category =
            CASE
                WHEN am.move_type IN ('out_invoice', 'out_refund', 'out_receipt')
                THEN 'invoice'
                WHEN am.move_type IN ('in_invoice', 'in_refund', 'in_receipt')
                THEN 'vendor_bill'
                ELSE 'other'
            END
        FROM account_move_line aml
        JOIN account_move am ON am.id = aml.move_id
        WHERE aml.id = aal.move_id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_account_analytic_line_category(env)
    openupgrade.load_data(env.cr, "account", "15.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "account",
        [
            "email_template_edi_invoice",
            "mail_template_data_payment_receipt",
        ],
    )
