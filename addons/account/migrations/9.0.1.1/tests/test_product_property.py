# coding: utf-8
from openerp.tests.common import TransactionCase


class TestProductProperty(TransactionCase):
    def test_product_property(self):
        """ Product expense property is migrated successfully """
        product = self.env.ref('product.product_product_43')
        account = self.env.ref('account.cog')
        self.assertEqual(product.property_account_expense_id, account)
