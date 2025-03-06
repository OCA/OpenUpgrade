from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestSaleMigration(TransactionCase):
    def test_sale_order_state(self):
        self.assertEqual(self.env.ref("sale.sale_order_18").state, "sale")
        self.assertTrue(self.env.ref("sale.sale_order_18").locked)
