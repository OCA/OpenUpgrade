# © 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestPayment(TransactionCase):
    def test_payment(self):
        """Test that cancelled payments have the correct state"""
        self.assertEqual(
            self.env['account.payment'].search([
                ('communication', '=', 'openupgrade_draft_payment'),
            ]).state, 'draft')
        self.assertEqual(
            self.env['account.payment'].search([
                ('communication', '=', 'openupgrade_cancelled_payment'),
            ]).state, 'cancelled')
