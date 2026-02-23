from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestSaleMigration(TransactionCase):
    def test_res_company_downpayment_account_id(self):
        """
        Test that the migration set res.company#downpayment_account_id
        """
        self.assertTrue(self.env.company.downpayment_account_id)
