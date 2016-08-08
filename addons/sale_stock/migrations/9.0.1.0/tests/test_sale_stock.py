# coding: utf-8
from openerp.tests.common import TransactionCase


class TestSaleStock(TransactionCase):

    def test_sale_stock(self):
        """ Printer product was to be invoiced on delivery in 8.0 test data.
        Check that this product is now set to invoice on delivery, while the
        service product is not."""
        self.assertEqual(
            self.env.ref('product.product_product_37').invoice_policy,
            'delivery')
        self.assertNotEqual(
            self.env.ref('product.product_product_consultant').invoice_policy,
            'delivery')
