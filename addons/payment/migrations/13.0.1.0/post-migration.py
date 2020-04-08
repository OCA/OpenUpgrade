# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

unlink_by_xmlid = [
    'payment.payment_acquirer_custom'
]


def map_payment_acquirer_state(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE payment_acquirer
        SET state = CASE WHEN {website_published} = TRUE THEN 'enabled'
            ELSE 'disabled' END
        WHERE state = 'prod'""".format(
            website_published=openupgrade.get_legacy_name('website_published')
        )
    )


def update_account_invoice_transaction_rel_table(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE account_invoice_transaction_rel aitr
        SET invoice_id = am.id
        FROM account_move am
        WHERE am.old_invoice_id = aitr.{}
        """.format(openupgrade.get_legacy_name('invoice_id'))
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    map_payment_acquirer_state(env.cr)
    update_account_invoice_transaction_rel_table(env.cr)
    openupgrade.delete_records_safely_by_xml_id(env, unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'payment', 'migrations/13.0.1.0/noupdate_changes.xml')
