# coding: utf-8
# Copyright 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestPurchaseRequisition(TransactionCase):
    def test_purchase_requisition(self):
        """ Product setting was migrated properly """
        self.assertEqual(
            self.env.ref('product.product_product_13').purchase_requisition,
            'tenders')
        self.assertEqual(
            self.env.ref('product.product_product_48').purchase_requisition,
            'rfq')
