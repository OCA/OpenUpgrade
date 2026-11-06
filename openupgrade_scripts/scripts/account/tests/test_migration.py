from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestAccountMigration(TransactionCase):
    def test_sending_data(self):
        """
        Test that me migrate send_and_print_values correctly to sending_data
        """
        moves_with_sending_data = self.env["account.move"].search(
            [
                ("sending_data", "!=", False),
            ]
        )
        self.assertTrue(moves_with_sending_data)
        self.assertEqual(
            moves_with_sending_data[0].sending_data["author_user_id"],
            self.env.user.id,
        )
        self.assertEqual(
            moves_with_sending_data[0].sending_data["author_partner_id"],
            self.env.user.partner_id.id,
        )

    def test_payment_state_direct_to_bank(self):
        """Payments from a non reconcilable bank account are paid, whatever the
        reconciliation shape.
        """
        for name in ("s1", "s2", "s3", "s4a", "s4b"):
            payment = self.env.ref("openupgrade_test_account.ou_direct_%s" % name)
            self.assertEqual(
                payment.state,
                "paid",
                "ou_direct_%s should have migrated to 'paid'" % name,
            )

    def test_payment_state_outstanding_not_fully_paid(self):
        """Payments from an outstanding account stay in process while the
        invoices they are reconciled with are not paid.
        """
        for name in ("s1", "s2"):
            payment = self.env.ref("openupgrade_test_account.ou_outstanding_%s" % name)
            self.assertEqual(
                payment.state,
                "in_process",
                "ou_outstanding_%s should have stayed 'in_process'" % name,
            )

    def test_payment_state_outstanding_fully_paid(self):
        """Payments from an outstanding account are paid once all the invoices
        they are reconciled with are.
        """
        for name in ("s3", "s4a", "s4b"):
            payment = self.env.ref("openupgrade_test_account.ou_outstanding_%s" % name)
            self.assertEqual(
                payment.state,
                "paid",
                "ou_outstanding_%s should have been promoted to 'paid'" % name,
            )
