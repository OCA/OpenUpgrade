from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestPaymentMigration(TransactionCase):
    def test_no_transactions_without_method(self):
        payment_transactions = self.env["payment.transaction"].search([])
        self.assertTrue(payment_transactions)
        self.assertFalse(
            payment_transactions.filtered_domain([("payment_method_id", "=", False)])
        )
