from odoo.tests import TransactionCase, tagged

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestAccountMigration(TransactionCase):
    def test_account_payment_term_installation(self):
        """
        Test that the extra payment term we add triggers installation of
        account_payment_term
        """
        module = self.env["ir.module.module"].search(
            [("name", "=", "account_payment_term")]
        )
        self.assertEqual(module.state, "to install")


@openupgrade_test
@tagged("post_install")
class TestAccountMigrationPost(TransactionCase):
    def test_account_payment_term_migration(self):
        """
        Test that the extra payment term we add is migrated correctly
        """
        term = self.env["account.payment.term"].search(
            [
                ("name", "=", "Openupgrade test term"),
            ]
        )
        self.assertEqual(
            term.line_ids.days_next_month,
            "5",
        )
