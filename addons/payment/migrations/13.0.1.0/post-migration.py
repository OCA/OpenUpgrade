# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from psycopg2 import sql
from openupgradelib import openupgrade

unlink_by_xmlid = [
    'payment.payment_acquirer_custom'
]


def update_account_invoice_transaction_rel_table(cr):
    table = "openupgrade_legacy_13_0_ait_rel"
    openupgrade.logged_query(
        cr, sql.SQL(
            """INSERT INTO account_invoice_transaction_rel
            (transaction_id, invoice_id)
            SELECT transaction_id, am.id
            FROM {} rel
            JOIN account_move am ON am.old_invoice_id = rel.invoice_id"""
        ).format(sql.Identifier(table))
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_account_invoice_transaction_rel_table(env.cr)
    openupgrade.delete_records_safely_by_xml_id(env, unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'payment', 'migrations/13.0.1.0/noupdate_changes.xml')
