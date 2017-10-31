# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import TransactionCase


class TestSale(TransactionCase):
    def test_sale(self):
        self.assertTrue(
            self.env.ref('sale.sale_order_2').order_line[0].currency_id ==
            self.env.ref('sale.sale_order_2').currency_id)
        self.assertEqual(
            self.env.ref('sale.sale_order_2').invoice_status,
            'no'
        )
        self.assertEqual(
            self.env.ref('sale.sale_order_2').order_line[0].invoice_status,
            'no'
        )
        self.assertEqual(
            self.env.ref('sale.sale_order_4').order_line[0].invoice_status,
            'invoiced'
        )
        self.assertEqual(
            self.env.ref('sale.sale_order_4').order_line[0].invoice_status,
            'invoiced'
        )
