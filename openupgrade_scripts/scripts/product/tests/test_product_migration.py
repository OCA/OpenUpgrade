from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestProductMigration(TransactionCase):
    def test_product_uom(self):
        """
        Test that packages have been correctly migrated to uoms
        """
        product = self.env.ref("product.product_delivery_01")
        self.assertIn(
            self.env.ref("uom.product_uom_pack_6"), product.product_uom_ids.uom_id
        )
        new_uom = product.product_uom_ids.uom_id - self.env.ref(
            "uom.product_uom_pack_6"
        )
        self.assertEqual(new_uom.relative_uom_id, self.env.ref("uom.product_uom_unit"))
        self.assertEqual(new_uom.relative_factor, 13)
        self.assertEqual(
            self.env.ref("product.product_delivery_02").product_uom_ids.uom_id,
            new_uom,
        )
